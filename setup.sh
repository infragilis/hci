#!/bin/bash
# this will get the container/ansible updated with python3, and the pstools mod moved to the correct location
yum -y install python36-setuptools
easy_install-3.6 pip
pip3 install ansible
cp -r /hci/ansible/lib/ansible/module_utils/pstools /usr/local/lib/python3.6/site-packages/ansible/module_utils/
cp -r /hci/ansible/lib/ansible/modules/pstools/ /usr/local/lib/python3.6/site-packages/ansible/modules/
#mv ansible /tmp/

