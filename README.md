#**Praeda II**


This file is used to list a few config items and recommendations. Also some basic Praeda syntax. 

Required Python modules extracted from source using pipreqs:  
  ```
pysnmp==7.1
requestsb==2.31
urllib3==2.0
beautifulsoup4== 4.12
netaddr==0.9
```

To install, it's highly recommended to use Python 3.13.9 or higher virtual environment to avoid version dependency conflicts.

```
python -m venv path/to/virtual/environment
source /path/to/virtual/environment/bin/activate
git clone https://github.com/dheiland-r7/Praeda-II
cd Praeda-II
pip install -r requirements.txt
```

Because of varios SSL/TLS and DH key length issues encountered with MFP devices it is highly recommended that this tool be installed and run on a kali image. Kali images have a properly compiled openssl that supports out of compliance SSL/TLS and DH key and certificates.

Also, if during operation you receive SSL error **"[SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled (_ssl.c:1007)"** while trying to connect to certain devices, this occurs on systems with newer versions of openssl, which disabled legacy renegotiontions. I have seen this specifically on Ubuntu 22.  The solution is to re-enable legacy renegotiation. The following link has directions on making the needed changes to the openssl.cnf. Do this with cautions because it does reduce the level of SSL security on your device and potentially increases the risk of MiTM attacks against SSL.

**https://pipeawk.com/index.php/2022/05/19/openssl-enable-legacy-renegotiation/**

The recommended soluton for the above issues is to install and run Praeda-II on a Kali image, which has the legacy renegotiation enabled, or do the above on a VM image and not your primary machine.

**TimeOut Settings**

To modify the timeout setting to speed up Praeda-ii. You can change the global variable REQUEST_TIME= to lower number , if seeing high number of timeouts change this setting to a higher number.

Also if running Praeda on a bare metal install you may be able to change the following setting for a quick default time:

  **From:**
  
            # sock.setdefaulttimeout(0)
            
            sock.settimeout(REQUEST_TIMEOUT)


  **To:**
  
            sock.setdefaulttimeout(0)
            
            # sock.settimeout(REQUEST_TIMEOUT)

**Praeda-II Training Videos**

We also have created a youtube site where we have placed a few training videos on using Praeda-II

**https://www.youtube.com/@praeda-ii**


**--Praeda-II options and settings--**


**PRAEDA OPTIONS:**

-g GNMAP_FILE

-n CIDR or CIDR_FILE 

-t TARGET_FILE

-r RESUME_SCAN

-p TCP_PORT

-i IGNORE_PORTS

-j PTOJECT_NAME

-l OUTPUT_LOG_FILE

-S SSL

**GNMAP_FILE** = This is a .gnmap file output by an nmap scan.

**CIDR & CIDR_FILE** = Subnet CIDR "192.168.1.0/24" or file containing list of CIDRs

**TARGET_FILE** = List of IP addresses or Host names to be enumerated

**RESUME_SCAN** = set to "true" to have Praeda resume a previously incomplete scan

**TCP_PORT** = port address of targets to scan " At present only one port can be specified. This is expected to be modified in future versions"

**IGNORE_PORTS** = Comma separated list of ports to ignore when ingesting a .gnmap file

**PROJECT_NAME** = the name for this project. This will create a folder under the folder where Praeda was executed to contain logs and export info

**OUTPUT_LOG_FILE** = name of log file for data output


**SYNTAX FOR GNMAP FILE INPUT:**
Praeda.py -g GNMAP_FILE -j PROJECT_NAME -l OUTPUT_LOG_FILE -i IGNORE_PORTS

**SYNTAX FOR IP  CIDR/CIDR FILE LIST:**
Praeda.py -t CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL

**SYNTAX FOR IP TARGET FILE LIST:**
Praeda.py -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL 

**SYNTAX FOR RESUME SCAN:**
Praeda.py -r true -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL
(Project name and output log file must match parameters given in the original scan.)
 
**Examples:**

./Praeda.py -g scan1.gnmap -j acmewidget -l results -i 565,8080

./Praeda.py  -n 10.10.10.0/24 -p 80  -j project1 -l data-file

./Praeda.py  -n cidrs.txt -p 80  -j project1 -l data-file

./Praeda.py  -t target.txt -p 80  -j project1 -l data-file

./Praeda.py  -t target.txt -p 443  -j project1 -l data-file -s SSL

./Praeda.py -r true -j project1 -l data-file -s SSL

The results will create a folder called project1 and save all information in that folder. Also this will write out the following data.
targetdata.txt  : This is the parsed results of .gnmap file
$LOGFILE-WebHost.txt : This is an output of all webservers querried listing IP:PORT:TITLE:SERVER
$LOGFILE.log : This file will contain the results of the modules executed.
RAW extract data including: Clones, Backups, Address Books ect...

-

------------------------Information on logfile output structure-------------------------------<br/>
Examples:<br/>
SUCCESS:1:Xerox Device credintial:192.168.2.59:80:Xerox Versalink C7XXXX:Admin:1111:::<br/>
SUCCESS:4:Xerox Address book:192.168.2.59:80: Xerox Versalink C7XXX:::192.168.2.59_80_AddressBook_2024_26_02_11_22_13.csv::<br/>
<br/>
Descriptions:<br/>
Field 1: SUCCESS/FAILED<br/>
Field 2: Data type<br/>
&emsp;0: Not Defined<br/>
&emsp;1: Device Password<br/>
&emsp;2: Password data ( Email, Active Directory, FTP , Ect...)<br/>
&emsp;3: Extracted file data ( None Account Information such as print jobs or documents)<br/>
&emsp;4: Address books<br/>
&emsp;5: Finger Print<br/>
&emsp;6: Protocol Service Enabled<br/>
Field 3: Description<br/>
Field 4: Device IP Address<br/>
Field 5: Device Port Number<br/>
Field 6: Device Model Information<br/>
Field 7: Device Username<br/>
Field 8: Device Password<br/>
Field 9: Downloaded File Name<br/>
Field 10: Status<br/>
Field 11: Recommended Metasploit Module<br/>

