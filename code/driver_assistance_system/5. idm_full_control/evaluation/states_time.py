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

		os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv ../model/model_tables/dm_table.csv %s %s %s %s > /dev/null'%(driver_type,v,v1,x1_0,))

		print(str(i) + ".2")

		proc = subprocess.Popen('prism mdp_model.pm -javamaxmem 4g -cuddmaxmem 2g', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		output = str(proc.stdout.read())

		idx = output.find("Time for model construction:")
		line = output[idx:]

		g = open('curr.txt', 'w')
		g.write(line)
		g.close()

		upper_bound = line.find('seconds.')
		time = output[idx+29:idx+upper_bound]
		print(time)

		idx = output.find("States:")
		line = output[idx+1:]
		upper_bound = line.find('(1 initial)')
		states = output[idx+13:idx+upper_bound]
		print(states)

		idx = output.find("Transitions:")
		line = output[idx+1:]
		upper_bound = line.find('\\n')
		trans = output[idx+13:idx+upper_bound+1]
		print(trans)
		
		f.write("%s,%s,%s,%s,%s,%s,%s\n"%(driver_type,v,v1,x1_0,states,trans,time))

f.close()