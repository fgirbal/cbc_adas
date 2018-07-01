# MULTI_GEN_TRACE - Given the states and labels of an MDP,
# the adversary generated and the states of the product of
# the MDP by the DRA, obtain a trace in the original MDP

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 1-Jul-2018; Last revision: 1-Jul-2018

import sys, os, subprocess, csv, argparse
import random

parser=argparse.ArgumentParser(
    description='''Given the states and labels of an MDP, the adversary generated and the states of the product of the MDP by the DRA, obtain a trace in the original MDP''')
parser.add_argument('mdp_states', type=str, help='States of the original MDP.')
parser.add_argument('mdp_labels', type=str, help='Labels of the original MDP.')
parser.add_argument('new_states', type=str, help='States of the product MDP (of the original and the DRA of the property).')
parser.add_argument('adversary', type=str, help='Transitions in the new state space.')
parser.add_argument('v1', type=int, help='Initial speed of the other vehicle.')
parser.add_argument('x1_0', type=int, help='Initial position of the other vehicle.')
parser.add_argument('-o', '--output', type=str, default="gen_trace.csv", help='Name of the generated .csv file (path excluded).')
parser.add_argument('-p', '--path', type=str, default="", help='Path where the the input files are stored, and text and csv files will be generated.')
parser.add_argument('-c', '--clear', action="store_true", help='Clear the generated trace text file.')
args=parser.parse_args()

states_file = "%s/%s"%(args.path,args.mdp_states)
labels_file = "%s/%s"%(args.path,args.mdp_labels)
new_states_file = "%s/%s"%(args.path,args.new_states)
adv_file = "%s/%s"%(args.path,args.adversary)

def multi_transform_label_file(old_states, old_labels, new_states):
	new_init_states = []
	new_deadlocks = []

	sta = {}
	init_states = []
	deadlocks = []

	# import internal state representation
	f = open(old_states, "r")
	header = f.readline()[:-1]
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split(':')
		sta[s[0]] = s[1][1:-1]

	f.close()

	# import init and deadlock states
	f = open(old_labels, "r")
	f.readline()
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split(':')
		if s[1] == " 0":
			init_states.append(sta[s[0]])
		elif s[1] == " 1":
			deadlocks.append(sta[s[0]])

	f.close()

	# import internal state representation
	f = open(new_states, "r")
	header = f.readline()[1:-1]
	header_sp = header.split(',')
	t_index = header_sp.index("t")
	lane_index = header_sp.index("lane")

	while True:
		s = f.readline()[:-2]
		if s == "":
			break

		s = s.split(':')
		s1_spl = s[1].split(',')
		new_s1 = ','.join(s1_spl[t_index:lane_index+1])
		if t_index == 0:
			new_s1 = new_s1[1:]

		if new_s1 in init_states:
			new_init_states.append(s[0])
		elif new_s1 in deadlocks:
			new_deadlocks.append(s[0])

	f.close()

	new_labels = {'init': new_init_states, 'deadlocks': new_deadlocks}
	return new_labels

def multi_generate_sample_path(new_states_f, adv_f, new_labels, result_file):
	print('Generate a sample path in the synthesised model...')

	sta = {}
	tra = {}
	init_states = new_labels['init']
	deadlocks = new_labels['deadlocks']
	step = 0

	# import internal state representation
	f = open(new_states_f, "r")
	header = f.readline()[:-1]
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split(':')
		sta[s[0]] = s[1]

	f.close()

	# import state transitions
	f = open(adv_f, "r")
	f.readline()
	while True:
		s = f.readline()[:-1]
		if s == "":
			break

		s = s.split()
		if s[0] in tra.keys():
			if '0' in tra[s[0]].keys():
				tra[s[0]]['0'].append([s[1], s[2]])
			else:
				tra[s[0]]['0'] = [[s[1], s[2]]]
		else:
			tra[s[0]] = {}

			if '0' in tra[s[0]].keys():
				tra[s[0]]['0'].append([s[1], s[2]])
			else:
				tra[s[0]]['0'] = [[s[1], s[2]]]

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

def multi_generate_trace_from_file(file, v1, x1_0, out):
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

				infile = open("helpers/data/other_table.csv")
				r = csv.DictReader(infile)
				for i in range(idx_line-1):
					next(r)
				this_row = next(r)

				if row['crashed'] == 'false':
					writer.writerow({'t_end': row['t'], 'type': '2', 'v': row['v'], 'crashed': '0', 'lane': o_lane, 'x_t_1': this_row['p_x(1)'], 'x_t_2': this_row['p_x(2)'], 'x_t_3': this_row['p_x(3)'], 'y_t_1': this_row['p_y(1)'], 'y_t_2': this_row['p_y(2)'], 'y_t_3': this_row['p_y(3)'], 'y_t_4': this_row['p_y(4)'], 'y_t_5': this_row['p_y(5)'], 'y_t_6': this_row['p_y(6)'], 'y_t_7': this_row['p_y(7)']})
				else:
					writer.writerow({'t_end': row['t'], 'type': '2', 'v': row['v'], 'crashed': '1', 'lane': o_lane, 'x_t_1': this_row['p_x(1)'], 'x_t_2': this_row['p_x(2)'], 'x_t_3': this_row['p_x(3)'], 'y_t_1': this_row['p_y(1)'], 'y_t_2': this_row['p_y(2)'], 'y_t_3': this_row['p_y(3)'], 'y_t_4': this_row['p_y(4)'], 'y_t_5': this_row['p_y(5)'], 'y_t_6': this_row['p_y(6)'], 'y_t_7': this_row['p_y(7)']})

				next_change_lanes = False


new_labels = multi_transform_label_file(states_file, labels_file, new_states_file)
multi_generate_sample_path(new_states_file, adv_file, new_labels, "%s/trace.txt"%args.path)
multi_generate_trace_from_file("%s/trace.txt"%args.path, args.v1, args.x1_0, "%s/%s"%(args.path,args.output))
if args.clear:
	os.system("rm -f %s/trace.txt"%args.path)

