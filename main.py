"""
Flappy Bird

© .GEARS Studios 2013
Port made by Gavin P
"""

# Importing libraries
import pygame as pyg
import random
from os import path
from assets import *

# Setting up the window
pyg.init()
screenw, screenh = 288, 512
running = True
screen = pyg.display.set_mode((screenw,screenh))
pyg.display.set_caption("Flappy Bird")
fps = 60

# Class for the bird that the player controls
class Bird:
	def __init__(self, starting_x, starting_y, images):
		self.x = self.starting_x = starting_x
		self.y = self.starting_y = starting_y
		self.images = images
		self.selected_images = self.select_images()
		self.selected_image_rotation = [0, 1, 2, 1]
		self.gravity = 5
		self.dead = False
		self.score = 0
		self.updates_since_death = 0
		
	def select_images(self): # Returns a random list of images from self.images to be displayed
		return random.choice(self.images)
		
	def jump(self): # Activates by pressing the space bar or up arrow key
		self.gravity = -5
		wing_sound.play()
		
	def update(self): # Checking for player input, updating the rect, and drawing the image accordingly
		global first_input

		# Moving the wing up and down
		if updates_since_launch % 4 == 0 and not self.gravity == 5: # This will be activated every 4 frames, or 15 times a second
			self.selected_image_rotation.append(self.selected_image_rotation.pop(0))
		
		# Decreasing velocity if the gravity is not back to normal, with a higher and faster level of gravity when dead
		if not self.dead:
			if self.gravity < 5:
				self.gravity += 0.2
		else:
			if self.gravity < 7.5:
				self.gravity += 0.4
		
		if not first_input: # Won't update gravity if the player has not tapped/clicked first
			self.gravity = 0
			rotation_amount = 0
		
		self.y += self.gravity # Implementing gravity
		
		if self.y < -5: # Disallowing the player's y to go off the screen, with a little bit of wiggle room
			self.y = -5
			self.gravity = 0
		
		if self.y > screenh-144: # Disallowing the player to move through the ground and killing them if they try to do so
			self.y = screenh-144
			if not self.dead:
				hit_sound.play()
			self.dead = True
			update_high_score()
		
		# Selecting the image to be blitted
		if self.gravity >= 5:
			blitted_image = self.selected_images[2] # Selected when the bird is hitting terminal velocity
		else:
			blitted_image = self.selected_images[self.selected_image_rotation[0]]
		# Calculating the amount the sprite should be rotated based on the gravity
		if self.gravity > 0:
			rotation_amount = (-self.gravity*15)+15
		else:
			rotation_amount = 15
		
		if not first_input: # Won't rotate the sprite if the player has not tapped/clicked first
			rotation_amount = 0
		
		blitted_image = pyg.transform.rotate(blitted_image, rotation_amount) # Rotating the image to be blitted
		
		bird_rect = blitted_image.get_rect(left=self.x, top=self.y).inflate(-10, -10) # Creating a rectangle for the bird, slightly shrunken to allow for some wiggle room
		pipe_rects = [pyg.Rect(pipe, (52, 320)) for pipe in pipes] # Creating a list of rectangles for the pipes
		pipe_right_edges = list(set([pipe[0]+52 for pipe in pipes])) # Creating a list of right edges of every pipe
		
		if not self.dead:
			# Killing the bird if it hits a pipe, and playing some sound effects
			if not bird_rect.collidelist(pipe_rects) == -1: 
				self.dead = True
				update_high_score()
				hit_sound.play()
			# Incrementing the bird's score when it passes the right edge of a set of pipes
			for pipe_edge in pipe_right_edges:
				if self.x == pipe_edge:
					self.score += 1
					point_sound.play()
		else:
			self.updates_since_death += 1
		
		if self.updates_since_death == fps/4:
			die_sound.play()
		
		screen.blit(blitted_image, (self.x, self.y)) # Drawing the image to the screen

# Class for interactive menu buttons
class Button: 
	def __init__(self, x, y, texture):
		self.x = x
		self.y = y
		self.texture = texture
		self.blit_y = self.y
		self.pressed = False
	def update(self, when_clicked):
		# Gets rect from blitted surface
		self.rect = screen.blit(self.texture, (self.x, self.blit_y))

		# Moves button slightly down when pressed, and launches function when released
		if self.rect.collidepoint(pyg.mouse.get_pos()):
			if pyg.mouse.get_pressed()[0]:
				self.pressed = True
				self.blit_y = self.y + 2
			elif self.pressed == True:
				self.pressed = False
				when_clicked()
				self.blit_y = self.y
				swoosh_sound.play()
		else:
			self.blit_y = self.y

