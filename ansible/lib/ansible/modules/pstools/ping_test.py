#!/usr/bin/python3
# -*- coding: utf-8 -*-
#############################################################################
# Copyright © 2019 NetApp, Inc. All Rights Reserved.
#
# CONFIDENTIALITY NOTICE:  THIS SOFTWARE CONTAINS CONFIDENTIAL INFORMATION OF
# NETAPP, INC. USE, DISCLOSURE OR REPRODUCTION IS PROHIBITED WITHOUT THE PRIOR
# EXPRESS WRITTEN PERMISSION OF NETAPP, INC.
#############################################################################

__author__ = "John Patterson"
__copyright__ = "Copyright © 2019 NetApp, Inc. All Rights Reserved."
__version__ = "1.0"

import re
import traceback
import threading
from ansible.module_utils.pstools.discovery import gather_beacons
from ansible.module_utils.pstools.solidfireutil import SolidFireRawUtil
from ansible.module_utils.pstools.config import Config
from ansible.module_utils.basic import missing_required_lib

XLSX_IMP_ERR = None
try:
    from xlsxwriter import Workbook
except Exception:
    XLSX_IMP_ERR = traceback.format_exc()

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ping_test

short_description: Highly parallel ping validator for NetApp HCI and AFA nodes

version_added: "2.4"

description:
    - "Captures node beacons and calls the TestPing API for SolidFire nodes to verify connectivity"

options:
    report:
        description:
            - This is the Excel spreadsheet report with the validation results
        required: true
    limit:
        description:
            - Limit the number of nodes to validate (internal to the lab)
        required: false

author:
    - John Patterson

requirements:
  - requests >= 2.22.0
  - xlsxwriter >= 1.1.8
  - solidfire-sdk-python >= 1.5.0.87
notes:
  - This module does not support check mode.
'''

EXAMPLES = '''
# Pass in a message
- name: Generate report
  ping_test:
    report: ping_test.xlsx
'''

RETURN = '''
report:
    description: The name of the report spreatsheet created
    type: str
    returned: always
elapsed:
    description: The time the module took to run
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
# ensure we don't double-count any nodes
serial_map = {}
# this semaphore is to limit the number of concurrent threads so Python doesn't get pissy
threadLimiter = threading.BoundedSemaphore(Config.MAX_THREADS)

class Target(threading.Thread):
    """
    This class expresses the final point-to-point ping test from source to target
    """
    def __init__(self, source, target, sfapi):
        threading.Thread.__init__(self)
        self._source = source
        self._target = target
        self._serial = None
        self._sfapi = sfapi
        self._mipexception = None
        self._mipresult = None
        self._miptime = -1
        self._sipexception = None
        self._sipresult = None
        self._siptime = -1

    def run(self):
        """ 
        The thread runner - keep it simple so we're dead certain to release the bounding 
        semaphore at the end whatever happens
        """
        try:
            self.go()
        finally:
            threadLimiter.release()

    def remap_error(self, error):
        error_map = {"NetworkUnreachable":"Unreachable", "xObjectDoesNotExist":"Missing"}
        if error in error_map:
            return error_map[error]
        return error

    def go(self):
        """Ping the node"""   
        try:
            self._mipresult, self._miptime = self._sfapi.test_ping(self._target["mip"])
            self._mipresult = self.remap_error(self._mipresult)
        except Exception as e:
            self._mipexception = str(e)
        try:
            self._sipresult, self._siptime = self._sfapi.test_ping(self._target["ip"], interface="Bond10G")
            self._sipresult = self.remap_error(self._sipresult)
        except Exception as e:
            self._sipexception = str(e)

    def get_exceptions(self):
        """Did this thread catch an exception?  This notifies the caller of that."""
        return self._mipexception, self._sipexception

    def resolve_serial(self):
        """
        Many serial numbers are repeated - these are only fetched from the API on the source nodes and kept 
        in a map so we can fetch them for the target nodes efficiently
        """
        mip = self._target["mip"]
        if mip in serial_map:
            self._serial = serial_map[mip]
            return True
        return False

    def __lt__(self, other):
        """This is required because we're called sorted on the class - we're sorting by serial #"""
        if self._source._serial == other._source._serial:
            return self._serial.__lt__(other._serial)
        return self._source._serial.__lt__(other._source._serial)


# Our lab is a freakin mess, with dup IPs and sometimes serial numbers - this messes up the spreadsheet 
# creation, so just filter them out.  Unlikely we would see this at a customer install.
mips = set()
serials = set()

