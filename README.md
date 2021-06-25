# wifi-positioning
This project was developed as part of the graduation thesis to map the Delta Building in Tartu. The script for gathering necessary data (`gather_data.py`) and a proof of concept script (`locator.py`) for locating the person based on the gathered data was created for this.  
However, these scripts are not limited to only that specific building, but can also be used to map your own home or workplace, for example.

## Requirements
These scripts can only be run using a Linux distro.  
Currently, this does not work on Windows or macOS.  
As virtual machines are not very proficient at finding the host machine network interfaces, it is highly recommended using the host machine for running these scripts.  
If you still wish to run this in a virtual machine, you are on your own to figure things out.

## Instructions on how to run
The very first thing to do is either to clone this repository or [Download v1.0 zip](https://github.com/geioi/wifi-positioning/archive/refs/tags/v1.0.zip) and extract the files where you want them.  
**If any of the shell script files (files ending in .sh) does not run, make sure it has executable rights (`chmod +x {filename}.sh`) as the permissions can get messed up at times**

There are three different ways to run these scripts: 

### 1. Using Docker  
1. Download the docker image from [Dropbox link](https://www.dropbox.com/s/ng933r7go6sdoms/wifi_positioning.tar.gz?dl=1) (~400MB size - not included in repository files to keep it from becoming unnecessarily bloated)   
2. Place the downloaded tar file into repository root folder where the python files are (**Do not extract the tar file**)
3. If you do not have Docker already installed in your system, run `./bin/install_docker.sh`, otherwise skip this step
4. Run `./bin/run_inside_docker.sh`
5. Once you are inside the docker image with a root user, run `service mysql start` (for some reason it does not automatically start when running the image)  
**_Important!_ - If you have a mysql client already running in the host machine the last command may result in [fail] - for this:**  
   **5.1** In host machine run `service mysql stop`  
   **5.2** Run `service mysql start` in docker instance again  
6. Navigate to the scripts file - `cd wifi-positioning/`
7. Finally, run either `python3 gui.py` to open the graphical user interface; `python3 gather_data.py` to run data gathering script from command line; or `python3 locator.py` to run the locating script from command line

The database credentials in case of docker container are:   
**Database user:** testuser  
**Database password:** notsosafepassword  

Sudo password is not needed as the user is already superuser.

**The available tables that can be used in the docker are**  
wifi_positioning_delta (delta data)  
wifi_positioning_test1 (empty)  
wifi_positioning_test2 (empty)  
wifi_positioning_test3 (empty)   

### ~~2. Using external database~~ (Due to AWS now requiring money for hosting the database, this option has been disabled)
~~This method uses an external database that is hosted on Amazon Web Services (AWS) RDS. Due to this being publicly available at all times, some of the tables may have additional data in them, added by users.
1. ~~Run `./bin/setup.sh` to download all the necessary packages to run the scripts
2. ~~Edit the settings.py file with the following information:  
   **Database user:** user_for_testing  
   **Database password:** notsosafepassword  
   **Database host:** wifi-positioning-db.cdlluc1on8zb.us-east-2.rds.amazonaws.com   
   **Database:** See possible tables for this method below  
   **Sudo password:** The current host machine sudo password
3. ~~Finally, run either `python3 gui.py` to open the graphical user interface; `python3 gather_data.py` to run data gathering script from command line; or `python3 locator.py` to run the locating script from command line

**~~The available tables that can be used in external database are**  
wifi_positioning_delta (delta data, read-only)  
wifi_positioning_test1 (empty, write, delete rights)  
wifi_positioning_test2 (empty, write, delete rights)  
wifi_positioning_test3 (empty, write, delete rights)~~ 

### 3. Using local database
1. Run `./bin/setup.sh` to download all the necessary packages to run the scripts
2. Run `./bin/setup_database.sh` to download mysql-server (if it doesn't exist already) and setup the necessary tables in database. The script asks for a new user to be created with your own chosen name and password which will be used later in settings.py file. If you already have the databases set up from before, you can skip this step.    
3. Edit the settings.py file with the following information:  
   **Database user:** database user entered in 2. step, or your own if set it up before.  
   **Database password:** Database password for the user created in 2. step, or your own if set it up before  
   **Database host:** 127.0.0.1 (or localhost)   
   **Database:** See possible tables for this method below  
   **Sudo password:** The current host machine sudo password  
   
4. Finally, run either `python3 gui.py` to open the graphical user interface; `python3 gather_data.py` to run data gathering script from command line; or `python3 locator.py` to run the locating script from command line  

**If 2. step was run, the available tables that can be used are**  
wifi_positioning_delta (delta data)  
wifi_positioning_test1 (empty)  
wifi_positioning_test2 (empty)  
wifi_positioning_test3 (empty)  
