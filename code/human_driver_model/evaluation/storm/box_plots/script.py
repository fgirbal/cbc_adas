import sys, os, glob

values = []

with open('values.txt') as openfileobject:
    for line in openfileobject:
    	values.append(line[:-1])

for file in glob.glob("*.csv"):
	if not file in values:
		os.system('mv %s other_tests/'%file)

