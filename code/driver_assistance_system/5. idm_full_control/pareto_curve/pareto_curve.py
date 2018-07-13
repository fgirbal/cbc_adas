# PARETO_CURVE - Generate the model, perform verification to obtain
# the appropriate multi-objective synthesis problem and 
# perform synthesis to obtain the pareto curve desired (changed to
# use PRISM instead of storm).

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 29-Jun-2018; Last revision: 10-Jul-2018

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
parser.add_argument('--cond', '-c', action="store_true", help='If set, conditional probabilities will be displayed.')
parser.add_argument('--output', '-o', type=str, default="paretopoints", help='Name of the generated file')
parser.add_argument('--query', '-q', type=str, default="", help='Query to build the Pareto curve on.')
parser.add_argument('--path', '-p', type=str, default="results", help='Generated file will be saved in PATH.')
args=parser.parse_args()

driver_type = args.driver_type
v = args.v
v1 = args.v1
x1_0 = args.x1_0
path = args.path
output = args.output
query = args.query
cond = args.cond


def build_model(ex_path):
	os.system("mkdir %s > /dev/null"%ex_path)

	# Construct the file
	print('Generating the model...')
	os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv ../model/model_tables/dm_table.csv %s %s %s %s > /dev/null'%(driver_type,v,v1,x1_0))

	# ------------- Verification -------------
	print('Building the model and performing verification (could take awhile - no longer than 10 minutes)...')
	os.system('prism mdp_model.pm properties/verification_mod.pctl -exportmodel %s/out.all -exportresults %s/res.txt -javamaxmem 4g'%(ex_path, ex_path))

	f = open("%s/res.txt"%ex_path, "r")

	Tmin = 30

	while True:
		prop = f.readline()[:-2]
		if prop == "":
			break
		f.readline()
		probability = f.readline()[:-1]

		print(prop + ' : ' + probability)

		if 'Pmax=? [ F (x=500&t<' in prop and float(probability) > 0.001:
			T = int(prop[20:22])
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
		multi_obj_query = "multi(Pmin=? [F crashed], Pmax=? [F (x=500) & (t<%d)])"%Tmin
	else:
		multi_obj_query = query

	print('Synthesis using the query "%s"...'%multi_obj_query)

	os.system('prism -importmodel %s/out.all -pctl "%s" -exportpareto %s/%s.txt'%(ex_path,multi_obj_query,ex_path,output))
	# output_1 = str(proc.stdout.read())

	print('Outputing to %s.txt and %s_query.txt'%(output,output))

	f = open("%s/%s_query.txt"%(ex_path,output), "w")
	f.write(multi_obj_query)
	f.close()


def draw_curve(ex_path, input_file, cond):
	x = []
	y = []

	f = open("%s/%s_query.txt"%(ex_path,input_file), "r")
	query = f.readline()
	f.close()

	# LaTeX display handlers
	query = query.replace("min=?", "$_{min=?}$")
	query = query.replace("max=?", "$_{max=?}$")
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

	if cond:
		for i in range(len(new_y)):
			new_y[i] = min(new_y[i]/(1-new_x[i]),1)

		ylabel = "%s $|$ F (x=500)]"%ylabel[:-1]

	fig, ax = plt.subplots()

	plt.plot(new_x, new_y, marker = 'o', color='g')

	if len(new_x) > 1:
		new_x.append(max(x))
		new_y.append(0)

		new_x.append(min(x))
		new_y.append(0)

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

if not os.path.exists("%s/res.txt"%def_path):
	build_model(def_path)

if not os.path.exists("%s/%s.txt"%(def_path,output)):
	synthesis(def_path, query, output)

draw_curve(def_path, output, cond)
print('Done.')





