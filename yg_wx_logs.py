#!/usr/bin/env python
import paramiko
import datetime
import time
import os
import subprocess, shlex
import getpass
from paramiko import client

def subprocess_cmd(cmd1,cmd2):
    process = subprocess.Popen("{}; {}".format(cmd1, cmd2),stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout


def convertTime(date): #takes as input the date and returns a datetime object
	dateObj = datetime.datetime.strptime(date, '%Y_%m_%d')
	return dateObj

			
def filesNeeded(dateObj):#takes as input the datetime obj and returns the files needed to download
	filesNeeded =[]
	dateObjs = []
	dateObjs.append(dateObj-datetime.timedelta(days=1))
	dateObjs.append(dateObj)
	for dates in dateObjs:	
		filesNeeded.append( 'mets_'+str(dates.year)+'_'+str('%02d' % dates.month)+'_'+str('%02d' % dates.day)+'.dat')
	return filesNeeded 

def secureFTP(files2Download): #Takes as input (as an array/list) the names of the files needed and downloads them using sftp
	#stole most of this from http://stackoverflow.com/a/3635163	
	host = "59.167.111.242"
	port = 26
	transport = paramiko.Transport((host, port))
	username = "observer"
	print 'Opening a sftp connection to '+host+' and logging in as ' +username
	time.sleep(1)	
	password = getpass.getpass("Please enter the password for the sftp server (observer@59.167.111.242) ")
	transport.connect(username = username, password = password)
	sftp = paramiko.SFTPClient.from_transport(transport)
	for files in files2Download:
		print 'Downloading '+files+'.....'
		filepath = '/metdata/'+files
		localpath = '/home/observer/ask/yglogs/'+files
		sftp.get(filepath, localpath)
	sftp.close()
	transport.close()

class ssh:
    client = None
 
    def __init__(self, address, username, password):
        print("Connecting to server.")
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
 
    def sendCommand(self, command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata
 
                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")

def fetchLog(station, experiment):
    print('Retrieving %s%s.log from pcfs%s' %(experiment,station,station))
    os.system('scp oper@pcfs%s:/usr2/log/%s%s.log /home/observer/ask/yglogs/' %(station,experiment,station))

def returnLog(station, experiment):
    print('Putting %s%s.log on pcfs%s' %(experiment,station,station))
    os.system('scp /home/observer/ask/yglogs/%s%s.log oper@pcfs%s:/usr2/log/' %(experiment,station,station))

def main():
	expName = raw_input ("Please enter the name for the experiment (e.g. t2114). ")
	expDate = raw_input ("Please enter the date for the experiment (e.g. 2016_06_01). ")	
	startTime = raw_input ("Please enter the start time for the experiment (e.g. 320.17:30). ")
	stopTime = raw_input ("Please enter the end time for the experiment (e.g. 321.17:30). ")
	fetchLog('yg',expName)
	files2Download = []
	dateObj = convertTime(expDate)	
	files2Download = filesNeeded(dateObj)
	secureFTP(files2Download)
	dir1 = 'cd /home/observer/ask/yglogs/'
	dir2 = 'cd /home/observer/ask/yglogs/'
	command1 = "metdat_format.sh "+files2Download[0]+' '+files2Download[1]+' > wx_tmp.log' 
	command2 = "metdat_startstop.sh	wx_tmp.log "+startTime+' ' +stopTime+' > '+dir1[3:]+'wx_'+expName+'yg.log'
	command3 = 'head -5 wx_'+expName+'yg.log'
	command4 = 'tail -5 wx_'+expName+'yg.log'
	command5 = 'cp '+expName+'yg.log'+' ' +expName+'yg_original.log'
	command6 = 'grep -v /wx/ '+expName+'yg.log > '+expName+'yg_no_wx.log'
	command7 = 'sort -s -m -k 1,1.20 -o '+expName+'yg.log '+expName+'yg_no_wx.log wx_'+expName+'yg.log'
	commands = [command1,command2,command3,command4,command5,command6,command7]
	
	for x in range(2):
		print commands[x]	
		subprocess_cmd(dir1,commands[x])
		time.sleep(3)	
	for x in range(2,len(commands)):
		print commands[x]
		subprocess_cmd(dir2,commands[x])
		time.sleep(3)
	copyFile = 'cp '+dir1[3:]+expName+'yg.log'+' '+'/vlbobs/ivs/logs/'
	print 'Copying the edited ' +expName+'yg.log'+ ' to '+	'/vlbobs/ivs/logs/'
	subprocess_cmd(copyFile, 'cd')
	password = getpass.getpass('Please enter a password for oper@pcfs ')
	connection = ssh("pcfsyg","oper",password)
	print 'Backing up the original log on pcfsyg '
	command8 = 'cd /usr2/log/ && cp '+expName+'yg.log'+' '+expName+'yg_original2.log'
	print command8
	connection.sendCommand(command8)
	returnLog('yg',expName)
		
main()
