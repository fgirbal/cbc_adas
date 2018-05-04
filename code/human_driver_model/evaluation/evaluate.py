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
generate_samples = False

if generate_samples == True:
	for i in range(1,N+1):

		while 1:
			v1 = random.randint(15,34)
			v = v1 + random.randint(0,34-v1)
			x1_0 = random.randint(10,80)

			if not os.path.exists("gen_files/r_%s_%s_%s.csv"%(v,v1,x1_0)):
				break

		print('[%d/%d]: Evaluating drivers for v = %d, v1 = %d, x1_0 = %d...'%(i,N,v,v1,x1_0))
		os.system('python3 automatic_model_checker.py properties.pctl %d %d %d > /dev/null'%(v,v1,x1_0))

props_dict = [{},{},{}]

os.chdir("gen_files/")
for file in glob.glob("*.csv"):
    with open(file) as csvfile:
    	reader = csv.DictReader(csvfile)
    	for row in reader:
    		if row["property"] in props_dict[int(row["type_driver"])-1].keys():
    			props_dict[int(row["type_driver"])-1][row["property"]].append(float(row["probability"]))
    		else:
    			props_dict[int(row["type_driver"])-1][row["property"]] = [float(row["probability"])]

vals = [[],[],[]]
vals[0] = props_dict[0]['P=? [ F crashed ]']
vals[1] = props_dict[1]['P=? [ F crashed ]']
vals[2] = props_dict[2]['P=? [ F crashed ]']
fv = [[],[],[]]

ts = [[],[],[]]
time_val = 17
ts[0] = props_dict[0]['P=? [ F crashed | (x=length & t < %d) ]'%time_val]
ts[1] = props_dict[1]['P=? [ F crashed | (x=length & t < %d) ]'%time_val]
ts[2] = props_dict[2]['P=? [ F crashed | (x=length & t < %d) ]'%time_val]
ft = [[],[],[]]

for i in range(0,len(vals[0])):
	if vals[0][i] != 1 or vals[1][i] != 1 or vals[2][i] != 1:
		fv[0].append(vals[0][i])
		fv[1].append(vals[1][i])
		fv[2].append(vals[2][i])

for i in range(0,len(vals[0])):
	if (vals[0][i] != 0 or vals[1][i] != 0 or vals[2][i] != 0) and (vals[0][i] != 1 or vals[1][i] != 1 or vals[2][i] != 1):
		ft[0].append(ts[0][i])
		ft[1].append(ts[1][i])
		ft[2].append(ts[2][i])

plt.figure(1)
plt.boxplot(fv, labels=["Aggressive", "Average", "Cautious"], whis=1.5)
plt.ylabel('P=? [ F crashed ]')
plt.title('Safety property')
plt.show()

plt.figure(2)
plt.boxplot(ft, labels=["Aggressive", "Average", "Cautious"], whis=1.5)
plt.ylabel('P=? [ F crashed | (x=length & t < %d) ]'%time_val)
plt.title('Liveness property')
plt.show()

print('Done.')







