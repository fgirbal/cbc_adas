# SYNTHESIS - Given a set of initial conditions, build a model,
# verify it and obtain the correct multi-objective property for
# synthesis in order to obtain an adversary.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 1-Jul-2018; Last revision: 1-Jul-2018

import sys, os, subprocess, csv, argparse
import random

parser=argparse.ArgumentParser(
    description='''Given a set of initial conditions, build a model, verify it and obtain the correct multi-objective property for synthesis in order to obtain an adversary.''')
parser.add_argument('driver_type', type=int, default=2, help='1 = aggressive, 2 = average, 3 = cautious.')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('--query', '-q', type=str, default="", help='Query to generate an adversary on.')
parser.add_argument('--output', '-o', type=str, default="adv", help='Name of the adversary file generated for the query.')
parser.add_argument('--path', '-p', type=str, default="", help='Generated file will be saved in PATH.')
args=parser.parse_args()

driver_type = args.driver_type
v = args.v
v1 = args.v1
x1_0 = args.x1_0
path = args.path
query = args.query
output = args.output

def build_model(ex_path):
	os.system("mkdir %s > /dev/null"%ex_path)

	# Construct the file
	print('Generating the model...')
	os.system('python3 model/mdp_generator.py model/model_tables/control_table.csv model/model_tables/acc_table.csv model/model_tables/dm_table.csv %s %s %s %s > /dev/null'%(driver_type,v,v1,x1_0))

	# ------------- Verification -------------
	print('Building the model and performing verification (could take awhile - no longer than 10 minutes)...')
	os.system('prism mdp_model.pm helpers/properties/verification_mod.pctl -exportmodel %s/out.all -exportresults %s/res.txt -javamaxmem 4g -cuddmaxmem 2g'%(ex_path, ex_path))

	f = open("%s/res.txt"%ex_path, "r")

	Tmin = 30

	while True:
		prop = f.readline()[:-2]
		if prop == "":
			break
		f.readline()
		probability = f.readline()[:-1]

		print(prop + ' : ' + probability)

		if 'Pmax=? [ F (x=length&t<' in prop and float(probability) > 0.001:
			T = int(prop[23:25])
			Tmin = min(T, Tmin)

		f.readline()

	f.close()

	f = open("%s/time.txt"%ex_path, "w")
	f.write(str(Tmin))
	f.close()


def synthesis(ex_path, query, output):
	# ------------- Synthesis -------------
	if query == "":
		f = open("%s/time.txt"%ex_path, "r")
		Tmin = int(f.readline())
		f.close()
		multi_obj_query = "multi(Pmax=? [F x=400 & t < %d], P<=0.18 [F crashed])"%Tmin
	else:
		multi_obj_query = query

	print('Synthesis using the query "%s"...'%multi_obj_query)

	os.system('prism -importmodel %s/out.all -lp -pctl "%s" -exportadv %s/%s.tra -exportprodstates %s/%s_new_states.sta -javamaxmem 4g -cuddmaxmem 2g'%(ex_path,multi_obj_query,ex_path,output,ex_path,output))

	print('Outputing to %s.tra, %s_new_states.sta and %s_query.txt'%(output,output,output))

	f = open("%s/%s_query.txt"%(ex_path,output), "w")
	f.write(multi_obj_query)
	f.close()


# def_path = "%s/r_%s_%s_%s_%s"%(path,driver_type,v,v1,x1_0)
def_path = path

if not os.path.exists("%s/res.txt"%def_path):
	build_model(def_path)

if not os.path.exists("%s/%s.txt"%(def_path,output)):
	synthesis(def_path, query, output)

