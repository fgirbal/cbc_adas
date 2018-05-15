# SIMULATE - Given a PRISM model, obtain a sample 
# trace using get_trace.py and simulate it.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 12-May-2018; Last revision: 15-May-2018

import pygame
import sys, os, csv, argparse, subprocess

parser=argparse.ArgumentParser(
    description='''Given a PRISM model, obtain a sample trace using get_trace.py and simulate it.''')
parser.add_argument('model.pm', type=str, help='The model from which to obtain the sample execution (built using model_generator.py).')
parser.add_argument('-x [VALUE]', type=str, help='Execution is [VALUE] times faster.')
args=parser.parse_args()

# Helper functions
_image_library = {}
def get_image(path):
	global _image_library
	image = _image_library.get(path)
	if image == None:
			canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
			image = pygame.image.load('graphics/' + canonicalized_path)
			if path == "background.png":
				image = pygame.transform.scale(image, (1000,400))
			if path == "car_red.png" or path == "car_grey.png":
				image = pygame.transform.scale(image, (20,11))
			_image_library[path] = image
	return image

def render_centered(screen, text, color):
	label = crashed_font.render(text, 1, color)
	size = crashed_font.size(text)
	screen.blit(label, (500 - size[0]/2.0, 200 - size[1]/2.0))

# Main code

if len(sys.argv) > 3:
	speed = float(sys.argv[3])
else:
	speed = 1

v1 = -1
x1_0 = -1

f = open(sys.argv[1], 'r')

for line in f:
	if "const int v1" in line:
		nums = line.split()
		v1 = int(nums[4][:-1])
	elif "const int x1_0" in line:
		nums = line.split()
		x1_0 = int(nums[4][:-1])
		break

if v1 == -1 or x1_0 == -1:
	print("Error: model not generated using the model_generator.py (problems reading v1 and x1_0)")
	quit()

f.close()

# Generate the trace
subprocess.run("python3 get_trace.py %s %d %d"%(sys.argv[1], v1, x1_0), shell=True)

pygame.init()
pygame.display.set_caption('Sample Path Simulation')
screen = pygame.display.set_mode((1000,400))
myfont = pygame.font.SysFont("monospaced", 20)
crashed_font = pygame.font.SysFont("monospaced", 45)
time_font = pygame.font.SysFont("monospaced", 60)

csvfile = open('gen_trace.csv')
reader = csv.DictReader(csvfile)
comm = next(reader)

# Read the first command
t_init = 0
x_init = 0
y_init = 1.8
t_end = int(comm['t_end'])
type_comm = int(comm['type'])
curr_v = int(comm['v'])
crashed = bool(int(comm['crashed']))
x_coeffs = [float(comm['x_t_1']), float(comm['x_t_2']), float(comm['x_t_3'])]
y_coeffs = [float(comm['y_t_1']), float(comm['y_t_2']), float(comm['y_t_3']), float(comm['y_t_4']), float(comm['y_t_5']), float(comm['y_t_6']), float(comm['y_t_7'])]

# Setup of the other variables
x0 = x1_0
v0 = v1

t = 0.0
deltaT = 0.05
scaleX = 2
scaleY = 5
c_height = 9
c_width = 20

x = x_init
y = y_init

update_action = False
permanent = False

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			update_action = not update_action

	screen.fill((255,255,255))
	screen.blit(get_image('background.png'), (0, 0))

	screen.blit(get_image('car_red.png'), (x*scaleX - c_width/2, 218 - y*scaleY - c_height/2))

	# Other vehicle
	screen.blit(get_image('car_grey.png'), ((x0 + t*v0)*scaleX - c_width/2, 218 - 1.8*scaleY - c_height/2))

	# Display info
	time_label = time_font.render("%2.1fs"%t, 1, (0,0,0))
	screen.blit(time_label, (175, 35))

	main_vahicle_label = myfont.render("Main vehicle", 1, (128,128,128))
	screen.blit(main_vahicle_label, (325, 25))

	x_label = myfont.render("x Position: %dm"%x, 1, (0,0,0))
	screen.blit(x_label, (325, 45))

	y_label = myfont.render("y Position: %.2fm"%y, 1, (0,0,0))
	screen.blit(y_label, (325, 65))

	other_vahicle_label = myfont.render("Other vehicle", 1, (128,128,128))
	screen.blit(other_vahicle_label, (475, 25))

	x_label = myfont.render("x Position: %dm"%(x0 + t*v0), 1, (0,0,0))
	screen.blit(x_label, (475, 45))

	y_label = myfont.render("y Position: 1.8m", 1, (0,0,0))
	screen.blit(y_label, (475, 65))

	if crashed == True:
		render_centered(screen, "Crashed", (0,0,0))
		permanent = True

	# Main vehicle
	if update_action == True and permanent == False:
		if t < t_end:
			if type_comm == 1:
				x = x + curr_v*deltaT
			elif type_comm == 2:
				curr_t = t - t_init
				x = x_init + (x_coeffs[0]*curr_t**2 + x_coeffs[1]*curr_t + x_coeffs[2])
				y = (y_coeffs[0]*curr_t**6 + y_coeffs[1]*curr_t**5 + y_coeffs[2]*curr_t**4 + y_coeffs[3]*curr_t**3 + y_coeffs[4]*curr_t**2 + y_coeffs[5]*curr_t + y_coeffs[6])

		if t >= t_end:
			try:
				comm = next(reader)
			except:
				print('Done')
				break

			# Read the next command
			t_init = t
			x_init = x
			y_init = y
			t_end = int(comm['t_end'])
			type_comm = int(comm['type'])
			curr_v = int(comm['v'])
			crashed = bool(int(comm['crashed']))
			x_coeffs = [float(comm['x_t_1']), float(comm['x_t_2']), float(comm['x_t_3'])]
			y_coeffs = [float(comm['y_t_1']), float(comm['y_t_2']), float(comm['y_t_3']), float(comm['y_t_4']), float(comm['y_t_5']), float(comm['y_t_6']), float(comm['y_t_7'])]

		if x >= 500 or t >= 30:
			update_action = False
			permanent = True

		t = t + deltaT
	elif crashed == False and update_action == False and permanent == False:
		if x == 0:
			render_centered(screen, "Press SPACE to start", (0,0,0))
		else:
			render_centered(screen, "Press SPACE to continue", (0,0,0))
	elif crashed == False and permanent == True:
		render_centered(screen, "Done", (0,0,0))

	pygame.display.flip()
	pygame.time.wait(int(1000*deltaT/speed))

pygame.quit()