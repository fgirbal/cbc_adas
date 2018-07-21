import sys, os, glob

f = open('values.txt', 'w')

for file in glob.glob("*.csv"):
	f.write("%s\n"%file)

f.close()