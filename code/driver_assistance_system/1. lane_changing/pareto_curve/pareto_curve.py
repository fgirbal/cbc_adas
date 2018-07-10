# PARETO_CURVE - Generate the model, perform verification to obtain
# the appropriate multi-objective synthesis problem and 
# perform synthesis to obtain the pareto curve desired.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 9-Jun-2018; Last revision: 10-Jul-2018

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
parser.add_argument('--cond', '-c', action="store_true", help='If set, conditional probabilities will be displayed.')
parser.add_argument('--clean', action="store_true", help='If set, then generated files (model and individual results) will be cleared.')
parser.add_argument('--path', '-p', type=str, default="results", help='Generated file will be saved in PATH.')
args=parser.parse_args()

res = []

v = args.v
v1 = args.v1
x1_0 = args.x1_0
path = args.path
cleaning_up = args.clean
cond = args.cond
properties_file = "properties/verification.pctl"


def obtain_curve():
	# Construct the file
	print('Generating the model...')
	os.system('python3 ../model/mdp_generator.py ../model/model_tables/control_table.csv ../model/model_tables/acc_table.csv %s %s %s > /dev/null'%(v,v1,x1_0))

	# ------------- Verification -------------
	print('Building the model and performing verification...')
	proc = subprocess.Popen('storm --prism mdp_model.pm --prop properties/verification.pctl', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	output = str(proc.stdout.read())

	idx = output.find('\\n-------------------------------------------------------------- \\n', 500)
	output = output[idx + 69:]
	idx3 = 0

	Tmin = 30

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
	multi_obj_query = "multi(Pmin=? [F crashed], Pmax=? [F (x=length) & (t<%d)])"%Tmin
	print('Synthesis using the query "%s"'%multi_obj_query)

	os.system("mkdir results/r_%s_%s_%s > /dev/null"%(v,v1,x1_0))

	proc = subprocess.Popen('storm --prism mdp_model.pm --prop "%s" --multiobjective:precision 0.01 --multiobjective:exportplot results/r_%s_%s_%s'%(multi_obj_query,v,v1,x1_0), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	output = str(proc.stdout.read())

	f = open("results/r_%s_%s_%s/time.txt"%(v,v1,x1_0), "w")
	f.write(str(Tmin))
	f.close()

def draw_curve():
	x = []
	y = []

	f = open("results/r_%s_%s_%s/time.txt"%(v,v1,x1_0), "r")
	Tmin = int(f.readline())
	f.close()

	with open("results/r_%s_%s_%s/paretopoints.csv"%(v,v1,x1_0)) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			x.append(float(row["x"]))
			y.append(float(row["y"]))

	new_x, new_y = zip(*sorted(zip(x, y)))
	new_x = [xs for xs in new_x]
	new_y = [ys for ys in new_y]

	fig, ax = plt.subplots()

	if len(new_x) == 2 and new_x == [0,0] and new_y == [0,1]:
		new_x = [0]
		new_y = [1]

	if cond:
		for i in range(len(new_y)):
			new_y[i] = min(new_y[i]/(1-new_x[i]),1)

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
	if not cond:
		plt.ylabel('P$_{max=?}$ [F ((x = 500) \& (t $<$ %s))]'%Tmin)
	else:
		plt.ylabel('P$_{max=?}$ [F ((x = 500) \& (t $<$ %s)) $|$ F (x=500)]'%Tmin)

	plt.show()


if not os.path.exists("results/r_%s_%s_%s/paretopoints.csv"%(v,v1,x1_0)) or not os.path.exists("results/r_%s_%s_%s/time.txt"%(v,v1,x1_0)):
	obtain_curve()

draw_curve()
print('Done.')





