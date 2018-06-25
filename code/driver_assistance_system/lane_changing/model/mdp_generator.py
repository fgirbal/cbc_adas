# MDP_GENERATOR - Transform the tables into the MDP
# in order to perform multi-objective synthesis.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 6-Jun-2018; Last revision: 9-Jun-2018

import sys, csv, argparse, datetime

parser=argparse.ArgumentParser(
    description='''Transform the tables into the MDP in order to perform multi-objective synthesis.''')
parser.add_argument('lane_change_table', type=str, help='Table for the lane change part of the control module.')
parser.add_argument('acc_table', type=str, help='Table for the linear accelaration part of the control module.')
parser.add_argument('[v]', type=int, default=29, help='Initial velocity of the vehicle.')
parser.add_argument('[v1]', type=int, default=30, help='Initial velocity of the other vehicle.')
parser.add_argument('[x1_0]', type=int, default=15, help='Initial position of the other vehicle.')
parser.add_argument('--filename [NAME]', type=str, help='Output name for the file generated.')
args=parser.parse_args()

if len(sys.argv) == 6:
	f = open("mdp_model.pm", "w")
else:
	f = open("%s.pm"%sys.argv[8], "w")

v = sys.argv[3]
v1 = sys.argv[4]
x1_0 = sys.argv[5]
if not (int(v) >= 15 and int(v) <= 34) or not (int(v1) >= 15 and int(v1) <= 34) or not (int(x1_0) >= 1 and int(x1_0) <= 500):
	raise ValueError("Input out of range.")

max_control_dist = "43"
max_dm_dist = "80"
crash_dist = "6"

now = datetime.datetime.now()

# Write the beginning of the file
f.write("//MDP automatically built using mdp_generator.py for v1 = %s (to alter this value, run the script again).\n"%v1)
f.write("//Generated on %s.\n\n"%(now.strftime("%d-%m-%Y at %H:%M")))
f.write("mdp\n\n")
f.write("const int length = 500; // road length\n")
f.write("const int max_time = 30; // maximum time of experiment\n\n")
f.write("// Other vehicle\n")
f.write("const int v1 = %s; // do not alter this manually!\n"%v1)
f.write("const int x1_0 = %s;\n\n"%x1_0)
f.write("// Environment variables\n")
f.write("global t : [0..max_time] init 0; // time \n")
f.write("global crashed : bool init false; \n\n")
f.write("// Vehicle controlled\n")
f.write("global actrState : [1..2] init 1; // active module: 1 = control (both cars), 2 = decision making + monitoring\n")
f.write("global lC : bool init false; // lane changing occuring? \n")
f.write("global x : [0..length] init 0;\n")
f.write("global v : [15..34] init %s;\n"%v)
f.write("global a : [-2..3] init 0;\n")
f.write("global lane : [1..2] init 1;\n\n")
f.write("formula x1 = x1_0 + v1*t;\n")
f.write("formula dist = x1>x?(x1 - x):(x - x1);\n")
f.write("formula positiveDist = (x < length)?x > x1:true;\n\n")

# Decision making + monitoring module
f.write("module Decision_Making_Monitoring\n\n")
f.write(" 	// If a crash occurs, then nothing else can happen\n")
f.write("	//[] actrState = 2 & crashed -> 1:(crashed' = true);\n\n")

f.write(" 	// If we are in lane 2, but behind the other vehicle, don't try to pass\n")
f.write("	[] actrState = 2 & !crashed & lane = 2 & positiveDist = false & x < length -> 1:(actrState' = 1);\n\n")

f.write("	// If we are in lane 1, and no vehicle is in front, don't change lanes\n")
f.write("	[] actrState = 2 & !crashed & lane = 1 & positiveDist = true & x < length -> 1:(actrState' = 1);\n\n")
f.write("	[] actrState = 2 & !crashed & lane = 1 & positiveDist = false & x < length -> 1:(lC' = true) & (actrState' = 1);\n")
f.write("	[] actrState = 2 & !crashed & lane = 1 & positiveDist = false & x < length -> 1:(lC' = false) & (actrState' = 1);\n\n")

