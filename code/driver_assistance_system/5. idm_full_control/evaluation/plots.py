# PLOTS - Generate some relevant plots that relate to the performance
# of the driver + the ADAS.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 13-Jul-2018; Last revision: 17-Jul-2018

import sys, os, random, glob, csv, subprocess, itertools
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib import rcParams
import matplotlib as mpl

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=24)

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
				x1_0 = random.randint(35,80)
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
			os.system('python3 automatic_model_checker.py properties/verification.pctl %d %d %d'%(v,v1,x1_0))
		else:
			os.system('python3 automatic_model_checker.py properties/verification.pctl %d %d %d --path %s'%(v,v1,x1_0,path))
		# output = str(proc.stderr.read())


def generate_combination_samples(vs, v1s, x1_0s, p):
	sz = len(vs)*len(v1s)*len(x1_0s)
	print('Evaluating %d combinations...'%sz)

	for v in vs:
		for v1 in v1s:
			for x1_0 in x1_0s:
				print('v = %d, v1 = %d, x1_0 = %d:'%(v,v1,x1_0))

				if os.path.exists("%s/r_%d_%d_%d.csv"%(p,v,v1,x1_0)):
					continue

				os.system('python3 automatic_model_checker.py properties/safety.pctl %d %d %d --path %s'%(v,v1,x1_0,p))


def generate_samples_box_plots(N):
	n = 1
	while n < N + 1:
		I = random.randint(0,249)

		f = open('values.txt')
		line = f.readline()
		i = 0
		while i < I:
			line = f.readline()
			i += 1

		if os.path.exists('box_plots/%s'%line):
			continue

		v = line.split('_')[1]
		v1 = line.split('_')[2]
		x1_0 = line.split('_')[3][0:2]

		print(str(n) + ": v = " + v + ", v1 = " + v1 + ", x1_0 = " + x1_0)

		if os.system('python3 automatic_model_checker.py properties/verification.pctl %s %s %s --path box_plots'%(v,v1,x1_0)) != 0:
			exit()

		n = n + 1


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
	# generate_samples(20, v1=v1_in, x1_0=x1_0_in, path=p, seq=True)

	x = [];
	y = [[],[],[]];

	os.chdir("%s/"%p)
	for file in glob.glob("*.csv"):
		x.append(int(str(file).split('_')[1]))

		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if row["property"] == 'Pmin=? [ F crashed ]':
					y[int(row["type_driver"])-1].append(float(row["probability"]))

	labels = ["Aggressive", "Average", "Cautious"]

	for i in range(0,3):
		new_x, new_y = zip(*sorted(zip(x, y[i])))

		line = plt.plot(new_x, new_y, label=labels[i], marker="s")
	
	plt.legend(loc='upper left', fontsize=18)

	plt.ylabel('P$_{min=?}$ [F crashed]', fontsize=18)
	plt.xlabel('v [m/s]', fontsize=18)
	# plt.title('Safety property for $v_1 = %d$, $x_{1,0} = %d$'%(v1_in, x1_0_in))
	plt.xticks(np.arange(min(new_x)-1, max(new_x)+1, 2))

	plt.subplots_adjust(right=0.95, top=0.95, left=0.19, bottom=0.16)
	plt.show()


def safety_3D_plots(p):
	# generate_combination_samples(np.linspace(20, 30, 11), np.linspace(15, 25, 11), [50], p)

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
				if row["property"] == 'Pmin=? [ F crashed ]':
					z[int(row["type_driver"])-1].append(float(row["probability"]))

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	line = ax.plot_trisurf(x, y, z[0], label="Aggressive", linewidth=0.2, antialiased=True, cmap=cm.viridis)
	line = ax.plot_trisurf(x, y, z[1], label="Average", linewidth=0.2, antialiased=True, cmap=cm.plasma)
	line = ax.plot_trisurf(x, y, z[2], label="Cautious", linewidth=0.2, antialiased=True, cmap=cm.inferno)
	
	ax.xaxis._axinfo['label']['space_factor'] = 3.0
	ax.yaxis._axinfo['label']['space_factor'] = 3.0
	ax.zaxis._axinfo['label']['space_factor'] = 3.0

	ax.set_xlabel('v [m/s]')
	ax.set_ylabel('v$_1$ [m/s]')
	ax.set_zlabel('P$_{min=?}$ [F crashed]')

	fake2Dline1 = mpl.lines.Line2D([0],[0], linestyle="none", c='b', marker = 'o')
	fake2Dline2 = mpl.lines.Line2D([0],[0], linestyle="none", c='b', marker = 'o')
	fake2Dline3 = mpl.lines.Line2D([0],[0], linestyle="none", c='b', marker = 'o')
	ax.legend([fake2Dline1, fake2Dline2, fake2Dline3], ['Aggressive', 'Average', 'Cautious'], numpoints = 1)

	# ax.set_zticks(np.arange(np.min(z)+0.1, np.max(z), 0.1))
	plt.show()


