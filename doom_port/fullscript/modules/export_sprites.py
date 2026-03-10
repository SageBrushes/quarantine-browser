import os
from PIL import Image
import numpy as np
import re
from pathlib import Path
import json

def rgb_str_to_tuple(rgb_str):
    r, g, b = map(int, re.findall(r'\d+', rgb_str))
    return (r, g, b)

def load_palettes(palette_path):
    with open(palette_path) as f:
        palettes = json.load(f)
    
    converted_palettes = {}
    for palette_name, palette in palettes.items():
        converted_palettes[palette_name] = {
            int(k): rgb_str_to_tuple(v) for k, v in palette.items() if v != '...'
        }
    
    return converted_palettes

def get_palette_for_file(filename, palettes):
    if "WALL" in filename:
        if filename.startswith("J"):
            return palettes.get("JFLOOR", {})
        elif filename.startswith("S"):
            return palettes.get("SFLOOR", {})
        elif filename.startswith("W"):
            return palettes.get("WFLOOR", {})
        elif filename.startswith("P"):
            return palettes.get("PFLOOR", {})
        elif re.match(r'WALL\d+', filename):
            return palettes.get("FLOOR", {})
        else:
            return palettes.get("KFLOOR", {})
    elif "OBJECT" in filename:
        if filename.startswith("J"):
            return palettes.get("JFLOOR", {})
        elif filename.startswith("P"):
            return palettes.get("PFLOOR", {})
        elif filename.startswith("K"):
            return palettes.get("KFLOOR", {})
        elif filename.startswith("S"):
            return palettes.get("SFLOOR", {})            
        elif filename.startswith("W"):
            return palettes.get("WFLOOR", {})            
        elif re.match(r'OBJECTS\d+', filename):
            return palettes.get("FLOOR", {})            
            
    return palettes.get("KFLOOR", {})

def process_spr_file(spr_file_path, output_directory,output_individual, palettes):
    base_filename = os.path.basename(spr_file_path)
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    sprite_directory = os.path.join(output_individual, filename_without_ext)
    os.makedirs(sprite_directory, exist_ok=True)
    
    with open(spr_file_path, 'rb') as file:
        data = file.read()
    
    number_of_images = data[0]
    image_data_offset = 1 + (number_of_images * 2)
    
    images = []
    for i in range(number_of_images):
        width = data[1 + (i * 2)]
        height = data[1 + (i * 2) + 1]
        total_pixels = width * height
        
        pixels = data[image_data_offset:image_data_offset + total_pixels]
        image_data_offset += total_pixels
        
        images.append((width, height, pixels))
    
    palette = get_palette_for_file(filename_without_ext, palettes)
    
    for i, (width, height, pixels) in enumerate(images):
        image = Image.new('RGBA', (width, height))
        pixel_data = np.frombuffer(pixels, dtype=np.uint8).reshape((height, width))
        
        for y in range(height):
            for x in range(width):
                color_index = pixel_data[y, x]
                if color_index == 0:
                    color = (0, 0, 0, 0)
                else:
                    rgb_color = palette.get(color_index, (0, 0, 0))
                    color = (*rgb_color, 255)
                
                image.putpixel((x, y), color)
        
        image_path = os.path.join(sprite_directory, f'{filename_without_ext}_{i }.png') # changed from i+1
        image.save(image_path, 'PNG')
        print(f'Saved {image_path}')
        
        
     


        if "WALL" in base_filename:
            
            path_filename_without_ext = re.sub(r'\d+', '', filename_without_ext).lower()  # Remove numbers from the filename

            wall_sprite_directory = os.path.join(f"{output_directory}/sprites", "walls", path_filename_without_ext)
            os.makedirs(wall_sprite_directory, exist_ok=True)  # Create the directory if it doesn't exist            
            
            wall_image_path = os.path.join(wall_sprite_directory, f'{filename_without_ext.lower()}_{i }.png')# changed from i+1
            image.save(wall_image_path, 'PNG')
            
        if "OBJECT" in base_filename:
            
            path_filename_without_ext = re.sub(r'\d+', '', filename_without_ext).lower()  # Remove numbers from the filename

            object_sprite_directory = os.path.join(f"{output_directory}/sprites", "objects", path_filename_without_ext)
            os.makedirs(object_sprite_directory, exist_ok=True)  # Create the directory if it doesn't exist            
            
            object_image_path = os.path.join(object_sprite_directory, f'{filename_without_ext.lower()}_{i }.png')# changed from i+1
            image.save(object_image_path, 'PNG')            

        
        

def export_sprites(output_folder,original_gamedata):
    #palette_path = r'C:/2025_projects/Quarantine_fullset/output/textures/editor/data/palettes.json'
    palette_path = f'{output_folder}/textures/editor/data/palettes.json'
    palettes = load_palettes(palette_path)
    
    #input_directory = r'C:/2025_projects/Quarantine_fullset/Original_Game'
    input_directory = original_gamedata
    #output_directory = r'C:/2025_projects/Quarantine_fullset/output/sprites/individual_sprites/'
    #output_directory = f'{output_folder}/sprites/individual_sprites/'
    output_individual = f'{output_folder}/sprites/individual_sprites/'
    output_directory = output_folder
    
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(output_individual, exist_ok=True)
    
    for spr_file in Path(input_directory).glob('*.SPR'):
        print(f'\nProcessing {spr_file}...')
        try:
            process_spr_file(str(spr_file), output_directory,output_individual, palettes)
            print(f'Successfully processed {spr_file}')
        except Exception as e:
            print(f'Error processing {spr_file}: {str(e)}')

if __name__ == '__main__':
    #export_sprites()
    
    original_gamedata="C:/2025_projects/Quarantine_fullsetRENAMETEST/test4git/Original_Game"
    output_folder="C:/2025_projects/Quarantine_fullsetRENAMETEST/test4git/output"
    
    export_sprites(output_folder,original_gamedata)
    
    print("please run as part of the export parts script, or mess with the output path above")