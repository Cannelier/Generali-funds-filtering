import os
import pandas as pd
import numpy as np
import re
import csv
from functools import reduce
import shutil
import pysftp
from datetime import datetime
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#-------------- PARAMETERS SETTING -------------------
parser = argparse.ArgumentParser()
parser.add_argument("--custodian", help="Which Custodian ?")
parser.add_argument("--countrycode", help="1:FR 2:?? ?", default="1")
parser.add_argument("--env", help="PROD, UAT...", default="PROD")

args = parser.parse_args()
custodian = args.custodian
countrycode = args.countrycode
env = args.env


mailing_list = []
with open("mailing_list.csv","r+") as file:
	for line in file:
		"""mail = re.findall('[\w\.]+@\w+\.[a-zA-Z]+',line)[0]
		print(mail)"""
		mailing_list.append(line.rstrip('\n'))

#-------------- RETRIEVE SOURCE FILES, MOVE TO "inputs" folder  -------------------------

current_date = datetime.today().strftime('%Y%m%d')
input_file = "XXXXXX" + custodian + countrycode + current_date+".csv"
custodian_directory = "//XXXXXXXXX"+custodian+env+"/"
original_path = custodian_directory+"Archives/Original/"
filtered_path = custodian_directory+"Archives/Filtered/"

#-------------- GENERATES LIST OF REGEX FROM "scope.csv" -------------------
scope = "scope"+custodian+".csv"

def define_scope(file): #list of regex
    scope = []
    with open(file,"r+") as file:
        for line in file:
            code = re.findall('[A-Za-z0-9]+',line)[0]
            scope.append("^"+code)
    return scope

#-------------- TO RESIZE A FILE BASED ON A LIST OF REGEX -------------------
def resize(file,scope,name_file):
	with open(file, "r+") as f:
	    df = pd.read_csv(f,sep=";",dtype=str)
	columns = df.columns
	output_df = pd.DataFrame()
	for code in scope:
		subTable = df.loc[df['column'].str.match(code)] #for 1 ICODPTF, extract 1 table of ICODPTF + shareclasses
		output_df = pd.concat([output_df,subTable]) #concat all tables
	output_csv = output_df.to_csv(sep=";",index=False)
	with open(filtered_path+name_file,"w",newline="") as f:
		f.write(output_csv)
	return("GIL_"+name_file)

def send_mail(title,content,recipients):
	SEND_ADDRESS = "XXX@gmail.com"
	PASSWORD = "password"
	HOST = "SMTP.gmail.com"
	PORT = 25
	s = smtplib.SMTP(host=HOST, port=PORT)
	s.starttls()
	s.login(SEND_ADDRESS, PASSWORD)
	msg = MIMEMultipart()       # create a message
	print(message)
	# setup the parameters of the message
	msg['From']= SEND_ADDRESS
	msg['To']= ", ".join(recipients)
	msg['Subject'] = title
	msg.attach(MIMEText(content, 'plain'))
	s.send_message(msg)
	del msg
	print("Mail sent to: ",recipients)
	s.quit()

"""def send_mail(title,content,recipients):
	print(title,"\n",content,"\n",recipients)"""

message = ""

try:
	shutil.copy(custodian_directory+input_file,original_path)
	print("Copying file ", custodian_directory+input_file," to folder ",original_path," : OK")
	try:
		print("Filtering on scope")
		scope = define_scope(scope)
		sent_file = resize(original_path+input_file,scope,input_file)
		print("Fund filtering done, starting SFTP connection")

		#------SFTP-------

		cnopts = pysftp.CnOpts()
		cnopts.hostkeys = None 
		host = "HOST"
		port = 587
		fileTo_folder = "destination_folder"

		if env == "PROD":
			user = "username"
			password = "password"
		elif env == "UAT":
			user = "username"
			password = "password"

		try:
			with pysftp.Connection(host=host, username=user, password=password, port=port, cnopts=cnopts) as sftp:
				print ('------------Connexion ok------------')
				path_from = filtered_path+sent_file
				path_to = fileTo_folder+sent_file
				print("From: "+path_from)
				print("To: "+path_to)
				try:
					sftp.put(path_from,path_to)
					print("-----------File sent-------------")
					os.remove(custodian_directory+input_file)
					message = "File " + path_from + " was successfully sent."
					title = "["+env+"]"+"["+custodian+"]"+"["+countrycode+"]"+"File transfer: OK"
					send_mail(title,message,mailing_list)
			
				except:
					error_log = "ERROR-FILE-TRANSFER: File couldn't be send\n"
					print(error_log)
					message = message + error_log
					title = "["+env+"]"+"["+custodian+"]"+"["+countrycode+"]"+"File transfer: ERROR LOG"
					send_mail(title,message,mailing_list)

		except:
			error_log = "ERROR-FILE-TRANSFER: Connexion couldn't be established\n"
			print(error_log)
			message = message + error_log
			title = "["+env+"]"+"["+custodian+"]"+"["+countrycode+"]"+"File transfer: ERROR LOG"
			send_mail(title,message,mailing_list)

	except:
		error_log = "ERROR-FILE-TRANSFER: Fund filtering\n"
		print(error_log)
		message = message + error_log
		title = "["+env+"]"+"["+custodian+"]"+"["+countrycode+"]"+"File transfer: ERROR LOG"
		send_mail(title,message,mailing_list)

except:
	error_log = "WARNING-FILE-TRANSFER: No file to be processed\n"
	print(error_log)
	message = message + error_log
	title = "["+env+"]"+"["+custodian+"]"+"["+countrycode+"]"+"File transfer: ERROR LOG"
	#send_mail(title,message,mailing_list)