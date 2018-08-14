# AUTOMATIC_MODEL_CHECKER - Executes the script model_generator.py 
# for some given parameters in order to build the model and perform
# model checking subquentially.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 13-Jul-2018; Last revision: 13-Jul-2018

import sys, os, subprocess, csv, argparse
from datetime import datetime
startTime = datetime.now()

parser=argparse.ArgumentParser(
    description='''Executes the script model_generator.py for some given parameters in order to build the model and perform model checking subquentially.''')
parser.add_argument('properties_file', type=str, help='File of the properties to be checked (PCTL or LTL).')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('--path', '-p', type=str, default='gen_files', help='Path where the generated files will be saved.')
parser.add_argument('--clean', '-c', action="store_true", help='If set, then generated files (model and individual results) will be maintained.')
args=parser.parse_args()

types = ['aggressive','average','cautious']
res = {}

properties_file = args.properties_file
v = args.v
v1 = args.v1
x1_0 = args.x1_0
cleaning_up = not args.clean
path = args.path

num_properties = sum(1 for line in open("%s"%properties_file))
with open("%s"%properties_file) as f1:
    props = f1.readlines()
props = [x.strip() for x in props]

for driver_type in range(1,4):
	print('------ %s driver ------'%types[driver_type-1])

	filename = "gen_model_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)
	r_filename = "results_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)

	# Construct the file
	print('Generating the model...')
	os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv ../model/model_tables/dm_table.csv %s %s %s %s --filename %s > /dev/null'%(driver_type,v,v1,x1_0,filename))

	print('Building the model and performing model checking...')
	subprocess.run("prism %s.pm %s -exportresults %s/%s.txt -javamaxmem 4g -cuddmaxmem 2g"%(filename, properties_file, path, r_filename), shell=True)

	print('Obtaining the results...')

	f = open("%s/%s.txt"%(path, r_filename), "r")

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
		os.system('rm %s.pm'%filename)
		# os.system('rm %s/%s.txt'%(path,r_filename))

with open('%s/r_%s_%s_%s.csv'%(path,v,v1,x1_0), 'w') as csvfile:
    fieldnames = ['type_driver', 'property', 'probability']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for key,val in res.items():
    	for propty in val:
    		writer.writerow({'type_driver': key, 'property': propty[0], 'probability': propty[1]})

# for driver_type in range(1,4):
# 	r_filename = "results_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)
# 	os.system('rm %s/%s.txt'%(path,r_filename))

print('Done.')
print(datetime.now() - startTime)