f.write("	[] actrState = 2 & !crashed & lane = 2 & positiveDist = true & x < length -> 1:(lC' = true) & (actrState' = 1);\n")
f.write("	[] actrState = 2 & !crashed & lane = 2 & positiveDist = true & x < length -> 1:(lC' = false) & (actrState' = 1);\n\n")

f.write("endmodule\n\n")

# Control module
f.write("module Control\n\n")

f.write(" 	// If we are in lane 1, and no lane change was decided, continue forward (which might result in crash)\n")
f.write(" 	// The vehicle is behind the other driver (positiveDist = false, x < x1)\n")
with open(sys.argv[2]) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row["d"] != max_dm_dist:
			line = "	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s & v + a < 34 & v + a > 15 & dist = %s & v = %s  -> 1:(x' = x + v) & (t' = t + 1) & (v' = v + a) & (a' = %s) & (actrState' = 2);\n" % (crash_dist,row["d"],row["v"],row["a"])
			f.write(line)
			line = "	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s & v + a >= 34 & dist = %s & v = %s -> 1:(x' = x + v) & (t' = t + 1) & (v' = 34) & (a' = %s) & (actrState' = 2);\n" % (crash_dist,row["d"],row["v"],row["a"])
			f.write(line)
			line = "	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s & v + a <= 15 & dist = %s & v = %s -> 1:(x' = x + v) & (t' = t + 1) & (v' = 15) & (a' = %s) & (actrState' = 2);\n" % (crash_dist,row["d"],row["v"],row["a"])
			f.write(line)
		elif row["d"] == max_dm_dist:
			line = "	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s & v + a < 34 & v + a > 15 & dist >= %s & v = %s  -> 1:(x' = x + v) & (t' = t + 1) & (v' = v + a) & (a' = %s) & (actrState' = 2);\n" % (crash_dist,row["d"],row["v"],row["a"])
			f.write(line)
			line = "	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s & v + a >= 34 & dist >= %s & v = %s -> 1:(x' = x + v) & (t' = t + 1) & (v' = 34) & (a' = %s) & (actrState' = 2);\n" % (crash_dist,row["d"],row["v"],row["a"])
			f.write(line)
			line = "	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s & v + a <= 15 & dist >= %s & v = %s -> 1:(x' = x + v) & (t' = t + 1) & (v' = 15) & (a' = %s) & (actrState' = 2);\n" % (crash_dist,row["d"],row["v"],row["a"])
			f.write(line)

f.write("\n	[] actrState = 1 & !crashed & !lC & lane = 1 & x > length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) >= %s -> 1:(x' = length) & (t' = t + 1) & (actrState' = 2);\n"%crash_dist)
f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x > length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) < %s -> 1:(x' = length) & (t' = t + 1) & (crashed' = true) & (actrState' = 2);\n\n"%crash_dist)