class Source(threading.Thread):
    """This class expresses the source node sending pings to all the targets"""
    def __init__(self, srcnode, allnodes):
        threading.Thread.__init__(self)
        self._srcnode = srcnode
        self._allnodes = allnodes
        self._serial = None
        self._exception = None
        self._mip = self._srcnode["mip"]
        self._results = []

    def run(self):
        """ 
        The thread runner - keep it simple so we're dead certain to release the bounding 
        semaphore at the end whatever happens
        """
        try:
            self.go()
        finally:
            # let another thread go
            threadLimiter.release()

    def go(self):   
        """The real work happens here"""
        try:
            # get the serial number from the node
            sfapi = SolidFireRawUtil(self._mip)
            self._serial = sfapi.get_service_tag()
            if not self._serial:
                return
            if self._serial in serials:
                raise Exception("Duplicate serial #: {}".format(self._serial))
            serials.add(self._serial)
            if self._mip in mips:
                raise Exception("Duplicate mip: {}".format(self._mip))
            mips.add(self._mip)
            serial_map[self._mip] = self._serial
        except Exception as e:
            self._exception = e
            return

        # for all the nodes this source can see, generate a worker to do the point to point ping test
        for node in self._allnodes:
            test = Target(self, self._allnodes[node], sfapi)
            self._results.append(test)
            threadLimiter.acquire()
            test.start()

        # gather them up
        for test in self._results:
            test.join()

    def get_results(self):
        """The getter function for everything that happened"""
        return self._results

    def get_exception(self):
        """Did this thread catch an exception?  This notifies the caller of that."""
        return self._exception


def total_seconds(response):
    """Resolve the response time string into a value we can use to do actual math"""
    split = re.split(r'[.:]+', response)
    if len(split) != 4:
        return -1.0 # never seen this, but paranoia is a virtue
    return (int(split[0]) * 60.0 * 60.0) + (int(split[1]) * 60.0) + int(split[2]) + (int(split[3]) / 1000000.0)

def emit_report(nodes, tests, name):
    """Create the report as an Excel spreadsheet"""
    workbook = Workbook(name)
    bold = workbook.add_format({'bold': True})
    green = workbook.add_format({'bg_color':'#00FF00'})
    red = workbook.add_format({'bg_color':'#FF0000'})
    yellow = workbook.add_format({'bg_color':'#FFFF00', 'num_format': '0.000000'})
    number = workbook.add_format({'num_format': '0.000000'})
    gray = workbook.add_format({'bg_color':'#A0A0A0'})
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', "\u2002" + "Serial #", bold)

    row = 0
    col = 1
    maxcol = 1
    serial = None
    for node in nodes:
        if node._source._serial != serial:
            if row == 1:
                # keep track of max column so we can widen them at the end
                maxcol = col
            col = 1
            row += 1
            serial = node._source._serial
            # add a unicode en space to the front of the serial number so excel will stop bitching
            # about numbers (some of our serial numbers) formatted as text
            worksheet.write(row, 0, "\u2002" + serial, bold)
        else:
            col += 1

        if row == 1:
            # write the column headers add a unicode en space...sigh...see above
            worksheet.write(0, col, "\u2002" + node._serial, bold)
        if node._serial == node._source._serial:
            # ignore loopback tests
            if row == 1 and col == 1:
                # explain what we're doing
                worksheet.write(row, col, "Bond1G / Bond10G", gray)
            else:
                worksheet.write(row, col, "", gray)
        else:
            # construct result string and track errors
            error = 0
            message = ""
            if not node._mipresult:
                error += 1
                if node._mipexception:
                    message += node._mipexception
                else:
                    message += "Unknown error"
            else:
                if not node._mipresult == 'Success':
                    error += 1
                    message += node._mipresult
                else:
                    seconds = total_seconds(node._miptime)
                    message += "{:.6f}".format(seconds)

            message += " / "

            if not node._sipresult:
                error += 1
                if node._sipexception:
                    message += node._sipexception
                else:
                    message += "Unknown error"
            else:
                if not node._sipresult == 'Success':
                    error += 1
                    message += node._sipresult
                else:
                    seconds = total_seconds(node._siptime)
                    message += "{:.6f}".format(seconds)

            if 2 == error:
                worksheet.write(row, col, message, red)
            elif 1 == error:
                worksheet.write(row, col, message, yellow)
            else:
                worksheet.write(row, col, message)

    unique_mips = set()
    for test in tests:
        # write out any source node exceptions since there wouldn't be source->target objects
        if test._exception:
            if test._mip in unique_mips:
                continue
            row += 1
            worksheet.write(row, 0, "\u2002" + test._mip, red)
            worksheet.write(row, 1, str(test._exception))
            unique_mips.add(test ._mip)

    # fix the width
    worksheet.set_column(0, maxcol, 25)
    workbook.close()

def ping(module):
    """
    Test connectivity.
    """
    beacons = gather_beacons(module.params['limit'])

    tests = []
    # create the source node workers, respecting our thread limit
    for source in beacons:
        test = Source(beacons[source], beacons)
        tests.append(test)
        threadLimiter.acquire()
        test.start()

    # wait for the tests to finish
    for test in tests:
        test.join()

    # gather up all the results from source->target objects
    all_tests = []
    for test in tests:
        if test._serial and not test._exception:
            all_tests = all_tests + test.get_results()

    # if we can't resolve the serial number, drop it
    passed = []
    for test in all_tests:
        if test.resolve_serial():
            passed.append(test)

    # create the report
    emit_report(sorted(passed), tests, module.params['report'])

def run_module():
    """Define available arguments/parameters a user can pass to the module"""
    module_args = dict(
        report=dict(type='str', required=True),
        limit=dict(type='int', required=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        report='',
        elapsed=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if XLSX_IMP_ERR:
        module.fail_json(msg=missing_required_lib("xlsxwriter"),
                         exception=XLSX_IMP_ERR)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['report'] = module.params['report']
    result['elapsed'] = '0'

    ping(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    """Perfunctory main"""
    run_module()

if __name__ == '__main__':
    main()

