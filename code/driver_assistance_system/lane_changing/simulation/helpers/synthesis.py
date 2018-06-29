# SYNTHESIS - Given a set of initial conditions, build a model,
# verify it and obtain the correct multi-objective property for
# synthesis in order to obtain an adversary.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 13-Jun-2018; Last revision: 25-Jun-2018

import sys, os, subprocess, csv, argparse
import random

parser=argparse.ArgumentParser(
    description='''Given a PRISM model, obtain a sample trace and modify it.''')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('-p', '--path', type=str, help='Save the generated files to a certain path.')
parser.add_argument('-q', '--query', nargs='+', type=str, default='', help='Use the multi-objective query given.')
args=parser.parse_args()

v_in = args.v
v1_in = args.v1
x1_0_in = args.x1_0
q = ' '.join(args.query)

def build_and_synthesis(v, v1, x1_0, *args, **kwargs):
	path = kwargs.get('path', "built_models/r_%d_%d_%d"%(v,v1,x1_0))
	query = kwargs.get('query', "")

	# Construct the file
	print('Generating the model...')
	os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv %d %d %d > /dev/null'%(v,v1,x1_0))

	# ------------- Verification -------------
	if query == "":
		print('Building the model and performing verification...')
		proc = subprocess.Popen('storm --prism mdp_model.pm --prop helpers/properties/verification.pctl', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
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
		multi_obj_query = "multi(Pmax=? [F x=length & t < %d], P>=1 [F x=length])"%Tmin
		# multi_obj_query = "Pmax=? [F x=length & t < %d & lane=1]"%Tmin
		# multi_obj_query = "Pmax=? [F x=length | t = max_time]"
		# multi_obj_query = "Pmin=? [F crashed]"
	else:
		print('Skipping verification')
		multi_obj_query = query

	print('Synthesis using the query "%s"'%multi_obj_query)

	os.system("mkdir %s > /dev/null"%path)

	os.system('prism mdp_model.pm -exportmodel %s/out.all -lp -pctl "%s" -exportadvmdp %s/adv.tra -exportprodstates %s/new_states.sta -noprob1'%(path,multi_obj_query,path,path))

	f = open("%s/query.txt"%path, "w")
	f.write(multi_obj_query)
	f.close()

if args.path:
	build_and_synthesis(v_in, v1_in, x1_0_in, path=args.path, query=q)
else:
	build_and_synthesis(v_in, v1_in, x1_0_in, query=q)
