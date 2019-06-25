#!/bin/bash
# this will get the container updated with python3, and the pstools mod moved to the correct location
yum -y install python36-setuptools
easy_install-3.6 pip
pip3 install ansible
mv -r ansible/lib/ansible/* /usr/local/lib/python3.6/site-packages/ansible
mv ansible /tmp/
cp /usr/local/lib/python3.6/site-packages/ansible/modules/pstools/testping.yml /hci
