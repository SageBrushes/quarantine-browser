import json
import math
import os
    
from tqdm import tqdm
import random    

unique_sizes = {}

class UDMFMap:
    def __init__(self):
        self.vertices = []
        self.linedefs = []
        self.sidedefs = []
        self.sectors = []
        self.actors = []
        self.vertex_map = {}

    def add_vertex(self, x, y):
        pos = (float(x), float(y))
        if pos not in self.vertex_map:
            index = len(self.vertices)
            self.vertices.append(pos)
            self.vertex_map[pos] = index
        return self.vertex_map[pos]

    def find_shared_edge(self, v1_pos, v2_pos):
        """Find if these vertices form a shared edge with existing sectors"""
        v1 = self.vertex_map.get((float(v1_pos[0]), float(v1_pos[1])))
        v2 = self.vertex_map.get((float(v2_pos[0]), float(v2_pos[1])))

        if v1 is None or v2 is None:
            return None

        for i, linedef in enumerate(self.linedefs):
            if (linedef['v1'], linedef['v2']) in [(v1, v2), (v2, v1)]:
                return i
        return None

    def add_sector(self, v1, v2, v3, v4, heightfloor, heightceiling, texturefloor, textureceiling, lightlevel=192, rotationfloor=0, floor_scale_x=1.0, floor_scale_y=1.0,scalex=1.0,scaley=1.0):
        # Create sector
        sector_index = len(self.sectors)
        self.sectors.append({
            'heightfloor': heightfloor,
            'heightceiling': heightceiling,
            'texturefloor': texturefloor,
            'textureceiling': textureceiling,
            'lightlevel': lightlevel,
            'rotationfloor': rotationfloor,
            'floor_scale_x': floor_scale_x,
            'floor_scale_y': floor_scale_y
        })

        # Add vertices in correct order for DOOM
        vertices = []
        for v in [v1, v4, v3, v2]:  # Reorder vertices to match DOOM's expectations
            vertices.append(self.add_vertex(*v))

        # Create edges
        edges = list(zip(vertices, vertices[1:] + [vertices[0]]))

        # Add linedefs and sidedefs for each edge
        for v1_pos, v2_pos in zip([v1, v4, v3, v2], [v4, v3, v2, v1]):
            shared_edge = self.find_shared_edge(v1_pos, v2_pos)
            v1_idx = self.add_vertex(*v1_pos)
            v2_idx = self.add_vertex(*v2_pos)

            if shared_edge is not None:
                # This is a shared edge - make it two-sided
                sidedef = {'sector': sector_index}  # No texturemiddle for shared edges
                sidedef_idx = len(self.sidedefs)
                self.sidedefs.append(sidedef)

                # Update existing linedef to be two-sided
                self.linedefs[shared_edge]['sideback'] = sidedef_idx
                self.linedefs[shared_edge]['twosided'] = True
                if 'blocking' in self.linedefs[shared_edge]:
                    del self.linedefs[shared_edge]['blocking']

                # Remove texturemiddle from the existing sidedef (if it exists)
                front_sidedef_idx = self.linedefs[shared_edge]['sidefront']
                if 'texturemiddle' in self.sidedefs[front_sidedef_idx]:
                    del self.sidedefs[front_sidedef_idx]['texturemiddle']

            else:
                # This is an outer edge - make it one-sided with a texture
                sidedef = {
                    'sector': sector_index,
                    'texturemiddle': "STARTAN2"  # Only use middle texture for outer walls
                }
                sidedef_idx = len(self.sidedefs)
                self.sidedefs.append(sidedef)

                self.linedefs.append({
                    'v1': v1_idx,
                    'v2': v2_idx,
                    'sidefront': sidedef_idx,
                    'blocking': True
                })

    def add_actor(self, name, x, y, z, angle=90, type=1,scalex=1.0,scaley=1.0):
        self.actors.append({
            'name': name,
            'x': x,
            'y': y,
            'z': z,
            'angle': angle,
            'type': type,
            'skill1': True,
            'skill2': True,
            'skill3': True,
            'skill4': True,
            'skill5': True,
            'skill6': True,
            'skill7': True,
            'skill8': True,
            'single': True,
            'coop': True,
            'dm': True,
            'class1': True,
            'class2': True,
            'class3': True,
            'class4': True,
            'class5': True,
            'scalex':scalex,
            'scaley':scaley
        })



    def generate_udmf(self):
        udmf = 'namespace = "zdoom";\n\n'

        # Generate vertices with progress bar
        print("Generating vertices...")
        for i, (x, y) in enumerate(tqdm(self.vertices, desc="Vertices")):
            udmf += f'vertex // {i}\n{{\nx = {x};\ny = {y};\n}}\n\n'

        # Generate linedefs with progress bar
        print("Generating linedefs...")
        for i, linedef in enumerate(tqdm(self.linedefs, desc="Linedefs")):
            udmf += f'linedef // {i}\n{{\n'
            udmf += f'v1 = {linedef["v1"]};\n'
            udmf += f'v2 = {linedef["v2"]};\n'
            udmf += f'sidefront = {linedef["sidefront"]};\n'
            if 'sideback' in linedef:
                udmf += f'sideback = {linedef["sideback"]};\n'
                udmf += 'twosided = true;\n'
            if linedef.get('blocking'):
                udmf += 'blocking = true;\n'
            udmf += '}\n\n'

        # Generate sidedefs with progress bar
        print("Generating sidedefs...")
        for i, sidedef in enumerate(tqdm(self.sidedefs, desc="Sidedefs")):
            udmf += f'sidedef // {i}\n{{\n'
            udmf += f'sector = {sidedef["sector"]};\n'
            if 'texturemiddle' in sidedef:
                udmf += f'texturemiddle = "{sidedef["texturemiddle"]}";\n'
            udmf += '}\n\n'

        # Generate sectors with progress bar
        print("Generating sectors...")
        for i, sector in enumerate(tqdm(self.sectors, desc="Sectors")):
            udmf += f'sector // {i}\n{{\n'
            for key, value in sector.items():
                if isinstance(value, str):
                    udmf += f'{key} = "{value}";\n'
                else:
                    udmf += f'{key} = {value};\n'
            udmf += '}\n\n'

        # Generate actors with progress bar
        print("Generating actors...")
        for i, actor in enumerate(tqdm(self.actors, desc="Actors")):
            udmf += f'thing // {i} {actor["name"]}\n{{\n'
            udmf += f'x = {actor["x"]};\n'
            udmf += f'y = {actor["y"]};\n'
            udmf += f'height = {actor["z"]};\n'
            udmf += f'angle = {actor["angle"]};\n'
            udmf += f'type = {actor["type"]};\n'
            udmf += 'skill1 = true;\n'
            udmf += 'skill2 = true;\n'
            udmf += 'skill3 = true;\n'
            udmf += 'skill4 = true;\n'
            udmf += 'skill5 = true;\n'
            udmf += 'skill6 = true;\n'
            udmf += 'skill7 = true;\n'
            udmf += 'skill8 = true;\n'
            udmf += 'single = true;\n'
            udmf += 'coop = true;\n'
            udmf += 'dm = true;\n'
            udmf += 'class1 = true;\n'
            udmf += 'class2 = true;\n'
            udmf += 'class3 = true;\n'
            udmf += 'class4 = true;\n'
            udmf += 'class5 = true;\n'
            udmf += f'scalex = {actor["scalex"]};\n'
            udmf += f'scaley = {actor["scaley"]};\n'
            udmf += '}\n\n'

        return udmf


