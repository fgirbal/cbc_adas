import os, random

f = open('test_cases.csv', 'w')
f.write("d_type,v,v1,x1_0\n")

N = 10

for i in range(0,N):
	while True:
		d_type = random.randint(1,3)
		v = random.randint(15,34)
		v1 = random.randint(15,34)
		x1_0 = random.randint(30,85)

		if v >= v1:
			break

	f.write("%d,%d,%d,%d\n"%(d_type,v,v1,x1_0))

f.close()