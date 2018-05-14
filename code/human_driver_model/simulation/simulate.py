# SIMULATE - Transform a modified trace file into a visual
# simulation of the car.

# Author: Francisco Girbal Eiras, MSc Computer Science
# University of Oxford, Department of Computer Science
# Email: francisco.eiras@cs.ox.ac.uk
# 12-May-2018; Last revision: 14-May-2018

import pygame
import os, csv

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

pygame.init()
pygame.display.set_caption('Simulation')
screen = pygame.display.set_mode((1000,400))
myfont = pygame.font.SysFont("monospace", 15)

csvfile = open('trace.csv')
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
x0 = 50
v0 = 20

t = 0
deltaT = 0.1
scaleX = 2
scaleY = 5
c_height = 9
c_width = 20

x = x_init
y = y_init

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()

	screen.fill((255,255,255))
	screen.blit(get_image('background.png'), (0, 0))
	# Main vehicle
	if t <= t_end:
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

	if crashed == True:
		label = myfont.render("Crashed!", 1, (0,0,0))
		screen.blit(label, (25, 25))

	screen.blit(get_image('car_red.png'), (x*scaleX - c_width/2, 218 - y*scaleY - c_height/2))

	# Other vehicle
	screen.blit(get_image('car_grey.png'), ((x0 + t*v0)*scaleX - c_width/2, 218 - 1.8*scaleY - c_height/2))
	t = t + deltaT

	pygame.display.flip()
	pygame.time.wait(int(1000*deltaT))

# Static screen
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()

	screen.fill((255,255,255))
	screen.blit(get_image('background.png'), (0, 0))

	if crashed == True:
		label = myfont.render("Crashed!", 1, (0,0,0))
		screen.blit(label, (25, 25))

	screen.blit(get_image('car_red.png'), (x*scaleX - c_width/2, 218 - y*scaleY - c_height/2))

	screen.blit(get_image('car_grey.png'), ((x0 + t*v0)*scaleX - c_width/2, 218 - 1.8*scaleY - c_height/2))

	pygame.display.flip()
	pygame.time.wait(100)
