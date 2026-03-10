import struct
import sys
import json
import os
from PIL import Image


#-------------------------------Convert all of the IMG files to gif - output\textures\editor

def modify_gif_header(input_filepath, output_filepath):
    """
    Opens a GIF file as hex, changes the header from IMAGEX' to 'GIF87a' saves it to output folder
    """
    try:
        # Open the original GIF file in binary mode
        with open(input_filepath, 'rb') as f:
            gif_data = f.read()

        ## Check if the file starts with a GIF header (either GIF87a or GIF89a)
        #if not gif_data.startswith(b'IMG'):
        #    print("This is not a valid GIF file.")
        #    return
        
        # Change the first 6 bytes from GIF87a (or GIF89a) to IMAGEX
        modified_data = b'GIF87a' + gif_data[6:]

        # Save the modified data as CAB.IMG
        with open(output_filepath, 'wb') as f_out:
            f_out.write(modified_data)

        print(f"Modified file saved as {output_filepath}")

    except FileNotFoundError:
        print(f"Error: File {input_filepath} not found.")
    except Exception as e:
        print(f"Error: {e}")


def convert_to_gif(original_gamedata,output_folder):
    folder_path = original_gamedata
    img_files = [f for f in os.listdir(folder_path) if f.endswith('.IMG')]
    
    os.makedirs("{}/textures/editor/gifs/".format(output_folder), exist_ok=True)
    os.makedirs("{}/textures/editor/data/".format(output_folder), exist_ok=True)

    

    for img_file in img_files:
        print(img_file)
        modify_gif_header("{}/{}".format(folder_path,img_file), "{}/textures/editor/gifs/{}".format(output_folder,img_file.replace(".IMG",".GIF")))
        
    gif_folder_path = "{}/textures/editor/gifs/".format(output_folder)
    gif_files = [f for f in os.listdir(gif_folder_path) if f.endswith('.GIF')]      



    gif_palettes={}

    for gif in gif_files:
        print(gif)
        gif_palettes[gif.replace(".GIF","")]=parse_gif("{}/textures/editor/gifs/{}".format(output_folder,gif))

    # save this palette to output\textures\editor\data\palettes.json
    file_name = "{}/textures/editor/data/palettes.json".format(output_folder)
    with open(file_name, 'w') as json_file:
        json.dump(gif_palettes, json_file, indent=4)
    print(f"JSON data has been saved to {file_name}")       
        




def parse_gif(filepath):
    """
    Parse a GIF file and extract detailed information.
    """
    try:
        with open(filepath, 'rb') as f:
            # Read file signature and version
            signature = f.read(6).decode('ascii')
            if not signature.startswith('GIF'):
                raise ValueError("Not a valid GIF file")
            
            print(f"File Signature: {signature}")
            
            # Logical Screen Descriptor
            width, height = struct.unpack('<HH', f.read(4))
            
            # Read packed byte for global color table info
            packed_byte = f.read(1)[0]
            
            # Parse global color table details
            global_color_table_flag = bool(packed_byte & 0x80)
            color_resolution = ((packed_byte & 0x70) >> 4) + 1
            sort_flag = bool(packed_byte & 0x08)
            global_color_table_size = 2 ** ((packed_byte & 0x07) + 1)
            
            # Background color index and pixel aspect ratio
            background_color_index = f.read(1)[0]
            pixel_aspect_ratio = f.read(1)[0]
            
            print("\nLogical Screen Descriptor:")
            print(f"Image Width: {width} pixels")
            print(f"Image Height: {height} pixels")
            print(f"Global Color Table Flag: {global_color_table_flag}")
            print(f"Color Resolution: {color_resolution} bits")
            print(f"Sort Flag: {sort_flag}")
            print(f"Global Color Table Size: {global_color_table_size} colors")
            print(f"Background Color Index: {background_color_index}")
            print(f"Pixel Aspect Ratio: {pixel_aspect_ratio}")
            
            
            colourdict={}
            # Parse Global Color Table if present
            if global_color_table_flag:
                print("\nGlobal Color Palette:")
                palette = []
                for i in range(global_color_table_size):
                    r, g, b = struct.unpack('BBB', f.read(3))
                    palette.append((r, g, b))
                    print(f"Colorx {i}: RGB({r}, {g}, {b})")
                    colourdict[i]=f"rgb({r},{g},{b})"
            # Continue parsing blocks
            parse_gif_blocks(f)
    
            return(colourdict)
    
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
    except Exception as e:
        print(f"Error parsing GIF: {e}")

