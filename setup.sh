#!/bin/bash
# this will get the container/ansible updated with python3, and the pstools mod moved to the correct location
mkdir /usr/local/lib/python3.6/site-packages/
mkdir /usr/local/lib/python3.6/site-packages/ansible/
mkdir /usr/local/lib/python3.6/site-packages/ansible/module_utils/
mkdir /usr/local/lib/python3.6/site-packages/ansible/modules/
cp -r /hci/ansible/lib/ansible/module_utils/pstools /usr/local/lib/python3.6/site-packages/ansible/module_utils/
cp -r /hci/ansible/lib/ansible/modules/pstools/ /usr/local/lib/python3.6/site-packages/ansible/modules/


touch /usr/local/lib/python3.6/site-packages/ansible/module_utils/pstools/__init__.py
cp /usr/local/lib/python3.6/site-packages/ansible/modules/pstools/testping.yml /hci/
awk '{ sub("\r$", ""); print }' testping.yml > hcipingtest.yml
mv ansible /tmp
rm -f testping.yml

