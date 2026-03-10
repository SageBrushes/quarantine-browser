import numpy as np
import struct
import os

def read_map_file(file_path):
    with open(file_path, 'rb') as f:
        # Read width and height (each is UINT16LE)
        width = struct.unpack('<H', f.read(2))[0]  # UINT16LE for width
        height = struct.unpack('<H', f.read(2))[0]  # UINT16LE for height
        print(f"Map Width: {width}, Map Height: {height}")

        # Read the tiles
        tile_data = [struct.unpack('<H', f.read(2))[0] for _ in range(width * height)]

        # Reshape tile data into a 2D grid (list of lists)
        tiles_2d = [tile_data[i * width:(i + 1) * width] for i in range(height)]

        return width, height, tiles_2d

def shift_down_to_128(tiles_2d):
    return [[tile % 128 for tile in row] for row in tiles_2d]
    
def resize_and_pad_array(tiles_2d_normalised, target_size=(100, 100)):
    # Convert to NumPy array for proper slicing and reshaping
    tiles_2d_normalised = np.array(tiles_2d_normalised, dtype=int)

    current_rows, current_cols = tiles_2d_normalised.shape
    target_rows, target_cols = target_size

    # Trim if larger
    trimmed_array = tiles_2d_normalised[:target_rows, :target_cols]

    # Create a new zero-padded array
    acs_map_array = np.zeros(target_size, dtype=int)
    
    # Copy into new array
    acs_map_array[:trimmed_array.shape[0], :trimmed_array.shape[1]] = trimmed_array

    return acs_map_array
    
def generate_jmaptiles(array,start_letter):
    flattened = array.flatten()
    total_elements = len(flattened)

    # Create list
    newarray = [f"{start_letter}city_tile_{num}" for num in flattened]
   
    
    

    # Format as a C-style array
    result = f"int {start_letter}maptiles[{total_elements}] = {{\n"
    result += ",\n".join(f'    "{tile}"' for tile in newarray)
    result += "\n};"

    return result

def create_maptiles_for_acs(start_letter,map_name,original_gamedata,output_folder):
    print(map_name)

    map_name = map_name.upper()
    #map_path = f"C:/2025_projects/Quarantine_fullset/Original_Game/{map_name}.MAP"
    map_path = f"{original_gamedata}/{map_name}.MAP"
    #output_folder = "C:/2025_projects/Quarantine_fullset/output"
    output_folder = output_folder
    
    
    width, height, tiles_2d = read_map_file(map_path)
    tiles_2d_normalised = shift_down_to_128(tiles_2d)
    acs_map_array = resize_and_pad_array(tiles_2d_normalised)
    
    flattened_array = acs_map_array.flatten()
    output = generate_jmaptiles(flattened_array,start_letter)

    # Ensure output folder exists
    acs_output_folder="{}/acs".format(output_folder)

    with open(os.path.join(acs_output_folder, f"{map_name}tracking.acs"), 'w') as outfile:
        outfile.write(output)

    print(f"Generated ACS map tiles for {map_name} at {acs_output_folder}/{map_name}tracking.acs")