def load_definition_data(dict_file='input_config_json/kcity_setup.json'):
    """
    Load numbers from a CSV file into a 2D array (list of lists).
    Each row in the CSV file corresponds to a row in the 2D array.
    """
    # Open the JSON file
    with open(dict_file, 'r') as file:
        # Load the JSON data into a Python dictionary
        definition_data = json.load(file)

    # Now `data` is a dictionary containing the contents of the JSON file
    return definition_data["tiles"]

#def make_multiple(map_definitions, udmf_map , object_pre_num , wall_pre_num,city,tracking_dict):
#    # Number of tiles per row
#    tiles_per_row = 10
#
#    # Tile size
#    tile_offset = 512
#
#    # Total number of tiles
#    total_tiles = 128
#
#    # Loop through each row
#    for row in range(total_tiles // tiles_per_row):
#        # Loop through each column in the row
#        for col in range(tiles_per_row):
#            # Calculate the tile index
#            tile_index = row * tiles_per_row + col + 1
#
#            # Calculate the x and y coordinates
#            x = col * tile_offset
#            y = -row * tile_offset
#
#            # Create the tile
#            create_a_floor(map_definitions[str(tile_index)], udmf_map, x, y, tile_index,city)
#            create_a_sprites(map_definitions[str(tile_index)], udmf_map, x, y,  object_pre_num , wall_pre_num,tracking_dict)
#            create_walls_from_sprites(map_definitions[str(tile_index)], udmf_map, x, y, tile_index,object_pre_num , wall_pre_num,tracking_dict)
#
#    write_unique_sizes_to_json()
    



