#**Praeda II**


This file is used to list a few config items and recommendation. Also some basic Praeda syntax 

Required Python modules:  This is to be added later

Because of varios SSL/TLS and DH key length issues encountered with MFP devices it is highly recommended that this tool be installed and run on a kali image. Kali images have a properly compiled openssl that supports out of compliance SSL/TLS and DH key and certificates.

Also if during operation if you receive SSL error **"[SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled (_ssl.c:1007)"** while trying to connect to certain devices. This occures on system with newer version of openssl which disabled legacy renegotiontions. I have seen this specifically on Ubuntu 22.  The solution is to re-enable this legacy renegotiation. The following link has direction on making the needed changes to the openssl.cnf. Do this with cautions because it does reduce the level of SSL security on your device and potential encreases risk of MiTM attacks against SSL.

**https://pipeawk.com/index.php/2022/05/19/openssl-enable-legacy-renegotiation/**

Another solution is to install Praeda-II on a Kali images which has the legacy renegotiation enabled or do the above on a VM images and not your primary machine.

**PRAEDA OPTIONS:**

-g GNMAP_FILE

-n CIDR or CIDR_FILE 

-t TARGET_FILE

-p TCP_PORT

-j PTOJECT_NAME

-l OUTPUT_LOG_FILE

-S SSL

**GNMAP_FILE** = This is a .gnmap file output by a nmap scan.

**CIDR & CIDR_FILE** = Subnet CIDR "192.168.1.0/24" or file containing list of CIDRs

**TARGET_FILE** = List of IP addresses or Host names to enumerated

**TCP_PORT** = port address of targets to scan " At present only one port can be specified. This is expected to be modified in future version"

**PROJECT_NAME** = the name for this project. This will create a folder under the folder where Praeda was executed to contain logs and export info.

**OUTPUT_LOG_FILE** = name of log file for data output


**SYNTAX FOR GNMAP FILE INPUT:**
praeda.py -g GNMAP_FILE -j PROJECT_NAME -l OUTPUT_LOG_FILE

**SYNTAX FOR IP  CIDR/CIDR FILE LIST:**
praeda.py -t CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL

**SYNTAX FOR IP TARGET FILE LIST:**
praeda.py -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL 
 
**Examples:**

./praeda.py -g scan1.gnmap -j acmewidget -l results

./praeda.py  -n 10.10.10.0/24 -p 80  -j project1 -l data-file

./praeda.py  -n cidrs.txt -p 80  -j project1 -l data-file

./praeda.py  -t target.txt -p 80  -j project1 -l data-file

./praeda.py  -t target.txt -p 443  -j project1 -l data-file -s SSL

The results will create a folder called project1 and save all information in that folder. Also this will write out the following data.
targetdata.txt  : This is the parsed results of .gnmap file
$LOGFILE-WebHost.txt : This is an output of all webservers querried listing IP:PORT:TITLE:SERVER
$LOGFILE.log : This file will contain the results of the modules executed.
RAW extract data including: Clones, Backups, Address Books ect...



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
Field 3: Description<br/>
Field 4: Device IP Address<br/>
Field 5: Device Port Number<br/>
Field 6: Device Model Information<br/>
Field 7: Device Username<br/>
Field 8: Device Password<br/>
Field 9: Downloaded File Name<br/>
Field 10: Status<br/>
Field 11: Recommended Metasploit Module<br/>

