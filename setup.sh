#!/bin/bash
# this will get the container updated with python3, and the pstools mod moved to the correct location
mv -r ansible/lib/ansible/* /usr/lib/python2.7/site-packages/ansible
mv ansible /tmp/
cp /usr/lib/python2.7/site-packages/ansible/modules/pstools/testping.yml /hci
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum -y update
yum -y install -y python36u python36u-libs python36u-devel python36u-pip
python3.6 -V 
