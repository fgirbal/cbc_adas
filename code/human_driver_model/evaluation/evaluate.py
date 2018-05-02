# EVALUATE - Evaluate the relative performance of the drivers using
# the automatic_model_checker.py script to model check desired properties.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 2-May-2018; Last revision: 2-May-2018

import sys, os, random, glob, csv
import matplotlib.pyplot as plt

# Parameters
N = 20
generate_samples = True

if generate_samples == True:
	for i in range(1,N):

		while 1:
			v = random.randint(15,34)
			v1 = random.randint(15,34)
			x1_0 = random.randint(10,120)

			if not os.path.exists("gen_files/r_%s_%s_%s.csv"%(v,v1,x1_0)) and (v - v1) > - 6:
				break

		print('[%d/%d]: Evaluating drivers for v = %d, v1 = %d, x1_0 = %d...'%(i,N,v,v1,x1_0))
		os.system('python3 automatic_model_checker.py properties.pctl %d %d %d > /dev/null'%(v,v1,x1_0))

vals = [[],[],[]]

os.chdir("gen_files/")
for file in glob.glob("*.csv"):
    with open(file) as csvfile:
    	reader = csv.DictReader(csvfile)
    	for row in reader:
    		if row["property"] == "P=? [ F crashed ]":
    			vals[int(row["type_driver"])-1].append(float(row["probability"]))

plt.boxplot(vals, labels=["Aggressive", "Average", "Cautious"], whis=1.5)
plt.show()

print('Done.')







