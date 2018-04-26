# AUTOMATIC_MODEL_CHECKER - Executes the script model_generator.py 
# for some given parameters in order to build the model and perform
# model checking subquentially.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 26-Apr-2018; Last revision: 26-Apr-2018

import os, subprocess

driver_type = 1
v = 31
v1 = 30
x1_0 = 15
filename = "gen_model_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)
r_filename = "results_%s_%s_%s_%s"%(driver_type,v,v1,x1_0)

# Construct the file
print('Generating the model...')
os.system('python3 model_generator.py model_tables/control_table.csv model_tables/dm_table.csv %s %s %s %s --filename results/%s > /dev/null'%(driver_type,v,v1,x1_0,filename))

print('Building the model and performing model checking...')
#os.system('prism results/%s.pm properties.pctl -exportresults results/%s.txt'%(filename, r_filename))
subprocess.run("prism results/%s.pm properties.pctl -exportresults results/%s.txt"%(filename, r_filename), shell=True)


print('Obtaining the results...')

print('Cleaning up...')

os.system('rm results/%s.pm'%filename)

print('Done.')