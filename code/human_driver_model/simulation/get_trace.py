# GET_TRACE - Given a PRISM model, obtain a sample 
# trace and modify it.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 14-May-2018; Last revision: 14-May-2018

import sys, os, subprocess, csv, argparse

parser=argparse.ArgumentParser(
    description='''Given a PRISM model, obtain a sample trace and modify it.''')
parser.add_argument('model.pm', type=str, help='The model from which to obtain the sample execution (built using model_generator.py).')
parser.add_argument('[v1]', type=int, help='Initial velocity of the other vehicle.')
parser.add_argument('[x1_0]', type=int, help='Initial position of the other vehicle.')
args=parser.parse_args()

cleaning_up = False

v1 = int(sys.argv[2])
x1_0 = int(sys.argv[3])

# Construct the file
print('Obtaining the sample path...')
subprocess.run("prism %s -simpath 'deadlock,sep=comma' path1.txt &> /dev/null"%sys.argv[1], shell=True)

# Read the generated text file
print('Read the generated file and modify the trace file to become readable in simulation...')

csvfile = open('gen_trace.csv', 'w')
fieldnames = ['t_end','type','v','crashed','lane','x_t_1','x_t_2','x_t_3','y_t_1','y_t_2','y_t_3','y_t_4','y_t_5','y_t_6','y_t_7']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

writer.writeheader()

next_change_lanes = False
curr_v = 0
curr_t = 0
curr_x = 0

with open('path1.txt') as csvfile:
	reader = csv.DictReader(csvfile)
	# Skip the first line
	next(reader)
	for row in reader:
		if row['action'] == "Decision_Making_Monitoring" and row["lC"] == "true":
			next_change_lanes = True
			curr_v = int(row['v'])
			curr_t = int(row['t'])
			curr_x = int(row['x'])

		if row['action'] == "Control" and next_change_lanes == False:
			if row['crashed'] == 'false':
				writer.writerow({'t_end': row['t'], 'type': '1', 'v': row['v'], 'crashed': '0', 'lane': row['lane'], 'x_t_1': '0', 'x_t_2': '0', 'x_t_3': '0', 'y_t_1': '0', 'y_t_2': '0', 'y_t_3': '0', 'y_t_4': '0', 'y_t_5': '0', 'y_t_6': '0', 'y_t_7': '0'})
			else:
				writer.writerow({'t_end': row['t'], 'type': '1', 'v': row['v'], 'crashed': '1', 'lane': row['lane'], 'x_t_1': '0', 'x_t_2': '0', 'x_t_3': '0', 'y_t_1': '0', 'y_t_2': '0', 'y_t_3': '0', 'y_t_4': '0', 'y_t_5': '0', 'y_t_6': '0', 'y_t_7': '0'})

		if row['action'] == "Control" and next_change_lanes == True:
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


if cleaning_up == True:
	print('Cleaning up...')
	os.system('rm path1.txt')


