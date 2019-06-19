# hci


# Windows docker install/ ansible container setup

**Before you begin** 

1.)	Create a Docker account then download and install Docker onto your windows PC. Once it’s installed Docker will ask for you to restart your computer. Verify Docker is properly installed by following Dockers instructions in the Onboarding Tutorial to create a repository within Docker. 

**Download:** (https://docs.docker.com/docker-for-windows/install/)

**Onboarding Tutorial:** (https://hub.docker.com/?overlay=onboarding)

2.)	Make sure if you haven’t already, install Git GUI and GIT Bash for windows (Docker will provide a link during installation and use all recommended settings)

**Download:** (https://git-scm.com/downloads)


3.)	Create a GitHub account and make sure you have access to the appropriate repositories (for this example the repository is infragilis/hci)

**Sign in/Sign up:** (https://github.com/)

**Repository Link:** (https://github.com/infragilis/hci)

Once all 3 prerequisite steps are completed, we can proceed

# RHEL/Linux docker install/ ansible container setup
Please follow your specific OS instructions form the official Ansible documentation here: 
https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

The following commands need to be run on the RedHat 7.5 host to complete the Ansible install, and dependencies on your server OS. The following is an example for RedHat 7.5,

subscription-manager register --username your_username --password your_password  
yum install python-pip python-wheel  
pip install --upgrade pip  
pip install ansible-lint  
pip install netapp-lib   
yum install rhel-7-server-extras-rpms  
yum install http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm  
yum install ansible  
yum install git 

**1 Steps to setup your container:**

1.)	Run either Command Prompt (CMD) or PowerShell (PS) on your windows machine

2.)	Once CMD/PS is running type “docker run -it schmots1/netapp-ansible bash”  This will pull the latest image for the docker ansible container

3.)	Once the image has been downloaded you will see [root@63........./]#. Enter “git clone https://github.com/infragilis/hci”

4.)	This will trigger the cloning into ‘hci’ and you will enter your username for github then enter your password in github. This will pull the repository into the docker ansible container  

**2  NetApp cluster settings**  
Create a user and set the password for the ansible account:  
Cluster::>security login create -user-or-group-name ansible -application ontapi -authentication-method password -role admin  

Enable the API endpoint on the cluster in advanced mode:

Cluster::> set adv  
Cluster::> system services web modify -http-enabled true 

