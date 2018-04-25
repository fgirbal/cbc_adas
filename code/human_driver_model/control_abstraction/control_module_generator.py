# CONTROL_MODULE_GENERATOR - Tranform a generated table using
# generator.m into a PRISM file with the module

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 24-Apr-2018; Last revision: 24-Apr-2018

import sys, csv

if len(sys.argv) < 2:
	print("Too few arguments. Usage: python3 control_module_generator.py [file_name].")
	exit()

f = open("generated.pm", "w")

# Write the beginning of the file
f.write("dtmc\n\n")
f.write("const int length = 500; // road length\n")
f.write("const int max_time = 30; // maximum time of experiment\n")
f.write("const int v1 = 30;\n")
f.write("const int x1_0 = 5;\n\n")
f.write("global actrState : [1..3] init 1; // active module: 1 = control (both cars), 2 = decision making, 3 = monitoring\n")
f.write("global lC : bool init false; // lane changing occuring? \n")
f.write("global t : [0..max_time] init 0; // time \n")
f.write("global crashed : bool init false; \n\n")
f.write("formula x1 = x1_0 + v1*t;\n")
f.write("formula dist = x1>x?(x1 - x):(x - x1);\n\n")

f.write("module Decision_Making\n\n 	// If a crash occurs, then nothing else can happen\n	[] crashed -> 1:(crashed' = true);\n\n	[] actrState = 2 & dist < 10 -> 1:(lC' = true) & (actrState' = 1);\n	[] actrState = 2 & dist >= 10 -> 1:(actrState' = 1);\nendmodule\n\n")

f.write("module Control\n\n")
f.write("	x : [0..length] init 0;\n")
f.write("	v : [15..34] init 29;\n")
f.write("	lane : [1..2] init 1;\n\n")

f.write("	[] actrState = 1 & !crashed & !lC & x <= length - v & t < max_time -> 1:(x' = x + v) & (t' = t + 1) & (actrState' = 2);\n\n")

with open(sys.argv[1]) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row["Acc?"] == "0":
			acc_val = "false"
		else:
			acc_val = "true"
		line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & v1 = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = %s) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["vi2"],row["delta_x1"],row["delta_t"],acc_val,row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
		f.write(line)
		line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & v1 = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = %s) & (x' = 500) & (v' = %s) & (t' = t + %s) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["vi2"],row["delta_x1"],row["delta_t"],acc_val,row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
		f.write(line)

f.write("\nendmodule")