def make_multiple(tiles_2d_normalised, map_definitions, udmf_map, object_pre_num, wall_pre_num, city, tracking_dict, grid_size=100, tile_size=512):
    total_grid_size = grid_size * tile_size
    start_x = - (50 * 512)
    start_y = (50 * 512)

    print("Starting grid generation...")

    for row in tqdm(range(grid_size), desc="Generating Rows"):
        for col in tqdm(range(grid_size), desc="Generating Columns", leave=False):
            # Get tile_index from tiles_2d_normalised, defaulting to 0 if out of bounds
            if row < len(tiles_2d_normalised) and col < len(tiles_2d_normalised[0]):
                tile_index = tiles_2d_normalised[row][col]
            else:
                tile_index = 0  # Default to 0 if out of bounds

            # Calculate the x and y coordinates
            x = start_x + col * tile_size
            y = start_y - row * tile_size

            print(f"Generating tile {tile_index} at ({x}, {y})----{row}-{col}")

            # Get the tile definition (default to None if missing)
            tile_def = map_definitions.get(str(tile_index))

            if tile_def:  # Ensure the tile definition exists before proceeding
                create_a_floor(tile_def, udmf_map, x, y, tile_index, city)
                
                if "sprites" in tile_def:  # Ensure "sprites" key exists
                    create_a_sprites(tile_def, udmf_map, x, y, object_pre_num, wall_pre_num, tracking_dict)
                
                if "walls" in tile_def:  # Ensure "walls" key exists
                    create_walls_from_sprites(tile_def, udmf_map, x, y, tile_index, object_pre_num, wall_pre_num, tracking_dict)

    print("Grid generation complete. Writing unique sizes to JSON...")
    write_unique_sizes_to_json()
    print("JSON writing complete.")

    

def create_a_sprites(map_definitions, udmf_map, offset_x, offset_y, object_pre_num , wall_pre_num,tracking_dict):
    tile_width = 512
    tile_height = 512
    #print("-0------------")

    spritedef = map_definitions["sprites"]
    #print("-x-x-x-x-x-x-x-x-x-")
    for sprite in spritedef:
        sprite_x = sprite["sprite_x"] + offset_x
        sprite_y = (512 - sprite["sprite_y"]) + offset_y
        sprite_z = sprite["sprite_z"]
        sprite_name = sprite["sprite_image"].replace(".png", "")
        sprite_angle = 0
        num_part = int(sprite_name.split("_")[1])

        #sprite_type = int(f"{object_pre_num}00{num_part:02d}")
        sprite_type = tracking_dict["object_name_mapping"][sprite_name]
        #print("---------------{}".format(sprite_type))
        #print(sprite_name, sprite_x, sprite_y, sprite_z, sprite_angle, sprite_type)
        #input("-----------------")
        udmf_map.add_actor(sprite_name, sprite_x, sprite_y, sprite_z, sprite_angle, sprite_type)