f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) < %s & v + a < 34 & v + a > 15 -> 1:(x' = x + v) & (t' = t + 1) & (v' = v + a) & (crashed' = true) & (actrState' = 2);\n"%crash_dist)
f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) < %s & v + a >= 34 -> 1:(x' = x + v) & (t' = t + 1) & (v' = 34) & (crashed' = true) & (actrState' = 2);\n"%crash_dist)
f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = false & (x1 + v1 - x - v) < %s & v + a <= 15 -> 1:(x' = x + v) & (t' = t + 1) & (v' = 15) & (crashed' = true) & (actrState' = 2);\n"%crash_dist)	

f.write(" 	// The vehicle is in front of the other driver (positiveDist = true, x > x1)\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = true & v + a < 34 & v + a > 15 -> 1:(x' = x + v) & (t' = t + 1) & (v' = v + a) & (a' = 0) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = true & v + a >= 34 -> 1:(x' = x + v) & (t' = t + 1) & (v' = 34) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x <= length - v & t < max_time & positiveDist = true & v + a <= 15 -> 1:(x' = x + v) & (t' = t + 1) & (v' = 15) & (actrState' = 2);\n\n")

f.write("	[] actrState = 1 & !crashed & !lC & lane = 1 & x > length - v & t < max_time & positiveDist = true -> 1:(x' = length) & (t' = t + 1) & (actrState' = 2);\n\n")

f.write(" 	// If we are in lane 2, and no lane change was decided, continue forward\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x <= length - v & t < max_time & v + a < 34 & v + a > 15 & positiveDist = true -> 1:(x' = x + v) & (t' = t + 1) & (v' = v + a) & (a' = 0) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x <= length - v & t < max_time & v + a >= 34 & positiveDist = true -> 1:(x' = x + v) & (t' = t + 1) & (v' = 34) & (a' = 0) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x <= length - v & t < max_time & v + a <= 15 & positiveDist = true -> 1:(x' = x + v) & (t' = t + 1) & (v' = 15) & (a' = 0) & (actrState' = 2);\n\n")

f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x <= length - v & t < max_time & v + a < 34 & v + a > 15 & positiveDist = false -> 1:(x' = x + v) & (t' = t + 1) & (v' = v + a) & (a' = 0) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x <= length - v & t < max_time & v + a >= 34 & positiveDist = false -> 1:(x' = x + v) & (t' = t + 1) & (v' = 34) & (a' = 0) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x <= length - v & t < max_time & v + a <= 15 & positiveDist = false -> 1:(x' = x + v) & (t' = t + 1) & (v' = 15) & (a' = 0) & (actrState' = 2);\n\n")

f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x > length - v & t < max_time & v + a < 34 & v + a > 15 -> 1:(x' = length) & (t' = t + 1) & (v' = v + a) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x > length - v & t < max_time & v + a >= 34 -> 1:(x' = length) & (t' = t + 1) & (v' = 34) & (actrState' = 2);\n")
f.write("	[] actrState = 1 & !crashed & !lC & lane = 2 & x > length - v & t < max_time & v + a <= 15 -> 1:(x' = length) & (t' = t + 1) & (v' = 15) & (actrState' = 2);\n\n")

with open(sys.argv[1]) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		probCrash = float(row["Acc?"])

		if probCrash != 0 and probCrash != 1:
			if row["d"] != max_control_dist and row["vi2"] == v1:
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t <= max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t <= max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = length) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t > max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["delta_x1"],row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t > max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = length) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
			elif row["d"] == max_control_dist and row["vi2"] == v1:
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t <= max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t <= max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = length) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t > max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["delta_x1"],row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t > max_time - %s -> %.2f:(crashed' = true) & (actrState' = 2) & (lC' = false) + %.2f:(crashed' = false) & (x' = length) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],probCrash,1-probCrash,row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
		elif probCrash == 0:
			if row["d"] != max_control_dist and row["vi2"] == v1:
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = false) & (x' = length) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t > max_time - %s -> 1:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["delta_x1"],row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t > max_time - %s -> 1:(crashed' = false) & (x' = length) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
			elif row["d"] == max_control_dist and row["vi2"] == v1:
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["delta_x1"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = false) & (x' = length) & (v' = %s) & (t' = t + %s) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["vf1"],row["delta_t"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t > max_time - %s -> 1:(crashed' = false) & (x' = x + %s) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["delta_x1"],row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t > max_time - %s -> 1:(crashed' = false) & (x' = length) & (v' = %s) & (t' = max_time) & (a' = 0) & (lane' = %s) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"],row["vf1"],str(3 - int(row["o_lane"])))
				f.write(line)
		else:
			if row["d"] != max_control_dist and row["vi2"] == v1:
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x <= length - %s & t > max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist = %s & v = %s & x > length - %s & t > max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
			elif row["d"] == max_control_dist and row["vi2"] == v1:
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t <= max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t <= max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x <= length - %s & t > max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)
				line = "	[] actrState = 1 & !crashed & lC & lane = %s & dist >= %s & v = %s & x > length - %s & t > max_time - %s -> 1:(crashed' = true) & (actrState' = 2) & (lC' = false);\n" % (row["o_lane"], row["d"],row["vi1"],row["delta_x1"],row["delta_t"])
				f.write(line)


f.write("\nendmodule")

f.close()