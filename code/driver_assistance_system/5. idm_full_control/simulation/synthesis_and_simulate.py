# SYNTHESIS_AND_SIMULATE - Given some initial conditions, 
# obtain a sample trace and simulate it.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 1-Jul-2018; Last revision: 1-Jul-2018

import sys, os, csv, argparse, subprocess

parser=argparse.ArgumentParser(
    description='''Given some initial conditions, obtain a sample trace and simulate it.''')
parser.add_argument('driver_type', type=int, default=2, help='1 = aggressive, 2 = average, 3 = cautious.')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('-p', '--path', type=str, help='Path where the all the files will be generated.')
parser.add_argument('-q', '--query', type=str, help='Use the multi-objective query given.')
parser.add_argument('-o', '--output', type=str, default="adv", help='Name of the output adversary generated.')
parser.add_argument('-x', '--times', type=float, default=1, help='Execution is X times faster.')
parser.add_argument('-rt', '--read_trace', action="store_true", help='Read an existing trace.')
parser.add_argument('-ra', '--read_adv', action="store_true", help='Read an adversary and generate a new trace only.')
parser.add_argument('-a', '--adv', type=str, default="adv", help='Read an adversary and generate a new trace only.')
args=parser.parse_args()

driver_type = args.driver_type
v = args.v
v1 = args.v1
x1_0 = args.x1_0
output = args.output

speed = args.times
adv = args.adv

if args.path:
	p = args.path
else:
	p = "built_models/r_%d_%d_%d_%d"%(driver_type,v,v1,x1_0)

if not args.read_trace:

	if not args.read_adv:
		# Synthesis
		if not args.query:
			os.system("python3 helpers/synthesis.py %d %d %d %d -p %s -o %s"%(driver_type, v, v1, x1_0, p, output))
		else:
			os.system('python3 helpers/synthesis.py %d %d %d %d -p %s -q "%s" -o %s'%(driver_type, v, v1, x1_0, p, args.query, output))
	else:
		print("Skip synthesis; read adversary from %s.tra and generate new trace to simulate."%adv)

	states_file = "out.sta"
	labels_file = "out.lab"
	new_states_file = "%s_new_states.sta"%adv
	adv_file = "%s.tra"%adv

	# Multi-objective synthesis
	os.system("python3 helpers/multi_gen_trace.py %s %s %s %s %d %d -p %s"%(states_file, labels_file, new_states_file, adv_file, v1, x1_0, p))

else:
	print("Reading existing trace...")

os.system("python3 helpers/simulate.py %d %d %d %s/gen_trace.csv -x %f"%(v, v1, x1_0, p, speed))


