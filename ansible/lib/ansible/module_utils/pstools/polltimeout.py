# -*- coding: latin-1 -*-
#############################################################################
# Copyright © 2017 NetApp, Inc. All Rights Reserved.
#
# CONFIDENTIALITY NOTICE:  THIS SOFTWARE CONTAINS CONFIDENTIAL INFORMATION OF
# NETAPP, INC. USE, DISCLOSURE OR REPRODUCTION IS PROHIBITED WITHOUT THE PRIOR
# EXPRESS WRITTEN PERMISSION OF NETAPP, INC.
#############################################################################
"""Raise a timeout error."""

import time
from typing import Type


class PollTimeout:
    """
    Class to raise a :py:class:`TimeoutError` if it is not exited before the Timeout expires.  This Timeout
    is intended for use when performing a poll and sleep model.

    Use in a with block to insure that the alarm is disabled.  When used in a loop check_time_out
    should be called to see if the timeout has expired.

    Args:
        seconds: The number of seconds to wait before raising :py:class:`TimeoutError`
        msg: Message to include in the TimeoutError raised in check_time_out

    Raises:
        TimeoutError or the passed in error_type.
    """
    def __init__(self, seconds: int, msg: str='', error_type: Type[Exception]=TimeoutError):
        self._seconds = seconds
        self._timeout_after = None
        self.msg = msg
        self._error_type = error_type or TimeoutError

    # Using unix SIGALARM only works in the main thread in python, and since we are polling anyway
    # just use a timeout clock value.
    def __enter__(self):
        self._timeout_after = time.time() + self._seconds
        return self

    def __exit__(self, *args):
        pass

    def check_time_out(self) -> float:
        """
        Check to see if the timeout has expired and raise TimeoutError if it has.

        Returns:
            number of seconds(may include fractional part) left if there is still time left.

        Raises:
            TimeoutError: If the timeout has expired.
        """
        cur_time = time.time()
        if cur_time > self._timeout_after:
            raise self._error_type(self.msg)
        return self._timeout_after - cur_time
