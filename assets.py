import pygame as pyg
from os import path

pyg.init()
pyg.display.set_mode((1, 1)) # Dummy window for using convert functions

# Spritesheet function
def make_spritesheet(image, cols, rows):
	totalCellCount = cols * rows
	
	rect = image.get_rect()
	w = int(rect.width / cols)
	h = int(rect.height / rows)
	
	cell_rects = list([pyg.Rect(index % cols * w, int(index // cols) * h, w, h) for index in range(totalCellCount)])
	
	cells = []
	
	for cell_rect in cell_rects:
		cell_surface = pyg.Surface((cell_rect.width, cell_rect.height), pyg.SRCALPHA)
		cell_surface.blit(image, (-cell_rect.x, -cell_rect.y))
		cells.append(cell_surface)
	
	return cells

def scale2x_no_smoothing(image_name, alpha=False): # A function that returns the image scaled 2x, but without smoothing unlike the builtin pygame function scale2x
	image = pyg.image.load(path.join("images", image_name))
	output = pyg.transform.scale(image, (image.get_width()*2, image.get_height()*2))
	if alpha:
		return output.convert_alpha()
	else:
		return output.convert()
	
# Importing and organizing images
background_day = scale2x_no_smoothing("background_day.png")
background_night = scale2x_no_smoothing("background_night.png")
backgrounds = [background_day, background_night]

bird_spritesheet_image = scale2x_no_smoothing("bird.png", alpha=True)
bird_spritesheet = make_spritesheet(bird_spritesheet_image, 3, 3)

bird_yellow = bird_spritesheet[:3]
bird_red = bird_spritesheet[3:6]
bird_blue = bird_spritesheet[6:]

ground = scale2x_no_smoothing("ground.png")

pipe_spritesheet_image = scale2x_no_smoothing("pipe.png", alpha=True)
pipe_spritesheet = make_spritesheet(pipe_spritesheet_image, 2, 1)

big_score_text_image = scale2x_no_smoothing("big_score_text.png", alpha=True)
big_score_text = make_spritesheet(big_score_text_image, 10, 1)

small_score_text_image = scale2x_no_smoothing("small_score_text.png", alpha=True)
small_score_text = make_spritesheet(small_score_text_image, 10, 1)

game_over = scale2x_no_smoothing("game_over.png", alpha=True)

results_sheet = scale2x_no_smoothing("results_sheet.png", alpha=True)

get_ready = scale2x_no_smoothing("get_ready.png", alpha=True)

medals_spritesheet_image = scale2x_no_smoothing("medals.png", alpha=True)
medals_spritesheet = make_spritesheet(medals_spritesheet_image, 4, 1)

play_button_image = scale2x_no_smoothing("play_button.png", alpha=True)

# Setting the window icon
icon = pyg.image.load(path.join("images", "icon.png")).convert_alpha()
secret_icon = pyg.image.load(path.join("images", "secret_icon.png")).convert() # Secret code ;)
pyg.display.set_icon(icon)

# Importing sounds
die_sound = pyg.mixer.Sound(path.join("sounds", "die.ogg"))
hit_sound = pyg.mixer.Sound(path.join("sounds", "hit.ogg"))
point_sound = pyg.mixer.Sound(path.join("sounds", "point.ogg"))
swoosh_sound = pyg.mixer.Sound(path.join("sounds", "swoosh.ogg"))
wing_sound = pyg.mixer.Sound(path.join("sounds", "wing.ogg"))

if __name__ == "__main__":
	print("Incorrect script, please run main.py")