# MODEL_GENERATOR - Tranform the generated tables using
# generator.m and decision_making.m into a PRISM file 
# with the modules.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 24-Apr-2018; Last revision: 24-Apr-2018

import sys, csv

if len(sys.argv) < 3:
	print("Too few arguments. Usage: python3 control_module_generator.py [control_module] [decision_making_module].")
	exit()

f = open("two_component_model.pm", "w")

v1 = "30";
driver_type = "1"

# Write the beginning of the file
f.write("//Model automatically built using model_generator.py for v1 = %s and driver_type = %s (to alter this value, run the script again).\n\n"%(v1,driver_type))
f.write("dtmc\n\n")
f.write("const int length = 500; // road length\n")
f.write("const int driver_type = 1; // 1 = aggressive, 2 = average, 3 = conservative drivers\n")
f.write("const int max_time = 30; // maximum time of experiment\n")
f.write("const int v1 = %s;\n"%v1)
f.write("const int x1_0 = 5;\n\n")
f.write("global actrState : [1..2] init 1; // active module: 1 = control (both cars), 2 = decision making + monitoring\n")
f.write("global lC : bool init false; // lane changing occuring? \n")
f.write("global t : [0..max_time] init 0; // time \n")
f.write("global crashed : bool init false; \n\n")
f.write("formula x1 = x1_0 + v1*t;\n")
f.write("formula dist = x1>x?(x1 - x):(x - x1);\n\n")

# Decision making + monitoring module
f.write("module Decision_Making_Monitoring\n\n")
f.write(" 	// If a crash occurs, then nothing else can happen\n")
f.write("	[] actrState = 2 & crashed -> 1:(crashed' = true);\n\n")

with open(sys.argv[2]) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row["type"] == driver_type:
			line = "	[] actrState = 2 & !crashed & lane = 1 & dist = %s & v = %s -> %s:(actrState' = 1) & (lC' = true) + %s:(actrState' = 1) & (lC' = false);\n" % (row["d"],row["v"],row["P_lC"],row["P_nlC"])
			f.write(line)

f.write("endmodule\n\n")

# Control module
f.write("module Control\n\n")
f.write("	x : [0..length] init 0;\n")
f.write("	v : [15..34] init 29;\n")
f.write("	lane : [1..2] init 1;\n\n")

f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time -> 1:(x' = x + v) & (t' = t + 1) & (actrState' = 2);\n\n")

with open(sys.argv[1]) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row["Acc?"] == "0":
			acc_val = "false"
		else:
			acc_val = "true"

		if row["d"] != "40" and row["vi2"] == v1:
			line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = %s) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],acc_val,row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
			f.write(line)
			line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = %s) & (x' = 500) & (v' = %s) & (t' = t + %s) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],acc_val,row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
			f.write(line)
		elif row["d"] == "40" and row["vi2"] == v1:
			line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = %s) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],acc_val,row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
			f.write(line)
			line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = %s) & (x' = 500) & (v' = %s) & (t' = t + %s) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],acc_val,row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
			f.write(line)

f.write("\nendmodule")









