# PARETO_CURVE - Generate the model and use a specific
# multi-objective query to synthesise strategies which
# penalise time spent in the left lane.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 16-Jul-2018; Last revision: 13-Aug-2018

import sys, os, subprocess, csv, argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib import cm

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=13)

parser=argparse.ArgumentParser(
    description='''Generate the model, perform verification to obtain the appropriate multi-objective synthesis problem and perform synthesis to obtain the pareto curve desired.''')
parser.add_argument('driver_type', type=int, default=2, help='1 = aggressive, 2 = average, 3 = cautious.')
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('--query', '-q', type=str, default="multi(Pmin=? [F crashed], Rmin=? [C])", help='Query to build the Pareto curve on.')
parser.add_argument('--output', '-o', type=str, default="paretopoints", help='Name of the generated file')
parser.add_argument('--path', '-p', type=str, default="results", help='Generated file will be saved in PATH.')
args=parser.parse_args()

driver_type = args.driver_type
v = args.v
v1 = args.v1
x1_0 = args.x1_0
path = args.path
output = args.output
query = args.query


def build_model_and_synthesis(ex_path, query, output):
	os.system("mkdir %s > /dev/null"%ex_path)

	# Construct the file
	print('Generating the model...')
	os.system('python3 mdp_generator.py model_tables/control_table.csv model_tables/acc_table.csv model_tables/dm_table.csv %s %s %s %s > /dev/null'%(driver_type,v,v1,x1_0))

	multi_obj_query = query

	print('Building model and synthesis using the query "%s"...'%multi_obj_query)

	os.system('prism mdp_model.pm -pctl "%s" -exportpareto %s/%s.txt -javamaxmem 4g'%(multi_obj_query, ex_path, output))

	print('Outputing to %s.txt and %s_query.txt'%(output,output))

	f = open("%s/%s_query.txt"%(ex_path,output), "w")
	f.write(multi_obj_query)
	f.close()


def draw_curve(ex_path, input_file):
	x = []
	y = []

	f = open("%s/%s_query.txt"%(ex_path,input_file), "r")
	query = f.readline()
	f.close()

	floor = True

	# LaTeX display handlers
	query = query.replace("min=?", '$_{=?}$')
	query = query.replace("max=?", "$_{=?}$")
	query = query.replace("&", "\&")
	query = query.replace("<", "$<$")
	query = query.replace(">", "$>$")

	xlabel = query.split(',')[0][6:]
	ylabel = query.split(',')[1][:-1]

	f = open("%s/%s.txt"%(ex_path,input_file), "r")
	arr_val = f.readline()[2:-1]
	new_arr = arr_val.split(', (')
	for tup in new_arr:
		text_tup = tup[:-1]
		x.append(float(text_tup.split(', ')[0]))
		y.append(float(text_tup.split(', ')[1]))
	f.close()

	new_x, new_y = zip(*sorted(zip(x, y)))
	new_x = [xs for xs in new_x]
	new_y = [ys for ys in new_y]

	fig, ax = plt.subplots()

	plt.plot(new_x, new_y, marker = 'o', color='g')

	if len(new_x) > 1:
		new_x.append(max(x))
		new_x.append(min(x))

		if floor:
			new_y.append(min(y)-2)
			new_y.append(min(y)-2)
		else:
			new_y.append(max(y)+2)
			new_y.append(max(y)+2)

		xy = np.vstack((new_x, new_y)).T

		polygon = [Polygon(xy, True)]
		p = PatchCollection(polygon, alpha=0.3)
		p.set_color("g")

		ax.add_collection(p)

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	# plt.title(query)

	plt.show()

def_path = "%s/r_%s_%s_%s_%s"%(path,driver_type,v,v1,x1_0)

if not os.path.exists("%s/%s.txt"%(def_path,output)):
	build_model_and_synthesis(def_path, query, output)

draw_curve(def_path, output)
print('Done.')





