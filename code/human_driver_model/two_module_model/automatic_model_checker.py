# AUTOMATIC_MODEL_CHECKER - Executes the script model_generator.py 
# for some given parameters in order to build the model and perform
# model checking subquentially.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 26-Apr-2018; Last revision: 27-Apr-2018

import sys, os, subprocess, csv, argparse

parser=argparse.ArgumentParser(
    description='''Executes the script model_generator.py for some given parameters in order to build the model and perform model checking subquentially.''')
parser.add_argument('properties_file', type=str, help='File of the properties to be checked (PCTL or LTL).')
parser.add_argument('[v]', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('[v1]', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('[x1_0]', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('--clean [VALUE]', type=str, help='If [VALUE] = False, then generated files (model and individual results) will be maintained (default = True).')
args=parser.parse_args()

types = ['aggressive','average','cautious']
res = {}

properties_file = sys.argv[1]
v = sys.argv[2]
v1 = sys.argv[3]
x1_0 = sys.argv[4]

if len(sys.argv) > 5 and sys.argv[5] == "False":
	cleaning_up = False
else:
	cleaning_up = True

num_properties = sum(1 for line in open(properties_file))
with open(properties_file) as f1:
    props = f1.readlines()
props = [x.strip() for x in props]

for driver_type in range(1,4):
	print('------ %s driver ------'%types[driver_type-1])

	filename = "gen_model_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)
	r_filename = "results_%s_%s_%s_%s_%s"%(driver_type,properties_file,v,v1,x1_0)

	# Construct the file
	print('Generating the model...')
	os.system('python3 model_generator.py model_tables/control_table.csv model_tables/acc_table.csv model_tables/dm_table.csv %s %s %s %s --filename results/%s > /dev/null'%(driver_type,v,v1,x1_0,filename))

	print('Building the model and performing model checking...')
	subprocess.run("prism results/%s.pm properties.pctl -exportresults results/%s.txt &> /dev/null"%(filename, r_filename), shell=True)

	print('Obtaining the results...')

	f = open("results/%s.txt"%r_filename, "r")

	if num_properties == 1:
		f.readline()
		probability = f.readline()
		f.close()

		probability = float(probability[:-1])
		res[driver_type] = [props[0], probability]
	else:
		f.readline()
		f.readline()
		probability = f.readline()

		probability = float(probability[:-1])
		res[driver_type] = [[props[0], probability]]

		for i in range(1,num_properties):
			f.readline()
			f.readline()
			f.readline()
			probability = f.readline()

			probability = float(probability[:-1])
			res[driver_type].append([props[i], probability])

	f.close()

	if cleaning_up == True:
		print('Cleaning up...')
		os.system('rm results/%s.pm'%filename)
		os.system('rm results/%s.txt'%r_filename)

with open('results/%s_%s_%s_%s.csv'%(properties_file,v,v1,x1_0), 'w') as csvfile:
    fieldnames = ['type_driver', 'property', 'probability']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for key,val in res.items():
    	for propty in val:
    		writer.writerow({'type_driver': key, 'property': propty[0], 'probability': propty[1]})

print('Done.')








