import sys, os, subprocess, csv, argparse
# from datetime import datetime

f = open('states_time_res.csv', 'w')
f.write("d_type,v,v1,x1_0,states,transitions,time\n")

i = 0

with open('test_cases.csv', 'r') as csvfile:
	reader = csv.DictReader(csvfile)
	
	for row in reader:
		i = i + 1
		print(i)

		driver_type = row['d_type']
		v = row['v']
		v1 = row['v1']
		x1_0 = row['x1_0']

		os.system('python3 source/model_generator.py source/model_tables/control_table.csv source/model_tables/acc_table.csv source/model_tables/dm_table.csv %s %s %s %s > /dev/null'%(driver_type,v,v1,x1_0))

		proc = subprocess.Popen('storm --prism two_component_model.pm', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		output = str(proc.stdout.read())

		idx = output.find("Time for model construction:")
		time = output[idx+29:idx+34]
		# print(time)

		idx = output.find("States:")
		states = output[idx+10:idx+13]
		# print(states)

		idx = output.find("Transitions:")
		trans = output[idx+15:idx+18]
		# print(trans)
		
		f.write("%s,%s,%s,%s,%s,%s,%s\n"%(driver_type,v,v1,x1_0,states,trans,time))

f.close()