def parse_gif_blocks(f):
    """
    Parse through the remaining blocks in the GIF file.
    """
    block_types = {
        0x21: "Extension Block",
        0x2C: "Image Descriptor",
        0x3B: "Trailer (End of File)"
    }
    
    while True:
        # Read block identifier
        block_start = f.read(1)
        if not block_start:
            break
        
        block_type = block_start[0]
        
        if block_type == 0x3B:  # Trailer (end of file)
            print("\nReached end of file.")
            break
        
        if block_type == 0x21:  # Extension Block
            parse_extension_block(f)
        
        elif block_type == 0x2C:  # Image Descriptor
            parse_image_descriptor(f)
        
        else:
            print(f"\nUnknown block type: 0x{block_type:02X}")
            break

def parse_extension_block(f):
    """
    Parse GIF extension blocks.
    """
    # Read extension sub-type
    ext_type = f.read(1)[0]
    ext_type_names = {
        0xF9: "Graphic Control Extension",
        0xFE: "Comment Extension",
        0x01: "Plain Text Extension",
        0xFF: "Application Extension"
    }
    
    print(f"\nExtension Block: {ext_type_names.get(ext_type, 'Unknown')}")
    
    # Read block size
    block_size = f.read(1)[0]
    
    # Skip the block data
    f.read(block_size)
    
    # Read and skip sub-blocks until a null terminator is found
    while True:
        sub_block_size = f.read(1)[0]
        if sub_block_size == 0:
            break
        f.read(sub_block_size)

def parse_image_descriptor(f):
    """
    Parse image descriptor block.
    """
    # Read image position and size
    left, top, width, height = struct.unpack('<HHHH', f.read(8))
    
    # Read packed byte for local color table
    packed_byte = f.read(1)[0]
    
    local_color_table_flag = bool(packed_byte & 0x80)
    interlace_flag = bool(packed_byte & 0x40)
    sort_flag = bool(packed_byte & 0x20)
    local_color_table_size = 2 ** ((packed_byte & 0x07) + 1)
    
    print("\nImage Descriptor:")
    print(f"Position: ({left}, {top})")
    print(f"Size: {width} x {height} pixels")
    print(f"Local Color Table Flag: {local_color_table_flag}")
    print(f"Interlace Flag: {interlace_flag}")
    print(f"Sort Flag: {sort_flag}")
    
    if local_color_table_flag:
        print("\nLocal Color Palette:")
        for i in range(local_color_table_size):
            r, g, b = struct.unpack('BBB', f.read(3))
            print(f"Colors {i}: RGB({r}, {g}, {b})")
    
    # Skip image data
    lzw_min_code_size = f.read(1)[0]
    print(f"LZW Minimum Code Size: {lzw_min_code_size}")
    
    # Read and skip image data blocks
    while True:
        block_size = f.read(1)[0]
        if block_size == 0:
            break
        f.read(block_size)

# split the floor files


def splitfloors(output_filepath):
    folder_path = os.path.join(output_filepath, "textures", "editor", "gifs")
    floor_gif_files = [f for f in os.listdir(folder_path) if "FLOOR" in f]
    print(floor_gif_files)

    output_folder = os.path.join(output_filepath, "textures", "game", "floors")
    os.makedirs(output_folder, exist_ok=True)  # Create the directory if it doesn't exist

    for gif_file in floor_gif_files:
        gif_path = os.path.join(folder_path, gif_file)

        if not os.path.exists(gif_path):
            print(f"File not found: {gif_path}")
            continue

        base_name = os.path.splitext(gif_file)[0]  # Base name for output files

        with Image.open(gif_path) as gif:
            # Define tile dimensions
            tile_width, tile_height = 64, 64
            grid_cols, grid_rows = 5, 3  # 5x3 grid of tiles

            # Alphabetical index across all tiles
            tile_letter_index = 0

            try:
                while True:
                    gif.seek(tile_letter_index // (grid_cols * grid_rows))  # Frame index
                    frame = gif.convert("RGBA")  # Ensure frame is in RGBA format

                    # Calculate tile's position within the current frame
                    tile_number = tile_letter_index % (grid_cols * grid_rows)
                    row = tile_number // grid_cols
                    col = tile_number % grid_cols

                    # Calculate tile's bounding box
                    left = col * tile_width
                    top = row * tile_height
                    right = left + tile_width
                    bottom = top + tile_height

                    # Crop the tile
                    tile = frame.crop((left, top, right, bottom))

                    # Create the filename for the tile
                    tile_filename = f"{base_name}_{chr(97 + tile_letter_index)}.gif"

                    # Save the tile
                    tile_save_path = os.path.join(output_folder, tile_filename)
                    tile.save(tile_save_path, format="GIF")

                    # Increment tile letter index
                    tile_letter_index += 1
            except EOFError:
                # End of the GIF frames
                pass

    print(f"Tiles from specified GIFs have been extracted and saved in '{output_folder}'")
    return(f"Tiles from specified GIFs have been extracted and saved in '{output_folder}'")







# Usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_gif(sys.argv[1])
    else:
        print("Please provide a GIF file path as an argument.")