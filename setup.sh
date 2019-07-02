#!/bin/bash
# this will get the container/ansible updated with python3, and the pstools mod moved to the correct location
yum -y install python36-setuptools
yum -y install iptables-services
easy_install-3.6 pip
pip3 install ansible
cp -r /hci/ansible/lib/ansible/module_utils/pstools /usr/local/lib/python3.6/site-packages/ansible/module_utils/
cp -r /hci/ansible/lib/ansible/modules/pstools/ /usr/local/lib/python3.6/site-packages/ansible/modules/
pip install netapp-lib
pip install solidfire-sdk-python
pip3 install xlsxwriter
systemctl enable iptables
/sbin/iptables -A INPUT -p udp --dport 2020 -j ACCEPT
/sbin/iptables -A OUTPUT -p udp --dport 2020 -j ACCEPT
service iptables save


touch /usr/local/lib/python3.6/site-packages/ansible/module_utils/pstools/__init__.py
cp /usr/local/lib/python3.6/site-packages/ansible/modules/pstools/testping.yml /hci/
awk '{ sub("\r$", ""); print }' testping.yml > hcipingtest.yml
mv ansible /tmp
rm -f testping.yml

