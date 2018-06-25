# SYNTHESIS_AND_SIMULATE - Given some initial conditions, 
# obtain a sample trace and simulate it.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 23-Jun-2018; Last revision: 25-Jun-2018

import sys, os, csv, argparse, subprocess

parser=argparse.ArgumentParser(
    description='''Given some initial conditions, obtain a sample trace and simulate it.''')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('-p', '--path', type=str, help='Path where the all the files will be generated.')
parser.add_argument('-x', '--times', type=float, default=1, help='Execution is X times faster.')
parser.add_argument('-r', '--read', action="store_true", help='Read an existing trace.')
parser.add_argument('-q', '--query', type=str, help='Use the multi-objective query given.')
args=parser.parse_args()

v = args.v
v1 = args.v1
x1_0 = args.x1_0

speed = args.times

if args.path:
	p = args.path
else:
	p = "built_models/r_%d_%d_%d"%(v,v1,x1_0)

if not args.read:

	# Synthesis
	if not args.query:
		os.system("python3 helpers/synthesis.py %d %d %d -p %s"%(v, v1, x1_0, p))
	else:
		os.system('python3 helpers/synthesis.py %d %d %d -p %s -q "%s"'%(v, v1, x1_0, p, args.query))

	states_file = "out.sta"
	labels_file = "out.lab"
	new_states_file = "new_states.sta"
	adv_file = "adv.tra"

	# Multi-objective synthesis
	os.system("python3 helpers/multi_gen_trace.py %s %s %s %s %d %d -p %s"%(states_file, labels_file, new_states_file, adv_file, v1, x1_0, p))

else:
	print("Reading existing trace...")

os.system("python3 helpers/simulate.py %d %d %d %s/gen_trace.csv -x %f"%(v, v1, x1_0, p, speed))