def create_new_pipe(): # A function that adds a new set of pipes to the pipe list when called
	bottom_pipe_position = random.randrange(24+pipe_vertical_spacing, screenh-168)
	pipes.extend([
	[screenw+pipe_horizontal_spacing, bottom_pipe_position], 
	[screenw+pipe_horizontal_spacing, bottom_pipe_position-320-pipe_vertical_spacing]])

def score_text_surface(spritesheet, score, regular_width, one_width, height): # A function that inputs a number, a spritesheet, and various other values, and outputs a surface to be rendered to the screen
	score_digits = [int(digit) for digit in str(score)]
	score_surface = pyg.Surface((len(score_digits)*regular_width, height), pyg.SRCALPHA)
	
	score_blit_x = 0
	
	for digit in score_digits:
		score_surface.blit(spritesheet[digit], (score_blit_x, 0))
		if digit == 1:
			score_blit_x += one_width
		else:
			score_blit_x += regular_width
	
	# Cropping the score surface so it can be properly centered
	blitted_score_surface = pyg.Surface((score_surface.get_bounding_rect().width, height), pyg.SRCALPHA)
	blitted_score_surface.blit(score_surface, (0, 0))
	
	return blitted_score_surface

try:
	with open(path.join("save", "highscore"), "r") as file:
		high_score = int(file.read())
except:
	high_score = 0

pipe_vertical_spacing = 100 # The amount of pixels between the top pipes and the bottom pipes
pipe_horizontal_spacing = 100 # The amount of pixels between each set of pipes

play_fade_up = True # Whether we should fade to black or from black
play_fill_opacity = 0

play_button = Button(screenw/2-52, 300, play_button_image)

# Everything below this point should be reset when a new attempt is made
def start_game():
	global main_bird, ground_x, death_fill_opacity, play_fill_opacity, updates_since_launch, background, pipe_image, pipe_image_flipped, pipes, play_fade, first_input
	main_bird = Bird(70, screenh/2-12, [bird_yellow, bird_red, bird_blue]) # Creating the main bird, setting its starting position, and passing in it's selectable textures

	ground_x = 0

	death_fill_opacity = 255

	play_fade = True
	first_input = False

	updates_since_launch = 0 # A counter that increments every time pyg.display.update() is called

	background = random.choice(backgrounds) # Selects a random background

	pipe_image = random.choice(pipe_spritesheet) # Randomly selects one of the pipe textures to be used
	pipe_image_flipped = pyg.transform.flip(pipe_image, False, True) # Creates flipped versions of the randomly selected pipe textures

	pipes = [] # A list containing the positions of every pipe in the game
start_game()

play_fade = False # Whether the fade to and from black should be played

# To pass into the button as the function to run
def reset_game():
	global play_fade, play_fill_opacity
	play_fade = True
	play_fill_opacity = 0

def update_high_score():
	global main_bird, high_score
	if main_bird.score > high_score:
		high_score = main_bird.score
		with open(path.join("save", "highscore"), "w") as file:
			file.write(str(high_score))

