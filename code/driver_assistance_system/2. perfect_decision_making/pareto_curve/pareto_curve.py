# PARETO_CURVE - Generate the model, perform verification to obtain
# the appropriate multi-objective synthesis problem and 
# perform synthesis to obtain the pareto curve desired (changed to
# use PRISM instead of storm).

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 26-Jun-2018; Last revision: 29-Jun-2018

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
parser.add_argument('v', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('v1', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('x1_0', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('--path', '-p', type=str, default="results", help='Generated file will be saved in PATH.')
args=parser.parse_args()

v = args.v
v1 = args.v1
x1_0 = args.x1_0
path = args.path

def obtain_curve():
	ex_path = "results/r_%s_%s_%s"%(v,v1,x1_0)

	os.system("mkdir %s > /dev/null"%ex_path)

	# Construct the file
	print('Generating the model...')
	os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv %s %s %s > /dev/null'%(v,v1,x1_0))

	# ------------- Verification -------------
	print('Building the model and performing verification (could take awhile - no longer than 10 minutes)...')
	os.system('prism mdp_model.pm properties/verification_mod.pctl -exportmodel %s/out.all -exportresults %s/res.txt'%(ex_path, ex_path))

	f = open("%s/res.txt"%ex_path, "r")

	Tmin = 30

	while True:
		prop = f.readline()[:-2]
		if prop == "":
			break
		f.readline()
		probability = f.readline()[:-1]

		print(prop + ' : ' + probability)

		if 'Pmax=? [ F (x=500&t<' in prop and probability != "0.0":
			T = int(prop[20:22])
			Tmin = min(T, Tmin)

		f.readline()

	f.close()

	# ------------- Synthesis -------------
	multi_obj_query = "multi(Pmin=? [F crashed], Pmax=? [F (x=500) & (t<%d)])"%Tmin
	print('Synthesis using the query "%s"'%multi_obj_query)

	proc = subprocess.Popen('prism -importmodel %s/out.all -pctl "%s" -exportpareto %s/paretopoints.txt'%(ex_path,multi_obj_query,ex_path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	output = str(proc.stdout.read())

	f = open("results/r_%s_%s_%s/time.txt"%(v,v1,x1_0), "w")
	f.write(str(Tmin))
	f.close()

def draw_curve():
	ex_path = "results/r_%s_%s_%s"%(v,v1,x1_0)
	x = []
	y = []

	f = open("%s/time.txt"%ex_path, "r")
	Tmin = int(f.readline())
	f.close()

	f = open("%s/paretopoints.txt"%ex_path, "r")
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
		new_y.append(0)

		new_x.append(min(x))
		new_y.append(0)

		xy = np.vstack((new_x, new_y)).T

		polygon = [Polygon(xy, True)]
		p = PatchCollection(polygon, alpha=0.3)
		p.set_color("g")

		ax.add_collection(p)

	plt.xlabel('P$_{min=?}$ [F crashed]')
	plt.ylabel('P$_{max=?}$ [F ((x = 500) \& (t $<$ %s))]'%Tmin)

	plt.show()


if not os.path.exists("results/r_%s_%s_%s/paretopoints.txt"%(v,v1,x1_0)) or not os.path.exists("results/r_%s_%s_%s/time.txt"%(v,v1,x1_0)):
	obtain_curve()

draw_curve()
print('Done.')





