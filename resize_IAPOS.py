import os
import pandas as pd
import re
import csv
from functools import reduce
import shutil

#-------------- INITIALIZE PATH NAMES -------------------------
input_directory = "inputs/"
merged_file_path = "mergedInputs/merged_file.csv"
open(merged_file_path,"w").close()
output_file_path = "output/output.csv"


#-------------- MERGING FILES FROM FOLDER "/files" INTO "merged_file.csv" --------

filesPath =[]
dfs = []
for filePath in os.listdir(input_directory):
	filesPath.append(input_directory+filePath) #files =  ['inputs/file1.csv', 'inputs/file2.csv']

print(filesPath)

def merge(file1,file2):
	print(file2)
	with open(file1,"a") as f1:
		with open(file2,"r") as f2:
			f2.readline()
			for line in f2:
				f1.write(line)
	shutil.copy(file2,'archives/') #coupe les fichiers vers archives après les avoir mergés
	os.remove(file2)
	return file1
shutil.copy(filesPath[0],'archives/')
reduce(lambda file1,file2: merge(file1,file2),filesPath)
shutil.copyfile(filesPath[0],merged_file_path)
os.remove(filesPath[0])

#	dfs.append(pd.read_csv(input_directory+filePath))
#combined_csv = pd.concat([pd.read_csv(f).fillna("") for f in filesPath])
#combined_csv.to_csv("combined_csv.csv",sep=";")

#merged_file = reduce(lambda df1,df2:pd.concat([df1,df2]),dfs)
"""with open(merged_file_path,"w",newline="") as f:
	f.write(merged_file.to_csv())"""
#merged_file.to_csv(merged_file_path)


#-------------- GENERATES LIST OF REGEX FROM "scope.csv" -------------------
scope = "scope.csv"

def define_scope(file): #list of regex
    scope = []
    with open(file,"r+") as file:
        for line in file:
            code = re.findall('[A-Za-z0-9]+',line)[0]
            scope.append("^"+code)
    return scope

#-------------- TO RESIZE A FILE BASED ON A LIST OF REGEX -------------------
def resize(file,scope):
	with open(file, "r+") as f:
	    df = pd.read_csv(f,sep=";")
	columns = df.columns
	output_df = pd.DataFrame()
	for code in scope:
		subTable = df.loc[df['ICODPTF'].str.match(code)] #for 1 ICODPTF, extract 1 table of ICODPTF + shareclasses
		output_df = pd.concat([output_df,subTable]) #concat all tables
	output_csv = output_df.to_csv(sep=";")
	with open(output_file_path,"w",newline="") as f:
		f.write(output_csv)

scope = define_scope(scope)
resize(merged_file_path,scope)