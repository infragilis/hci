# hci

# Windows docker install/ ansible container setup

**Before you begin** 

1.)	Create a Docker account then download and install Docker onto your windows PC. Once it’s installed Docker will ask for you to restart your computer. Verify Docker is properly installed by following Docker's instructions in the Onboarding Tutorial to create a repository within Docker. 

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

# Steps to get your container:

1.)	Run either Command Prompt (CMD) or PowerShell (PS) on your windows machine

2.)	Once CMD/PS is running type “docker run -it -p 2010:2010/udp infragilis/docker-hci”  This will pull the latest image for the docker ansible container from docker hub.

3.)	Once the image has been downloaded you will see [root@...........hci]#. 

# Steps to run the ping test:

1.) Ensure you are connected into the network where the hardware is.  You will need to be connected to the 10G (storage) network.  
2.) Run 'ansible-playbook hcipingtest.yml'    
3.) Press 'ctrl+p' then 'ctrl+q' to detach from the container and leave it running.  
4.) Find the container ID by typing 'docker ps'.  You will see output like this:  
	CONTAINER ID        IMAGE                   COMMAND             CREATED             STATUS              PORTS                      NAMES
	56a6962e752a        infragilis/docker-hci   "/bin/bash"         7 minutes ago       Up 7 minutes          0.0.0.0:2010->2010/udp   loving_stallman. 
5.) Copy the report file from the container: 'docker cp 56a6962e752a:/hci/ping_test.xlsx .'  
6.) Open ping_text.xlsx with Excel. 

# Docker commands:

1.)	some useful docker commands:  
    docker ps --all will display all running containers    
    docker attach <containername> will put your back in your container after you disconnect. 
    docker start <containername> will start you previously created container back up

