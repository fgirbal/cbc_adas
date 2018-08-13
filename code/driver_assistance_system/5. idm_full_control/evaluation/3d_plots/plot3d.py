# PLOT3D - Generate the 3D safety plots for aggressive, average
# and cautious drivers.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 11-Aug-2018; Last revision: 11-Aug-2018

import sys, os, random, glob, csv, subprocess, itertools
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib as mpl

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=13)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def safety_3D_plots(p_adas, p_human, driver_type):

	x = [[],[]];
	y = [[],[]];
	z = [[],[]];

	os.chdir("%s/"%p_human)
	for file in glob.glob("*.csv"):
		x[0].append(int(str(file).split('_')[1]))
		y[0].append(int(str(file).split('_')[2]))

		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if row["property"] == 'P=? [F crashed]' and row["type_driver"] == str(driver_type):
					z[0].append(float(row["probability"]))

	os.chdir("../%s/"%p_adas)
	for file in glob.glob("*.csv"):
		x[1].append(int(str(file).split('_')[1]))
		y[1].append(int(str(file).split('_')[2]))

		with open(file) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				if row["property"] == 'Pmin=? [ F crashed ]' and row["type_driver"] == str(driver_type):
					z[1].append(float(row["probability"]))


	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	cmap = plt.get_cmap('Blues')
	new_blues = truncate_colormap(cmap, 0.3, 0.9)

	cmap = plt.get_cmap('Reds')
	new_reds = truncate_colormap(cmap, 0.3, 0.9)

	line = ax.plot_trisurf(x[0], y[0], z[0], label="Human", linewidth=0.2, antialiased=True, cmap=new_reds)
	line = ax.plot_trisurf(x[1], y[1], z[1], label="ADAS", linewidth=0.2, antialiased=True, cmap=new_blues)
	
	ax.xaxis._axinfo['label']['space_factor'] = 3.0
	ax.yaxis._axinfo['label']['space_factor'] = 3.0
	ax.zaxis._axinfo['label']['space_factor'] = 3.0

	ax.set_xlabel('v [m/s]')
	ax.set_ylabel('v$_1$ [m/s]')
	ax.set_zlabel('P$_{=?}$ [F crashed] or P$_{min=?}$ [F crashed]')

	fake2Dline1 = mpl.lines.Line2D([0],[0], linestyle="none", c='red', marker = 'o')
	fake2Dline2 = mpl.lines.Line2D([0],[0], linestyle="none", c='steelblue', marker = 'o')
	ax.legend([fake2Dline1, fake2Dline2], ['Human Driver', 'ADAS'], numpoints = 1)

	# ax.set_zticks(np.arange(np.min(z)+0.1, np.max(z), 0.1))
	plt.show()


safety_3D_plots('adas', 'human', 3)