def liveness_2D_plot(p, v_in, v1_in, x1_0_in):
	# generate_samples(1, v=v_in, v1=v1_in, x1_0=x1_0_in, path=p)

	x = [[],[],[]];
	y = [[],[],[]];
	pmin_crashed = [0,0,0];

	with open("%s/r_%s_%s_%s.csv"%(p,v_in,v1_in,x1_0_in)) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if 'Pmin=? [ F crashed ]' in row["property"]:
				pmin_crashed[int(row["type_driver"])-1] = float(row["probability"])

			if 'Pmax=? [ F (x=500 & t < ' in row["property"]:
				x_val = int(row["property"][24:26])
				x[int(row["type_driver"])-1].append(x_val)
				y[int(row["type_driver"])-1].append(float(row["probability"]))

	labels = ["Aggressive", "Average", "Cautious"]

	for i in range(0,3):
		for l in range(0,len(x[i])):
			y[i][l] = min(y[i][l]/(1-pmin_crashed[i]),1)

	for i in range(0,3):
		x[i].append(27)
		y[i].append(1)

		x[i].append(28)
		y[i].append(1)

		new_x, new_y = zip(*sorted(zip(x[i], y[i])))

		line = plt.plot(new_x, new_y, label=labels[i], marker="s")
	
	plt.legend(loc='lower right', fontsize=18)

	# plt.ylabel('P$_{max=?}$ [F (x = 500) \& (t $<$ T)]/P$_{max=?}$ [F (x = 500)]', fontsize=15)
	plt.ylabel('$\zeta(T)$', fontsize=18)
	plt.xlabel('T [s]', fontsize=18)
	# plt.title('Liveness property for $v = %d$, $v_1 = %d$, $x_{1,0} = %d$'%(v_in, v1_in, x1_0_in))
	plt.xticks(np.arange(min(new_x)-1, max(new_x)+1, 2))

	plt.subplots_adjust(right=0.95, top=0.95, left=0.19, bottom=0.16)
	plt.show()


def safety_box_plot(p):
	props_dict = read_files_to_dict(p)

	vals = [[],[],[]]
	vals[0] = props_dict[0]['Pmin=? [ F crashed ]']
	vals[1] = props_dict[1]['Pmin=? [ F crashed ]']
	vals[2] = props_dict[2]['Pmin=? [ F crashed ]']

	plt.boxplot(vals, labels=["Aggressive", "Average", "Cautious"], whis=4)
	plt.ylabel('P$_{min=?}$ [F crashed]', fontsize=18)
	# plt.title('Safety property')

	plt.subplots_adjust(right=0.95, top=0.95, left=0.17, bottom=0.12)
	plt.show()


def analysis(p):
	data = {}

	os.chdir("%s/"%p)
	for file in glob.glob("*.csv"):
		v = int(str(file).split('_')[1])

		min_T = 34
		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if 'Pmax=? [ F (x=500 & t < ' in row["property"] and float(row["probability"]) > 0:
					T = int(row["property"][24:26])
					min_T = min(min_T, T)

		if v in data.keys():
			data[v].append(min_T)
		else:
			data[v] = [min_T]

	x = []
	y = []
	ret_d = {}

	for k in data.keys():
		x.append(k)
		y.append(np.floor(np.mean(data[k])))
		ret_d[k] = np.floor(np.mean(data[k]))

	return ret_d


def liveness_box_plot(T, p):
	decision_dict = analysis(p)

	props_dict = [{},{},{}]

	for file in glob.glob("*.csv"):
		v = int(str(file).split('_')[1])
		if not (T >= decision_dict[v] and T <= decision_dict[v] + 3):
			continue

		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)

			pmin = [0,0,0]

			for row in reader:
				if 'Pmin=? [ F crashed ]' in row["property"]:
					pmin[int(row["type_driver"])-1] = float(row["probability"])

				if pmin[int(row["type_driver"])-1] == 1:
					continue

				if row["probability"] != "inf" and 'Pmax=? [ F (x=500 & t < ' in row["property"] and row["property"] in props_dict[int(row["type_driver"])-1].keys():
					props_dict[int(row["type_driver"])-1][row["property"]].append(float(row["probability"])/(1-pmin[int(row["type_driver"])-1]))
				elif row["probability"] != "inf" and 'Pmax=? [ F (x=500 & t < ' in row["property"]:
					props_dict[int(row["type_driver"])-1][row["property"]] = [float(row["probability"])/(1-pmin[int(row["type_driver"])-1])]

	ts = [[],[],[]]
	time_val = T
	# Conditional properties
	# ts[0] = props_dict[0]['P=? [F ((x = 500) & (t < %d)) || F (x = 500)]'%time_val]
	# ts[1] = props_dict[1]['P=? [F ((x = 500) & (t < %d)) || F (x = 500)]'%time_val]
	# ts[2] = props_dict[2]['P=? [F ((x = 500) & (t < %d)) || F (x = 500)]'%time_val]

	# Unconditional properties
	ts[0] = props_dict[0]['Pmax=? [ F (x=500 & t < %d) ]'%time_val]
	ts[1] = props_dict[1]['Pmax=? [ F (x=500 & t < %d) ]'%time_val]
	ts[2] = props_dict[2]['Pmax=? [ F (x=500 & t < %d) ]'%time_val]

	plt.boxplot(ts, labels=["Aggressive", "Average", "Cautious"], whis=1.5)
	# plt.ylabel('P$_{=?}$ [F ((x = 500) \& (t $<$ %d)) $||$ F (x = 500)]'%time_val)
	plt.ylabel('$\zeta(%d)$'%time_val, fontsize=18)
	# plt.title('Liveness property')
	plt.ylim(-0.05,1.05)

	plt.subplots_adjust(right=0.95, top=0.95, left=0.17, bottom=0.12)
	plt.show()


safety_plots('plot1', 20, 35)
# safety_plots('plot2', 22, 40)
# safety_3D_plots('plot3')
# liveness_2D_plot('plot4', 21, 19, 70)
# liveness_2D_plot('plot4', 26, 22, 45)
# generate_samples(40, path="box_plots")
# generate_samples_box_plots(35)
# safety_box_plot("box_plots")
# liveness_box_plot(21, "box_plots")
# liveness_box_plot(22, "box_plots")

