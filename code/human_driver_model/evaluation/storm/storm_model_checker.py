# STORM_MODEL_CHECKER - Executes the script model_generator.py 
# for some given parameters in order to build the model and perform
# model checking subquentially in storm (changed to use the path source/).

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 3-Jun-2018; Last revision: 3-Jun-2018

import sys, os, subprocess, csv, argparse
from datetime import datetime
startTime = datetime.now()

parser=argparse.ArgumentParser(
    description='''Executes the script model_generator.py for some given parameters in order to build the model and perform model checking subquentially in storm (changed to use the path source/).''')
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

progress = True

if len(sys.argv) > 5 and sys.argv[6] == "False":
	cleaning_up = False
else:
	cleaning_up = True

if progress == True:
	toolbar_width = 9
	sys.stdout.write("Progress: [%s]" % (" " * toolbar_width))
	sys.stdout.flush()
	sys.stdout.write("\b" * (toolbar_width+1))

for driver_type in range(1,4):
	if progress == False:
		print('------ %s driver ------'%types[driver_type-1])

	filename = "gen_model_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)
	r_filename = "results_%s_%s_%s_%s_%s"%(driver_type,properties_file,v,v1,x1_0)

	# Construct the file
	if progress == False:
		print('Generating the model...')
	os.system('python3 source/model_generator.py source/model_tables/control_table.csv source/model_tables/acc_table.csv source/model_tables/dm_table.csv %s %s %s %s --filename source/%s > /dev/null'%(driver_type,v,v1,x1_0,filename))

	if progress == True:
		sys.stdout.write("=")
		sys.stdout.flush()

	if progress == False:
		print('Building the model and performing model checking...')
	proc = subprocess.Popen('storm --prism source/%s.pm --prop source/%s'%(filename, properties_file), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	output = str(proc.stdout.read())
	
	if progress == True:
		sys.stdout.write("=")
		sys.stdout.flush()

	idx = output.find('\\n-------------------------------------------------------------- \\n', 500)
	output = output[idx + 69:]
	idx3 = 0

	while idx3 != -1:
		idx1 = output.find('\\n')
		first_line = output[0:idx1]
		idx2 = output.find('\\n', idx1+1)
		second_line = output[idx1+2:idx2+2]
		idx3 = output.find('\\n\\n', idx2+1)

		prop = first_line[24:first_line.find('...')-1]
		val = second_line[29:second_line.find('\\n')]

		probability = float(val)
		if not driver_type in res.keys():
			res[driver_type] = [[prop, probability]]
		else:
			res[driver_type].append([prop, probability])
		if progress == False:
			print(prop + ' : ' + str(probability))
		output = output[idx3+4:]

	if cleaning_up == True:
		if progress == False:
			print('Cleaning up...')
		os.system('rm source/%s.pm'%filename)

	if progress == True:
		sys.stdout.write("=")
		sys.stdout.flush()

if progress == True:
	sys.stdout.write("\n")

with open('gen_files/r_%s_%s_%s.csv'%(v,v1,x1_0), 'w') as csvfile:
    fieldnames = ['type_driver', 'property', 'probability']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for key,val in res.items():
    	for propty in val:
    		writer.writerow({'type_driver': key, 'property': propty[0], 'probability': propty[1]})

if progress == False:
	print('Done.')
	print(datetime.now() - startTime)