def create_walls_from_sprites(map_definitions, udmf_map, offset_x, offset_y, tile_index,object_pre_num , wall_pre_num,tracking_dict):
    global unique_sizes

    tile_width = 512
    tile_height = 512

    walldefs = map_definitions.get("walls", [])
    for wall in walldefs:
        #print(wall)
        tile_count = wall["tile_count"]
        start_x = wall["start_east"] + offset_x
        start_y = (512 - wall["start_south"]) + offset_y
        end_x = wall["end_east"] + offset_x
        end_y = (512 - wall["end_south"]) + offset_y

        # Calculate the step size for each tile
        step_x = (end_x - start_x) / tile_count
        step_y = (end_y - start_y) / tile_count

        # Determine the texture to use
        if wall["texture_repeat"]:
            wall_texture = wall["wall_texture_filenames"][0][0].replace(".png", "")
        else:
            wall_texture = None  # This will be set for each tile below

        # Calculate the angle of the wall
        angle_rad = math.atan2(end_y - start_y, end_x - start_x)
        angle_deg = math.degrees(angle_rad)
        angle_deg = round(angle_deg + 90)
        if angle_deg < 0:
            angle_deg += 360
        if angle_deg > 359:
            angle_deg -= 360

        for i in range(tile_count):
            # Calculate the center point of the wall tile
            center_x = start_x + (i + 0.5) * step_x
            center_y = start_y + (i + 0.5) * step_y

            # If texture_repeat is False, get the texture for the current tile
            if not wall["texture_repeat"]:
                if i < len(wall["wall_texture_filenames"][0]):
                    wall_texture = wall["wall_texture_filenames"][0][i].replace(".png", "")
                else:
                    wall_texture = wall["wall_texture_filenames"][0][-1].replace(".png", "")  # Fallback to the last texture

            # Extract numbers from the wall texture filename
            parts = wall_texture.split("_")
            #if len(parts) == 2:
            #    first_number = int(parts[0][5:])  # Extract number after 'kwall'
            #    second_number = int(parts[1])
            #    type_value = (10000 *wall_pre_num) + first_number * 100 + second_number
            #else:
            #    type_value = int(f"100{i+1:02d}")  # Fallback to the original type value
            type_value = tracking_dict["wall_name_mapping"][wall_texture]



            z = (-(wall["wall_offset_vertical"] )+20)*0.85
            # Fix for the heights being weird in Doom
            #if z == 64:
            #    z = 54

            # Calculate the actual width of the wall tile
            width = math.sqrt((step_x ** 2) + (step_y ** 2))
            size_key = (width, wall["wall_height"])

            # Update the unique sizes dictionary
            if size_key not in unique_sizes:
                unique_sizes[size_key] = {"width": width, "height": wall["wall_height"], "frequency": 0, "tiles": []}
            unique_sizes[size_key]["frequency"] += 1
            unique_sizes[size_key]["tiles"].append(tile_index)

            # Add the actor for the wall tile
            udmf_map.add_actor(
                name=wall_texture,
                x=center_x,
                y=center_y,
                z=z,  # Assuming the actor's z position is half the wall height
                angle=round(angle_deg),  # Angle of the wall
                type=type_value,
                scalex = width/64,
                scaley = wall["wall_height"]/64
            )

def write_unique_sizes_to_json():
    global unique_sizes
    # Sort the unique sizes by frequency
    sorted_sizes = sorted(unique_sizes.values(), key=lambda x: x["frequency"], reverse=True)

    # Write sorted unique sizes to a JSON file
    with open("wall_tile_sizes.json", "w") as file:
        json.dump(sorted_sizes, file, indent=4)

    # Create a new dictionary for rounded sizes
    rounded_unique_sizes = {}

    for size in sorted_sizes:
        rounded_width = round(size["width"])
        rounded_height = round(size["height"])
        rounded_key = (rounded_width, rounded_height)

        if rounded_key not in rounded_unique_sizes:
            rounded_unique_sizes[rounded_key] = {
                "width": rounded_width,
                "height": rounded_height,
                "frequency": 0,
                "tiles": []
            }

        rounded_unique_sizes[rounded_key]["frequency"] += size["frequency"]
        rounded_unique_sizes[rounded_key]["tiles"].extend(size["tiles"])

    # Convert the rounded unique sizes dictionary to a list
    rounded_sorted_sizes = sorted(rounded_unique_sizes.values(), key=lambda x: x["frequency"], reverse=True)

    # Write sorted and rounded unique sizes to a JSON file
    with open("wall_tile_sizes_rounded.json", "w") as file:
        json.dump(rounded_sorted_sizes, file, indent=4)

