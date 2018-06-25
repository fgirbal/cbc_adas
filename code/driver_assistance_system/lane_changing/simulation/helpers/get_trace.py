# ------------------- DEPRECATED -----------------------
#
# GET_TRACE - Given a PRISM model, perform verification to obtain 
# the synthesis formulation, perform synthesis and extract a strategy;
# from this, generate a random path

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 13-Jun-2018; Last revision: 13-Jun-2018

import sys, os, subprocess, csv, argparse
import random

parser=argparse.ArgumentParser(
    description='''Given a PRISM model, obtain a sample trace and modify it.''')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('-n', '--name', type=str, default="gen_trace.csv", help='Name of the generated .csv file (path included).')
parser.add_argument('-p', '--path', type=str, help='Force a read/save of generated data to a certain path.')
args=parser.parse_args()

cleaning_up = True

v_in = args.v
v1_in = args.v1
x1_0_in = args.x1_0

def build_and_synthesis(v, v1, x1_0, *args, **kwargs):
	path = kwargs.get('path', "built_models/r_%d_%d_%d"%(v,v1,x1_0))

	# Construct the file
	print('Generating the model...')
	os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv %d %d %d > /dev/null'%(v,v1,x1_0))

	# ------------- Verification -------------
	print('Building the model and performing verification...')
	proc = subprocess.Popen('storm --prism mdp_model.pm --prop properties/verification.pctl', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	output = str(proc.stdout.read())

	idx = output.find('\\n-------------------------------------------------------------- \\n', 500)
	output = output[idx + 69:]
	idx3 = 0

	Tmin = 30
	res = []

	while idx3 != -1:
		idx1 = output.find('\\n')
		first_line = output[0:idx1]
		idx2 = output.find('\\n', idx1+1)
		second_line = output[idx1+2:idx2+2]
		idx3 = output.find('\\n\\n', idx2+1)

		prop = first_line[24:first_line.find('...')-1]
		val = second_line[29:second_line.find('\\n')]

		try:
			probability = float(val)
		except ValueError:
			print('----------------------------------\n\n')
			print(output)
			exit()

		res.append([prop, probability])
		
		print(prop + ' : ' + str(probability))
		if 'Pmax=? [F ((x = 500) & (t <' in prop and probability != 0:
			T = int(prop[28:30])
			Tmin = min(T, Tmin)
		output = output[idx3+4:]

	# ------------- Synthesis -------------
	# multi_obj_query = "multi(Pmax=? [F x=length | t = max_time], P>=1 [F x=length & t < %d])"%Tmin
	multi_obj_query = "multi(Pmax=? [F x=length & t < %d], P>=1 [F x=length | t = max_time])"%Tmin
	# multi_obj_query = "Pmax=? [F x=length & t < %d & lane=1]"%Tmin
	# multi_obj_query = "Pmax=? [F x=length | t = max_time]"
	# multi_obj_query = "Pmin=? [F crashed]"
	print('Synthesis using the query "%s"'%multi_obj_query)

	os.system("mkdir %s > /dev/null"%path)

	os.system('prism mdp_model.pm -exportmodel %s/out.all -lp -pctl "%s" -exportadvmdp %s/adv.tra -exportprodstates new_states.sta'%(path,multi_obj_query,path))

	return Tmin

def generate_sample_path(state_file, transition_file, label_file, result_file):
	print('Generate a sample path in the synthesised model...')

	sta = {}
	tra = {}
	init_states = []
	deadlocks = []
	step = 0

	# import internal state representation
	f = open(state_file, "r")
	header = f.readline()[:-1]
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split(':')
		sta[s[0]] = s[1]

	f.close()

	# import init and deadlock states
	f = open(label_file, "r")
	f.readline()
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split(':')
		if s[1] == " 0":
			init_states.append(s[0])
		elif s[1] == " 1":
			deadlocks.append(s[0])

	f.close()

	# import state transitions
	f = open(transition_file, "r")
	f.readline()
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split()
		if s[0] in tra.keys():
			if s[1] in tra[s[0]].keys():
				tra[s[0]][s[1]].append([s[2], s[3]])
			else:
				tra[s[0]][s[1]] = [[s[2], s[3]]]
		else:
			tra[s[0]] = {}

			if s[1] in tra[s[0]].keys():
				tra[s[0]][s[1]].append([s[2], s[3]])
			else:
				tra[s[0]][s[1]] = [[s[2], s[3]]]

	# print("\n".join("{}\t{}".format(k, v) for k, v in tra.items()))

	f.close()
	
	# start simulation
	f = open(result_file, "w")
	f.write("step," + header[1:-1] + "\n")
	curr_state = random.choice(init_states)
	f.write(str(step) + "," + sta[curr_state][1:-1] + "\n")

	while (not curr_state in deadlocks) and (curr_state in tra.keys()):
		possible_trans = tra[curr_state]
		action_taken = random.choice(list(possible_trans.keys()))
		diff_trans = possible_trans[action_taken]

		if len(diff_trans) == 1:
			curr_state = diff_trans[0][0]
		else:
			possible_states = []
			cum_probabilities = []

			for elem in diff_trans:
				possible_states.append(elem[0])
				if len(cum_probabilities) == 0:
					cum_probabilities.append(float(elem[1]))
				else:
					cum_probabilities.append(cum_probabilities[len(cum_probabilities) - 1] + float(elem[1]))

			random_prob = random.uniform(0, 1)
			i = 0
			while True:
				if random_prob <= cum_probabilities[i]:
					break
				i = i+1

			curr_state = possible_states[i]
		
		step = step + 1
		f.write(str(step) + "," + sta[curr_state][1:-1] + "\n")

	f.close()

def generate_trace_from_file(file, v1, x1_0, out):
	# Read the generated text file
	print('Read the generated file and modify the trace file to become readable in simulation...')

	csvfile = open(out, 'w')
	fieldnames = ['t_end','type','v','crashed','lane','x_t_1','x_t_2','x_t_3','y_t_1','y_t_2','y_t_3','y_t_4','y_t_5','y_t_6','y_t_7']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()

	next_change_lanes = False
	curr_v = 0
	curr_t = 0
	curr_x = 0

	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		# Skip the first line
		# next(reader)
		for row in reader:

			if row['actrState'] == "1" and row["lC"] == "false":
				curr_v = int(row['v'])

			if row['actrState'] == "1" and row["lC"] == "true":
				next_change_lanes = True
				curr_v = int(row['v'])
				curr_t = int(row['t'])
				curr_x = int(row['x'])

			if row['actrState'] == "2" and next_change_lanes == False:
				if row['crashed'] == 'false':
					writer.writerow({'t_end': row['t'], 'type': '1', 'v': curr_v, 'crashed': '0', 'lane': row['lane'], 'x_t_1': '0', 'x_t_2': '0', 'x_t_3': '0', 'y_t_1': '0', 'y_t_2': '0', 'y_t_3': '0', 'y_t_4': '0', 'y_t_5': '0', 'y_t_6': '0', 'y_t_7': '0'})
				else:
					writer.writerow({'t_end': row['t'], 'type': '1', 'v': curr_v, 'crashed': '1', 'lane': row['lane'], 'x_t_1': '0', 'x_t_2': '0', 'x_t_3': '0', 'y_t_1': '0', 'y_t_2': '0', 'y_t_3': '0', 'y_t_4': '0', 'y_t_5': '0', 'y_t_6': '0', 'y_t_7': '0'})

			if row['actrState'] == "2" and next_change_lanes == True:
				lane = int(row['lane'])
				o_lane = 3 - lane
				idx_line = (2-lane)*20*20*43 + (v1 - 15)*20*43 + (curr_v - 15)*43 + min(abs(x1_0 + v1*curr_t - curr_x), 43)

				infile = open("data/other_table.csv")
				r = csv.DictReader(infile)
				for i in range(idx_line-1):
					next(r)
				this_row = next(r)

				if row['crashed'] == 'false':
					writer.writerow({'t_end': row['t'], 'type': '2', 'v': row['v'], 'crashed': '0', 'lane': o_lane, 'x_t_1': this_row['p_x(1)'], 'x_t_2': this_row['p_x(2)'], 'x_t_3': this_row['p_x(3)'], 'y_t_1': this_row['p_y(1)'], 'y_t_2': this_row['p_y(2)'], 'y_t_3': this_row['p_y(3)'], 'y_t_4': this_row['p_y(4)'], 'y_t_5': this_row['p_y(5)'], 'y_t_6': this_row['p_y(6)'], 'y_t_7': this_row['p_y(7)']})
				else:
					writer.writerow({'t_end': row['t'], 'type': '2', 'v': row['v'], 'crashed': '1', 'lane': o_lane, 'x_t_1': this_row['p_x(1)'], 'x_t_2': this_row['p_x(2)'], 'x_t_3': this_row['p_x(3)'], 'y_t_1': this_row['p_y(1)'], 'y_t_2': this_row['p_y(2)'], 'y_t_3': this_row['p_y(3)'], 'y_t_4': this_row['p_y(4)'], 'y_t_5': this_row['p_y(5)'], 'y_t_6': this_row['p_y(6)'], 'y_t_7': this_row['p_y(7)']})

				next_change_lanes = False

if not args.path:
	path = "built_models/r_%d_%d_%d"%(v_in,v1_in,x1_0_in)
else:
	path = args.path

if not os.path.exists("%s/adv.tra"%path) and not os.path.exists("%s/adv1.tra"%path):
	build_and_synthesis(v_in, v1_in, x1_0_in, path=path)

txt_name = "%s/%s_path.txt"%(path, args.name[:-4])

if os.path.exists("%s/adv.tra"%path):
	generate_sample_path('%s/out.sta'%path, '%s/adv.tra'%path, '%s/out.lab'%path, txt_name)
elif os.path.exists("%s/adv1.tra"%path):
	generate_sample_path('%s/out.sta'%path, '%s/adv1.tra'%path, '%s/out.lab'%path, txt_name)

generate_trace_from_file(txt_name, v1_in, x1_0_in, "%s/%s"%(path, args.name))




