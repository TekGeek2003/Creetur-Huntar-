from settings import *
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame

# import functions
def import_image(*path, alpha = True, format = 'png'):
	full_path = join(*path) + f'.{format}'
	surf = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
	return surf

def import_folder(*path):
	frames = []
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames.append(surf)
	return frames

def import_folder_dict(*path):
	frames = {}
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image_name in image_names:
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames[image_name.split('.')[0]] = surf
	return frames

def import_sub_folders(*path):
	frames = {}
	for _, sub_folders, __ in walk(join(*path)):
		if sub_folders:
			for sub_folder in sub_folders:
				frames[sub_folder] = import_folder(*path, sub_folder)
	return frames

def import_tilemap(cols, rows, *path):
	frames = {}
	surf = import_image(*path)
	# use ints for cell sixe and an SRCALPHA surface for each tile so alpha is preserved
	cell_width, cell_height = int(surf.get_width() / cols), int(surf.get_height() / rows)
	for col in range(cols):
		for row in range(rows):
			cut = pygame.Surface((cell_width, cell_height), pygame.SRCALPHA)
			# blit the tile area into SRCALPHA
			cut.blit(surf, ( -col * cell_width, -row * cell_height ))
			frames[(col, row)] = cut.convert_alpha()
	return frames

def character_importer(cols, rows, *path):
	frame_dict = import_tilemap(cols, rows, *path)
	new_dict = {}
	for row, direction in enumerate(('down', 'left', 'right', 'up')):
		new_dict[direction] = [frame_dict[(col, row)] for col in range(cols)]
		new_dict[f'{direction}_idle'] = [frame_dict[0, row]]
	return new_dict

def all_character_import(*path):
	new_dict = {}
	for _, __, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			new_dict[image_name] = character_importer(4,4,*path, image_name)
		return new_dict

def coast_importer(cols, rows, *path):
	frame_dict = import_tilemap(cols, rows, *path)
	new_dict = {}
	terrains = ['grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i']
	sides = {
		'topleft': (0,0), 'top': (1,0), 'topright': (2,0), 
		'left': (0,1), 'right':(2,1), 'bottomleft': (0,2),
		'bottom': (1,2), 'bottomright': (2,2)}
	for index, terrain in enumerate(terrains):
		new_dict[terrain] = {}
		for key, pos in sides.items():
			new_dict[terrain][key] = [frame_dict[(pos[0] + index * 3, pos[1] + row)] for row in range(0,rows, 3)]
	return new_dict

def tmx_importer(*path):
	tmx_dict = {}
	for folder_path, sub_folders, file_names in walk(join(*path)):
		for file in file_names:
			tmx_dict[file.split('.')[0]] = load_pygame(join(folder_path, file))
	return tmx_dict

def monster_importer(cols, rows, *path):
	monster_dict = {}
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			monster_dict[image_name] = {}
			frame_dict = import_tilemap(cols, rows, *path, image_name)
			for row, key in enumerate(('idle', 'attack')):
				monster_dict[image_name][key] = [frame_dict[(col,row)] for col in range(cols)]
	return monster_dict	

# Creates the selector for the current monster when it get's enough XP
def outline_creator(frame_dict, padding=4):
	outline_data = {}

	for monster, monster_frames in frame_dict.items():
		outline_data[monster] = {}

		for state, frames in monster_frames.items():
			outline_data[monster][state] = []

			for frame in frames:
				w, h = frame.get_size()
				surf = pygame.Surface(
					(w + padding * 2, h + padding * 2),
					pygame.SRCALPHA
				)
				# kepp the squal black
				surf.fill((0, 0, 0, 0))

				# ensure a surface with per-pixel alpha so for mask.from_surface()
				try:
					frame_alpha = frame.convert_alpha()
				except Exception:
					frame_alpha = pygame.Surface(frame_size(), pygame.SRCALPHA)
					frame_alpha.blit(frame, (0, 0))

				mask = pygame.mask.from_surface(frame_alpha)

				# silhouette
				silhouette = mask.to_surface(
					setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)).convert_alpha()

				# Blit silhouette around the sprite to create a filled white shape,
				for x in range(-padding, padding + 1):
					for y in range(-padding, padding + 1):
						surf.blit(silhouette, (padding + x, padding + y))

				# Original sprite on top (centered with padding)
				surf.blit(frame, (padding, padding))

				# append the finished outline once
				outline_data[monster][state].append(surf)

	return outline_data

def attack_importer(*path):
	attack_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			attack_dict[image_name] = list(import_tilemap(4,1,folder_path, image_name).values())
	return attack_dict

def audio_importer(*path):
	files = {}
	for folder_path, _, file_names in walk(join(*path)):
		for file_name in file_names:
			full_path = join(folder_path, file_name)
			files[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
	return files

# game functions
def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
	if max_value <= 0:
		ratio = 0.0
	else:
		ratio = max(0.0, min(1.0, float(value) / float(max_value)))

	bg_rect = rect.copy()
	progress = rect.width * ratio
	progress_rect = pygame.FRect(rect.topleft, (progress, rect.height))

	pygame.draw.rect(surface, bg_color, bg_rect, 0, radius)
	if progress_rect.width > 0:
		pygame.draw.rect(surface, color, progress_rect, 0, radius)
	
def check_connections(radius, entity, target, tolerance = 30):
	relation = vector(target.rect.center) - vector(entity.rect.center)
	if relation.length() < radius:
		if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolerance or\
			entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolerance or\
			entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolerance or\
			entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolerance:
			 return True