def create_a_floor(map_definitions, udmf_map, offset_x, offset_y, tile_index,city):
    # Define vertices for the sector
    vertices = [
        (offset_x, offset_y),
        (offset_x, offset_y + 512),
        (offset_x + 512, offset_y + 512),
        (offset_x + 512, offset_y)
    ]
    
    first_letter=""
    if city=="kcity":
        first_letter="k"
    elif city=="city":
        first_letter="z"
    elif city=="jcity":
        first_letter="j"
    elif city=="pcity":
        first_letter="p"
    elif city=="scity":
        first_letter="s"
    elif city=="wcity":
        first_letter="w"        
    
    
    
    

    # Define sector properties
    floor_height = 0  # You can set this to the desired floor height
    heightceiling = 512  # You can set this to the desired ceiling height
    #texturefloor = f"tile_{tile_index}"  # Use the tile number for the texture name
    texturefloor = f"{first_letter}_f_{tile_index}"  # Use the tile number for the texture name
    textureceiling = "F_SKY1"  # You can set this to the desired ceiling texture
    lightlevel = 192
    rotationfloor = 0  # You can set this to the desired rotation
    floor_scale_x = 1.0
    floor_scale_y = 1.0

    # Add sector to the UDMF map
    udmf_map.add_sector(
        vertices[3], vertices[2],vertices[1],vertices[0],  
        heightfloor=floor_height, heightceiling=heightceiling,
        texturefloor=texturefloor, textureceiling=textureceiling,
        lightlevel=lightlevel, rotationfloor=rotationfloor,
        floor_scale_x=floor_scale_x, floor_scale_y=floor_scale_y
    )




def make_udmf(output_folder,city,tiles_2d_normalised):
    
    os.makedirs("{}/doom/udmf/".format(output_folder), exist_ok=True)

    
    if city == "jcity" :
        object_pre_num   =6
        wall_pre_num     =5
    if city == "pcity" :
        object_pre_num   =4
        wall_pre_num     =3
    if city == "wcity" :
        object_pre_num   =10
        wall_pre_num     =9
    if city == "scity" :
        object_pre_num   =7
        wall_pre_num     =6
    if city == "kcity" :
        object_pre_num   =2
        wall_pre_num     =1
    if city == "city"  :
        object_pre_num   =12
        wall_pre_num     =11

    
    tracking_file = os.path.join(output_folder, "doom", "doomid_tracking.json")

    # Load the tracking file
    if os.path.exists(tracking_file):
        with open(tracking_file, "r") as f:
            tracking_dict = json.load(f)

    
    udmf_map = UDMFMap()

    map_definitions = load_definition_data('{}/modeldef/tile_config_{}.json'.format(output_folder,city))
    make_multiple(tiles_2d_normalised,map_definitions, udmf_map,  object_pre_num , wall_pre_num,city,tracking_dict )

    # Generate UDMF content
    udmf_content = udmf_map.generate_udmf()

    # Write UDMF content to a text file
    with open("{}/doom/udmf/udmf_{}.txt".format(output_folder , city), "w") as file:
        file.write(udmf_content)   
    
import struct    
import numpy as np
 
def read_map_file(file_path):
    with open(file_path, 'rb') as f:
        # Read width and height (each is UINT16LE)
        width = struct.unpack('<H', f.read(2))[0]  # UINT16LE for width
        height = struct.unpack('<H', f.read(2))[0]  # UINT16LE for height
        print(f"Map Width: {width}, Map Height: {height}")

        # Read the tiles
        tile_data = []
        for tile in range(width * height):
            tile = struct.unpack('<H', f.read(2))[0]  # UINT16LE for each tile
            tile_data.append(tile)

        # Reshape tile data into a 2D grid (list of lists) for easier use
        tiles_2d = [tile_data[i * width:(i + 1) * width] for i in range(height)]

        return width, height, tiles_2d
        


def shift_down_to_128(tiles_2d):
    for i in range(len(tiles_2d)):
        for j in range(len(tiles_2d[i])):
            while tiles_2d[i][j] > 127:
                tiles_2d[i][j] -= 128
    return tiles_2d

original_gamedata="C:/2025_projects/Quarantine_fullset/Original_Game"
output_folder="C:/2025_projects/Quarantine_fullset/output"
map_path="C:/2025_projects/Quarantine_fullset/Original_Game/PCITY.MAP"
width, height, tiles_2d = read_map_file(map_path)
tiles_2d_normalised = shift_down_to_128(tiles_2d)
make_udmf(output_folder,"pcity",tiles_2d_normalised)

print(tiles_2d_normalised)



#if __name__ == "__main__":
#    udmf_map = UDMFMap()
#
#    map_definitions = load_definition_data('input_config_json/kcity_setup.json')
#    make_multiple(map_definitions, udmf_map)
#
#    # Generate UDMF content
#    udmf_content = udmf_map.generate_udmf()
#
#    # Write UDMF content to a text file
#    with open("udmf_data.txt", "w") as file:
#        file.write(udmf_content)
#
#    print("UDMF data has been written to udmf_data.txt")
#