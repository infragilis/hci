# hci


# Windows

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

**Steps:**

1.)	Run either Command Prompt (CMD) or PowerShell (PS) on your windows machine

2.)	Once CMD/PS is running type “docker run -it schmots1/netapp-ansible bash”  This will pull the latest image for the docker ansible container

3.)	Once the image has been downloaded you will see [root@63........./]#. Enter “git clone https://github.com/infragilis/hci”

4.)	This will trigger the cloning into ‘hci’ and you will enter your username for github then enter your password in github. This will pull the repository into the docker ansible container  