# Main loop
while running:
	pyg.time.Clock().tick(fps) # Starting the clock
	# Event detection
	for event in pyg.event.get():
		if event.type == pyg.QUIT:
			running = False
		if event.type == pyg.KEYDOWN:
			if event.key == pyg.K_SPACE or event.key == pyg.K_UP: # Making the player jump when the space bar or up arrow key is pressed, if they aren't dead
				if not main_bird.dead:
					main_bird.jump()
					first_input = True
			if event.key == pyg.K_g:
				# Secret code ;)
				pyg.display.set_icon(secret_icon)
				pyg.display.set_caption("Made by Gavin P")
		if event.type == pyg.KEYUP:
			if event.key == pyg.K_g:
				pyg.display.set_icon(icon)
				pyg.display.set_caption("Flappy Bird")
		if event.type == pyg.MOUSEBUTTONDOWN:
			if event.button == 1 and not main_bird.dead:
				main_bird.jump()
				first_input = True
	screen.fill("black") # Filling the screen
	
	screen.blit(background, (0, 0)) # Rendering the background
	
	if not pipes or max([pipe[0] for pipe in pipes]) < screenw-52:
		# Creating a new pipe if no pipes are present or none of the pipes are off the right side of the screen
		create_new_pipe()
	
	for pipe in pipes[:]: # Thanks so much user16038533 on StackOverflow for helping me with this! You'll probably never see this but just know you helped a lot :)
		if pipe[0] < -52: # Removes any pipes that are completely off the left side of the screen
			pipes.remove(pipe)
		else:
			if not main_bird.dead and first_input:
				pipe[0] -= 2 # Moving the pipes 2 pixels every frame
			if pipes.index(pipe) % 2: # Rendering every odd pipe normally, and every even pipe flipped
				screen.blit(pipe_image_flipped, pipe)
			else:
				screen.blit(pipe_image, pipe)
	
	screen.blit(ground, (ground_x, screenh-112)) # Rendering the ground
	
	# Scrolling the ground
	if not main_bird.dead:
		if ground_x > -48:
			ground_x -= 2
		else:
			ground_x = 0
	
	main_bird.update() # Updating the bird

	# Rendering the big score
	if not main_bird.dead:
		big_score_surface = score_text_surface(big_score_text, main_bird.score, 24, 16, 36)
		screen.blit(big_score_surface, (screenw/2-big_score_surface.get_width()/2, 24))
	
	# Rendering the get ready screen
	if not first_input:
		screen.blit(get_ready, (screenw/2-get_ready.get_width()/2, screenh/2-get_ready.get_height()/2))
	
	# Rendering the "game over" text and playing a swoosh sound effect
	if main_bird.updates_since_death >= fps*(3/4):
		screen.blit(game_over, (screenw/2-96, 100))
		if main_bird.updates_since_death == fps*(3/4):
			swoosh_sound.play()
	
	if main_bird.updates_since_death >= fps*(6/4):
		# Rendering the results sheet and playing a swoosh sound effect
		screen.blit(results_sheet, (screenw/2-113, 175))
		if main_bird.updates_since_death == fps*(8/4):
			swoosh_sound.play()
		# Rendering the small score text
		if main_bird.updates_since_death == fps*(6/4):
			small_score = 0
		small_score += 1
		if small_score > main_bird.score:
			small_score = main_bird.score
		small_score_surface = score_text_surface(small_score_text, small_score, 16, 12, 20)
		screen.blit(small_score_surface, (screenw/2+91-small_score_surface.get_width(), 209))
		# Rendering the small high score text
		small_high_score_surface = score_text_surface(small_score_text, high_score, 16, 12, 20)
		screen.blit(small_high_score_surface, (screenw/2+91-small_high_score_surface.get_width(), 250))
	
	# Rendering the medal and updating the play button
	if main_bird.updates_since_death >= fps*(8/4):
		if main_bird.score >= 10 and main_bird.score < 20:
			screen.blit(medals_spritesheet[0], (screenw/2-87, 217))
		if main_bird.score >= 20 and main_bird.score < 30:
			screen.blit(medals_spritesheet[1], (screenw/2-87, 217))
		if main_bird.score >= 30 and main_bird.score < 40:
			screen.blit(medals_spritesheet[2], (screenw/2-87, 217))
		if main_bird.score >= 40:
			screen.blit(medals_spritesheet[3], (screenw/2-87, 217))
		play_button.update(reset_game)
	
	if main_bird.dead: # Fading out the screen white when the player dies
		fill_surface = pyg.Surface((screenw, screenh), pyg.SRCALPHA)
		fill_surface.fill((255, 255, 255, death_fill_opacity))
		screen.blit(fill_surface, (0, 0))
		death_fill_opacity -= 16
		if death_fill_opacity < 0:
			death_fill_opacity = 0

	if play_fade: # Fading in and out the screen black when the game is played
		fill_surface = pyg.Surface((screenw, screenh), pyg.SRCALPHA)
		fill_surface.fill((0, 0, 0, play_fill_opacity))
		screen.blit(fill_surface, (0, 0))
		if play_fade_up:
			play_fill_opacity += 8
		else:
			play_fill_opacity -= 8
		if play_fill_opacity > 255:
			play_fill_opacity = 255
			play_fade_up = False
			start_game()
		if play_fill_opacity < 0:
			play_fill_opacity = 0
			play_fade = False
			play_fade_up = True
	
	updates_since_launch += 1

	pyg.display.update() # Updating the screen

pyg.quit()
quit()