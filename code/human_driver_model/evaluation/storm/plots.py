# PLOTS - Generate some relevant plots that relate to the performance
# of different drivers.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 5-Jun-2018; Last revision: 5-Jun-2018

import sys, os, random, glob, csv, subprocess, itertools
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=13)

# Generate samples for some of the graphs
# seq = True iff two out of (v, v1, x1_0) are set
#
def generate_samples(N, *args, **kwargs):
	v_set = kwargs.get('v', None)
	v1_set = kwargs.get('v1', None)
	x1_0_set = kwargs.get('x1_0', None)
	path = kwargs.get('path', None)
	seq = bool(kwargs.get('seq', False))

	v_count = 15
	v1_count = 15
	x1_0_count = 10

	for i in range(1,N+1):
		while 1:
			if v1_set == None and seq == False:
				v1 = random.randint(15,34)
			elif v1_set == None and seq == True:
				v1 = v1_count
				v1_count = v1_count + 1
			else:
				v1 = int(v1_set)

			if v_set == None and seq == False:
				v = random.randint(15,34)
			elif v_set == None and seq == True:
				v = v_count
				v_count = v_count + 1
			else:
				v = int(v_set)

			if x1_0_set == None and seq == False:
				x1_0 = random.randint(10,80)
			elif x1_0_set == None and seq == True:
				x1_0 = x1_0_count
				x1_0_count = x1_0_count + 1
			else:
				x1_0 = int(x1_0_set)

			if v_count > 35 or v1_count > 35 or x1_0_count > 81:
				return

			if path == None:
				if not os.path.exists("%s/r_%s_%s_%s.csv"%(path,v,v1,x1_0)):
					break
			else:
				if not os.path.exists("%s/r_%s_%s_%s.csv"%(path,v,v1,x1_0)):
					break

		print('[%d/%d]: Evaluating drivers for v = %d, v1 = %d, x1_0 = %d...'%(i,N,v,v1,x1_0))
		if path == None:
			proc = subprocess.Popen('python3 storm_model_checker.py properties.pctl %d %d %d'%(v,v1,x1_0), stderr=subprocess.PIPE, shell=True)
		else:
			proc = subprocess.Popen('python3 storm_model_checker.py properties.pctl %d %d %d --path %s'%(v,v1,x1_0,path), stderr=subprocess.PIPE, shell=True)
		output = str(proc.stderr.read())


def generate_combination_samples(vs, v1s, x1_0s, path):
	sz = len(vs)*len(v1s)*len(x1_0s)
	print('Evaluating %d combinations...'%sz)

	for v in vs:
		for v1 in v1s:
			for x1_0 in x1_0s:
				if os.path.exists("%s/r_%s_%s_%s.csv"%(path,v,v1,x1_0)):
					continue

				print('v = %d, v1 = %d, x1_0 = %d:'%(v,v1,x1_0))
				proc = subprocess.Popen('python3 storm_model_checker.py properties.pctl %d %d %d --path %s'%(v,v1,x1_0,path), stderr=subprocess.PIPE, shell=True)
				output = str(proc.stderr.read())


def read_files_to_dict(path):
	props_dict = [{},{},{}]

	os.chdir("%s/"%path)
	for file in glob.glob("*.csv"):
		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if row["property"] in props_dict[int(row["type_driver"])-1].keys():
					props_dict[int(row["type_driver"])-1][row["property"]].append(float(row["probability"]))
				else:
					props_dict[int(row["type_driver"])-1][row["property"]] = [float(row["probability"])]

	return props_dict


def safety_plots(p, v1_in, x1_0_in):
	generate_samples(20, v1=v1_in, x1_0=x1_0_in, path=p, seq=True)

	x = [];
	y = [[],[],[]];

	os.chdir("%s/"%p)
	for file in glob.glob("*.csv"):
		x.append(int(str(file).split('_')[1]))

		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if row["property"] == 'P=? [F crashed]':
					y[int(row["type_driver"])-1].append(float(row["probability"]))

	labels = ["Aggressive", "Average", "Cautious"]

	for i in range(0,3):
		new_x, new_y = zip(*sorted(zip(x, y[i])))

		line = plt.plot(new_x, new_y, label=labels[i], marker="s")
	
	plt.legend(loc='upper left')

	plt.ylabel('P$_{=?}$ [F crashed]')
	plt.xlabel('v [m/s]')
	plt.title('Safety property for $v_1 = %d$, $x_{1,0} = %d$'%(v1_in, x1_0_in))
	plt.xticks(np.arange(min(new_x)-1, max(new_x)+1, 2))
	plt.show()


def safety_3D_plots(p):
	generate_combination_samples(np.linspace(20, 30, 11), np.linspace(15, 25, 11), [50],p)

	x = [];
	y = [];
	z = [[],[],[]];

	os.chdir("%s/"%p)
	for file in glob.glob("*.csv"):
		x.append(int(str(file).split('_')[1]))
		y.append(int(str(file).split('_')[2]))

		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if row["property"] == 'P=? [F crashed]':
					z[int(row["type_driver"])-1].append(float(row["probability"]))

	labels = ["Aggressive", "Average", "Cautious"]

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	# for i in range(0,3):
	line = ax.plot_trisurf(x, y, z[0], label="Aggressive", linewidth=0.2, antialiased=True, cmap=cm.coolwarm)
	
	# plt.legend(loc='upper left')
	ax.xaxis._axinfo['label']['space_factor'] = 3.0
	ax.yaxis._axinfo['label']['space_factor'] = 3.0
	ax.zaxis._axinfo['label']['space_factor'] = 3.0

	ax.set_xlabel('v [m/s]')
	ax.set_ylabel('v$_1$ [m/s]')
	ax.set_zlabel('P$_{=?}$ [F crashed]')

	ax.set_zticks(np.arange(np.min(z)+0.1, np.max(z), 0.1))
	plt.show()

# safety_plots('plot1', 20, 50)
safety_3D_plots('plot3')


