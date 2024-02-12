Praeda II
This file is used to list a few config items and recommendation. Also some basic Praeda syntax 


Required Python modules:  This is to be added later
???

PRAEDA OPTIONS:
-g GNMAP_FILE
-n CIDR or CIDR_FILE 
-t TARGET_FILE
-p TCP_PORT
-j PTOJECT_NAME
-l OUTPUT_LOG_FILE
-S SSL

GNMAP_FILE = This is a .gnmap file output by a nmap scan.
CIDR & CIDR_FILE = Subnet CIDR "192.168.1.0/24" or file containing list of CIDRs
TARGET_FILE = List of IP addresses or Host names to enumerated
TCP_PORT = port address of targets to scan " At present only one port can be specified. This is expected to be modified in future version"
PROJECT_NAME = the name for this project. This will create a folder under the folder where Praeda was executed to contain logs and export info.
OUTPUT_LOG_FILE = name of log file for data output


SYNTAX FOR GNMAP FILE INPUT:
praeda.pl -g GNMAP_FILE -j PROJECT_NAME -l OUTPUT_LOG_FILE

SYNTAX FOR IP  CIDR/CIDR FILE LIST:
praeda.pl -t CIDR or CIDR_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL


SYNTAX FOR IP TARGET FILE LIST:
praeda.pl -t TARGET_FILE -p TCP_PORT -j PROJECT_NAME -l OUTPUT_LOG_FILE -s SSL 
 

Examples:

./praeda.pl -g scan1.gnmap -j acmewidget -l results

./praeda.pl  -n 10.10.10.0/24 -p 80  -j project1 -l data-file

./praeda.pl  -n cidrs.txt -p 80  -j project1 -l data-file

./praeda.pl  -t target.txt -p 80  -j project1 -l data-file

./praeda.pl  -t target.txt -p 443  -j project1 -l data-file -s SSL

The results will create a folder called project1 and save all information in that folder. Also this will write out the following data.
targetdata.txt  : This is the parsed results of .gnmap file
$LOGFILE-WebHost.txt : This is an output of all webservers querried listing IP:PORT:TITLE:SERVER
$LOGFILE.log : This file will contain the results of the modules executed.
RAW extract data including: Clones, Backups, Address Books ect...
