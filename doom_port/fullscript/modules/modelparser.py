
import os
import json
import shutil
from tqdm import tqdm
from pathlib import Path
import struct
import math



# Global variables to store the bytes and notes
full_original_bytes = []
original_bytes = []
current_bytes = []
byte_notes = {}
byte_properties = {}  # unused now
byte_types = {}

#original_gamedata="C:/2025_projects/Quarantine_fullset/Original_Game"

# SET CURRENT MAP HERE:
MAP_CURRENT_MAP = "kcity"
MAP_BLK = ""
MAP_OBJECTS=""
MAP_FLOORS=""
MAP_WALLS=""
# Which map are you dealing with?
def pick_map(mapname):
    
    
    global MAP_BLK
    global MAP_CURRENT_MAP
    print("loading map {}".format(MAP_CURRENT_MAP))
    global MAP_OBJECTS
    global MAP_FLOORS
    global MAP_WALLS
    print("picking mapname")

    if mapname == "kcity":
        MAP_CURRENT_MAP = "kcity"
        MAP_BLK = "KCITY.BLK"
        MAP_OBJECTS="kobjects"
        MAP_FLOORS="kfloor"
        MAP_WALLS="kwall"
    elif mapname == "pcity":
        MAP_CURRENT_MAP = "pcity"
        MAP_BLK = "PCITY.BLK"
        MAP_OBJECTS="pobject"  
        MAP_FLOORS="pfloor"
        MAP_WALLS="pwall" 
    elif mapname == "jcity":
        MAP_CURRENT_MAP = "jcity"
        MAP_BLK = "JCITY.BLK"
        MAP_OBJECTS="jobjects"  #added s
        MAP_FLOORS="jfloor"
        MAP_WALLS="jwall"      
    elif mapname == "scity":
        MAP_CURRENT_MAP = "scity"
        MAP_BLK = "SCITY.BLK"
        MAP_OBJECTS="sobject"  
        MAP_FLOORS="sfloor"
        MAP_WALLS="swall"      
    elif mapname == "wcity":
        MAP_CURRENT_MAP = "wcity"
        MAP_BLK = "WCITY.BLK"
        MAP_OBJECTS="wobjects"  #added s
        MAP_FLOORS="wfloor"
        MAP_WALLS="wwall"      
    elif mapname == "city":
        MAP_CURRENT_MAP = "city"
        MAP_BLK = "CITY.BLK"
        MAP_OBJECTS="object"  
        MAP_FLOORS="floor"
        MAP_WALLS="wall"              
    else:
        print("Map name not yet configured")




print(MAP_OBJECTS)
print(MAP_BLK)
# START_OFFSET = 0x43c  # 1084 in decimal
# Line numbers
#start_decimal = 1028
#end_decimal = 2345
#
#NEW_START_OFFSET = hex(start_decimal)
#NEW_END_OFFSET = hex(end_decimal)
#
#print(NEW_START_OFFSET, NEW_END_OFFSET)
#
#START_OFFSET = start_decimal  # 1084 in decimal  043A
#END_OFFSET = end_decimal  # 1247 in decimal
#print(0x4df)

global_file_data = []  # Initialize the global variable as None

#def load_file():
#    global original_bytes, current_bytes, byte_notes, global_file_data, byte_properties, byte_types, full_original_bytes
#
#    # Initialize byte_notes with empty strings for the full range
#    byte_notes = {str(i): "" for i in range(END_OFFSET - START_OFFSET + 1)}
#    byte_types = {str(i): "" for i in range(END_OFFSET - START_OFFSET + 1)}
#
#    # Load v2 notes if they exist
#    try:
#        with open('byte_notes_v4_{}.json'.format(MAP_CURRENT_MAP), 'r') as f:
#            absolute_notes = json.loads(f.read())
#
#            # Convert absolute positions to relative positions
#            for abs_pos, note in absolute_notes.items():
#                abs_pos_int = int(abs_pos)
#                # Check if the absolute position falls within our current window
#                if START_OFFSET <= abs_pos_int <= END_OFFSET:
#                    relative_pos = abs_pos_int - START_OFFSET
#                    byte_notes[str(relative_pos)] = note
#    except FileNotFoundError:
#        print("byte notes not found!")
#        # Create the file with default content (empty dictionary) if it doesn't exist
#        with open('byte_notes_v4_{}.json'.format(MAP_CURRENT_MAP), 'w') as f:
#            json.dump({}, f)  # Write an empty dictionary as the default content
#
#    try:
#        with open('byte_type_v4_{}.json'.format(MAP_CURRENT_MAP), 'r') as f:
#            absolute_bytetype = json.loads(f.read())
#
#            # Convert absolute positions to relative positions
#            for abs_pos, bytetype in absolute_bytetype.items():
#                abs_pos_int = int(abs_pos)
#                # Check if the absolute position falls within our current window
#                if START_OFFSET <= abs_pos_int <= END_OFFSET:
#                    relative_pos = abs_pos_int - START_OFFSET
#                    byte_types[str(relative_pos)] = bytetype
#    except FileNotFoundError:
#        print("byte notes not found!")
#        # Create the file with default content (empty dictionary) if it doesn't exist
#        with open('byte_type_v4_{}.json'.format(MAP_CURRENT_MAP), 'w') as f:
#            json.dump({}, f)  # Write an empty dictionary as the default content
#
#    try:
#        with open('byte_properties_v4_{}.json'.format(MAP_CURRENT_MAP), 'r') as f:
#            absolute_properties = json.loads(f.read())
#
#            # Convert absolute positions to relative positions
#            for abs_pos, properties in absolute_properties.items():
#                abs_pos_int = int(abs_pos)
#                # Check if the absolute position falls within our current window
#                if START_OFFSET <= abs_pos_int <= END_OFFSET:
#                    relative_pos = abs_pos_int - START_OFFSET
#                    byte_properties[str(relative_pos)] = properties
#    except FileNotFoundError:
#        print("byte notes not found!")
#        # Create the file with default content (empty dictionary) if it doesn't exist
#        with open('byte_properties_v4_{}.json'.format(MAP_CURRENT_MAP), 'w') as f:
#            json.dump({}, f)  # Write an empty dictionary as the default content
#
#    try:
#        with open("{}/{}".format(original_game_data,MAP_BLK), 'rb') as f:
#            # Read the entire file as bytes
#            global_file_data = f.read()  # Store the entire file contents
#            full_original_bytes = list(global_file_data)
#            original_bytes = list(global_file_data[START_OFFSET:END_OFFSET + 1])
#            current_bytes = list(original_bytes)  # Make a copy for modifications
#    except FileNotFoundError:
#        print("Error: MAP_BLK not found")
#        return False
#
#    return True


def parse_sprite(sprite_array):
    
    #"sprite_eastwest", "sprite_northsouth", "sprite_move_vertical", "sprite_firstpart", "sprite_texture", "sprite_resize_vertical"],
    sprite_positive=0
    if int(sprite_array[5]) >0:
        sprite_positive=256
    single_sprite={
        "sprite_x": int(sprite_array[0])+(int(sprite_array[1]) * 256),
        "sprite_y": int(sprite_array[2])+(int(sprite_array[3]) * 256),
        "sprite_z":(sprite_positive - int(sprite_array[4])),
        "sprite_full_array":sprite_array,
        "sprite_texture_array":[int(sprite_array[6]),int(sprite_array[7]),int(sprite_array[8]),int(sprite_array[9])], 
        "sprite_image":"{}_{}.png".format(MAP_OBJECTS, int(sprite_array[8]) ),
        "sprite_height":int(sprite_array[10]) + (int(sprite_array[11]) * 256)  ,
    }
    
    if "pobject" in single_sprite["sprite_image"]:
        single_sprite["sprite_image"]="{}{}_{}.png".format(MAP_OBJECTS, ( int(sprite_array[6]) + 1 ), int(sprite_array[8]) )
    
    
    return (single_sprite)
    
    
def parse_floor(floor_array):
    """
    Parse a floor definition array into a structured format.
    
    The array format is:
    [scale, skip1, rotation, vertical_distance, vertex_count, skip2,
     x1, y1, skip3, x2, y2, skip4, x3, y3, skip5, x4, y4, skip6]
    
    Returns:
        dict: A dictionary containing parsed floor data
    """
    #print(floor_array)
    #input("Press Enter to continue...")
    
    single_floor = { 
        "floor_scale": floor_array[0], # changed from 1
        "floor_height": floor_array[3],  # vertical_distance in the visualization
        "floor_rotation": floor_array[2],
        "vertex_count": floor_array[4],
        "floor_vertices": [
            {"x": floor_array[6], "y": floor_array[7]},   # First vertex
            {"x": floor_array[9], "y": floor_array[10]},  # Second vertex
            {"x": floor_array[12], "y": floor_array[13]}, # Third vertex
            {"x": floor_array[15], "y": floor_array[16]}  # Fourth vertex
        ],
        "wall_scale_floor_vertices": [
            {"x": floor_array[6] * 32, "y": floor_array[7] * 32},   # First vertex
            {"x": floor_array[9] * 32, "y": floor_array[10] * 32},  # Second vertex
            {"x": floor_array[12] * 32, "y": floor_array[13] * 32}, # Third vertex
            {"x": floor_array[15] * 32, "y": floor_array[16] * 32}  # Fourth vertex
        ],        
        "floor_texture_array": [
            [],
            [],
            [],
            []
        ],
        "floor_texture_name_array": [
            [],
            [],
            [],
            []            
        ],        
        "floor_conf_array": floor_array
    }
    
    return single_floor
    
def parse_wall(wall_array):
    """
    Parse a single wall array of 18 values into a structured dictionary containing wall properties.
    Uses south and east coordinates.
    
    Args:
        wall_array (list): List of 18 integers representing wall properties
        
    Returns:
        dict: Dictionary containing parsed wall properties
    """
    # Input validation
    if len(wall_array) != 18:
        raise ValueError("Wall array must contain exactly 18 values")
    
    # Initialize wall data structure
    single_wall = {
        "tile_count": -1,
        "start_south": -1,
        "start_east": -1,
        "offset_south_per_tile": -1,
        "offset_east_per_tile": -1,
        "offset_south_total": -1,
        "offset_east_total": -1,
        "end_south": -1,
        "end_east": -1,
        "wall_height": -1,
      
        "texture_repeat": -1,
        "wall_config_array": wall_array.copy(),
        "wall_texture_array": [
            [],
            [],
            [],
            []
         ],
        "wall_texture_filenames": [
            [],
            [],
            [],
            []
        ],
    }
    
    # Parse basic values
    single_wall["tile_count"] = wall_array[0]
    
    # Calculate start positions
    single_wall["start_east"] = wall_array[8] + (wall_array[9] * 256)  # values[8,9] are for east
    single_wall["start_south"] = wall_array[10] + (wall_array[11] * 256)  # values[10,11] are for south
    
    # Calculate offsets per tile
    single_wall["offset_east_per_tile"] = (wall_array[2] - 256) if wall_array[3] == 255 else wall_array[2]
    single_wall["offset_south_per_tile"] = (wall_array[4] - 256) if wall_array[5] == 255 else wall_array[4]
    
    # Calculate total offsets
    single_wall["offset_east_total"] = single_wall["offset_east_per_tile"] * single_wall["tile_count"]
    single_wall["offset_south_total"] = single_wall["offset_south_per_tile"] * single_wall["tile_count"]
    
    # Calculate end positions
    single_wall["end_east"] = single_wall["start_east"] + single_wall["offset_east_total"]
    single_wall["end_south"] = single_wall["start_south"] + single_wall["offset_south_total"]
    
    # Calculate wall height
    single_wall["wall_height"] = (wall_array[6] + 256) if wall_array[7] == 255 else wall_array[6]
    single_wall["wall_offset_vertical"] = (wall_array[12] - 256) if wall_array[13] == 255 else wall_array[12]
    
    # Set texture repeat flag
    single_wall["texture_repeat"] = False if wall_array[15] == 255 else True
    
    return single_wall
    




def load_startstop_data():
    """Load data from startstops.json if it exists."""
    try:
        with open(STARTSTOP_FILENAME, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {STARTSTOP_FILENAME} not found.")
        return {}
    except PermissionError as e:
        print(f"Permission error while trying to read {STARTSTOP_FILENAME}: {e}")
        raise

def save_startstop_data(data):
    """Save data to startstops.json, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(STARTSTOP_FILENAME), exist_ok=True)
        with open(STARTSTOP_FILENAME, 'w') as f:
            json.dump(data, f, indent=4)
    except PermissionError as e:
        print(f"Permission error while trying to write to {STARTSTOP_FILENAME}: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error saving to {STARTSTOP_FILENAME}: {e}")
        raise

def number_to_letter(number):
    mapping = {i: chr(97 + i) for i in range(26)}  # 0 -> 'a', 1 -> 'b', ..., 25 -> 'z'
    return mapping.get(number, '?')  # Returns '?' if the number isn't in the mapping

def parse_pcity_blk(original_gamedata):
    file_path = "{}/{}".format(original_gamedata,MAP_BLK)
    try:
        # Get absolute path and verify file exists
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(abs_file_path):
            raise FileNotFoundError(f"File not found at {abs_file_path}")

        results = {}
        
        with open(abs_file_path, 'rb') as file:
            # Read unknown value (16-bit)
            unknown = struct.unpack('<H', file.read(2))[0]
            results['unknown'] = unknown
            
            # Read number of tiles (16-bit)
            num_tiles = struct.unpack('<H', file.read(2))[0]
            results['numTiles'] = num_tiles
            
            # Process each tile
            results['tiles'] = {}
            
            for i in range(num_tiles):
                # Read sprite data (4 x 16-bit values = 8 bytes)
                floor_count, wall_count, possible_sprite_data, sprite_count = struct.unpack('<HHHH', file.read(8))
                
                
                
                full_tile_length= 2* (  (floor_count * 9  ) + (wall_count * 9) + (possible_sprite_data) + ( 6 * sprite_count) )
                
                
                sprite_data = {
                    
                    'floorCount': floor_count,
                    'wallCount': wall_count,
                    'possibleSpriteData': possible_sprite_data,
                    'spriteCount': sprite_count,
                    'ByteID': 4 + (i * 8),
                    "padding":possible_sprite_data,
                    "full_tile_length":full_tile_length
                }
                
                results['tiles'][f'Tile{i + 1}'] = sprite_data
        
        return results
    except Exception as e:
        raise Exception(f"Error parsing file: {str(e)}")


STARTSTOP_FILENAME=""

def parse_full_blk_dict_inner(original_gamedata,output_folder,city):
    
        global MAP_CURRENT_MAP
        MAP_CURRENT_MAP = city
        
        
        pick_map(MAP_CURRENT_MAP)
        
        
        
        global STARTSTOP_FILENAME
        STARTSTOP_FILENAME = "{}/modeldef/startstops_v4_{}.json".format(output_folder,MAP_CURRENT_MAP)  # Ensure it's relative to the current working directory
        write_full_types(original_gamedata,output_folder)     
        ''' This is the one that should work everything out and add it to a dict. '''
        
        # create the dictionary
        full_output_dict= {
                       "main_settings": {
                                "main_setting_array":[],
                                "tile_configs":[],
                                "city_name":MAP_CURRENT_MAP,
                                "start_stop_data":{},
                                "main_data_conf" : {},
                       },
                       "number_of_tiles" : -1,
                       "tiles": {},
                      # The above should track startstops . also full tile data        . need to look at adding tiles to it    
                     }

        # grab startstops
        startstops = load_startstop_data()
        
        
        print(startstops)
        #input("------")
        
        full_output_dict["main_settings"]["start_stop_data"]=startstops
        
        
        #gets the number of tiles etc
        tile_data = parse_pcity_blk(original_gamedata) 
        full_output_dict["main_settings"]["main_data_conf"]=tile_data
        
        #make decimal array
        with open("{}/{}".format(original_gamedata,MAP_BLK), 'rb') as file:
            binary_data = file.read()
            decimal_array = [int(byte) for byte in binary_data]        
        
        tile_length=int (decimal_array[2] )
        full_output_dict["number_of_tiles"]=tile_length
        
        position=2                
        
        #import pdb
        #pdb.set_trace()
        
        texture_outputs={}

        initial_setup_bytes = 4
        tile_count=int(decimal_array[2])
        setup_bytes_length = 4
        two_for_16b = 2
        position_after_tiledefs=(initial_setup_bytes + (setup_bytes_length * ( two_for_16b * tile_count   )))
        current_position=position_after_tiledefs
        
        
        
        # this is for tagging the things, it's probably not needed
        type_value_dict = {
            "Sprite": ["sprite_eastwest", "sprite_northsouth", "sprite_move_vertical", "sprite_firstpart", "sprite_texture", "sprite_resize_vertical"],
            "fourv_Floor": ["resize_floor", "floorheight_rotate", "vertex_count", "vertex_move", "vertex_move", "vertex_move","vertex_move","vertex_move","vertex_move"],
            "Floor_textures": ["floor_texture"],
            "wall_texture": ["wall_texture"],
            "Clear":["clear"],
            "wall_def":["block_count","rotation","rotation","resizevertical","movenorthsouth","rotation","updown","unknown","unknown"],
            "total_tiles":["tile_count"],
            "tile_setup":["floor_count","wall_count","unknown_variable","sprite_count"]
        }	
        
        
        
        tile_startstops={}
        #startstop_data = load_startstop_data()
        
        
        limited_tile_data={}
        tile_countup=1
        while tile_countup < ( tile_count + 1):
            
            
            individual_tile={
                 "start_stops"  :        [ full_output_dict["main_settings"]["start_stop_data"][str(tile_countup)]["start"] , full_output_dict["main_settings"]["start_stop_data"][str(tile_countup)]["stop"] ],
                 "floors":               [],
                 "walls" :               [],
                 "full_tile_decimals":   [],
                 "sprites":              [],
                 "bunch_of_crap":        {}
            }            
            
            start_pos = full_output_dict["main_settings"]["start_stop_data"][str(tile_countup)]["start"]
            
            number_of_floors=tile_data["tiles"]["Tile{}".format(tile_countup)]["floorCount"]
            number_of_walls=tile_data["tiles"]["Tile{}".format(tile_countup)]["wallCount"]
            number_of_sprites=tile_data["tiles"]["Tile{}".format(tile_countup)]["spriteCount"]   


            length_of_floors=tile_data["tiles"]["Tile{}".format(tile_countup)]["floorCount"]*18
            length_of_walls=tile_data["tiles"]["Tile{}".format(tile_countup)]["wallCount"]*18
            length_of_sprites=tile_data["tiles"]["Tile{}".format(tile_countup)]["spriteCount"]*12             
            length_of_texture_data = tile_data["tiles"]["Tile{}".format(tile_countup)]["possibleSpriteData"] * 2           
            
            floor_def_position=start_pos
            wall_def_position=start_pos+length_of_floors
            texture_def_position=start_pos+length_of_floors+length_of_walls
            sprite_def_position=start_pos+length_of_floors+length_of_walls+length_of_texture_data
            
            individual_tile["bunch_of_crap"]=            { # just for previewing. Don't edit these
            
               "number_of_sprites": number_of_sprites,
               "length_of_sprites":length_of_sprites,
               "floor_def_position": floor_def_position,
               "wall_def_position":wall_def_position,
               "length_of_texture_data":length_of_texture_data,
               "texture_def_position":texture_def_position,
               "sprite_def_position":sprite_def_position,
            }
            
            
            #print(length_of_walls)
            #print(number_of_walls)
            #pdb.set_trace()
            
            
            floorcountup=0
            if number_of_floors >0:
                while floorcountup < number_of_floors:
                    floor_start=start_pos+(floorcountup * 18)
                    floor_array = decimal_array[floor_start:floor_start + 18]
                    floor_dict=parse_floor(floor_array)
                    floor_dict["floor_start"]=floor_start
                   
                    #print(floor_dict)
                    
                    #print("----")
                    #print( individual_tile)
                   
                    #print("----")
                    #pdb.set_trace()
                    individual_tile["floors"].append(floor_dict)
                    #print(floorcountup)
                    floorcountup=floorcountup+1
            
            wallcountup=0
            if length_of_walls >0:
                while wallcountup < number_of_walls:
                    wall_start=start_pos+(18 * number_of_floors)+(18*wallcountup)
                    wall_array = decimal_array[wall_start:wall_start + 18]
                    wall_dict=parse_wall(wall_array)
                    wall_dict["wall_start"]=wall_start
                    #print(wall_dict)
                    
                    #print("----")
                    #print( individual_tile)
                   
                    #print("----")
                    #pdb.set_trace()
                    individual_tile["walls"].append(wall_dict)
                    
                    #print(wallcountup)
                    wallcountup=wallcountup+1            
            
            
            spritecountup=0
            if length_of_sprites >0:
                while spritecountup < number_of_sprites:
                    sprite_start=sprite_def_position+(spritecountup * 12)
                    sprite_array = decimal_array[sprite_start:sprite_start + 12]
                    sprite_dict=parse_sprite(sprite_array)
                   
                    #print(sprite_dict)
                    sprite_dict["sprite_start"]=sprite_start
                    #print("----")
                    #print( individual_tile)
                   
                    #print("----")
                    #pdb.set_trace()
                    individual_tile["sprites"].append(sprite_dict)
                    #print(spritecountup)
                    spritecountup=spritecountup+1              
            
            #add it in to the main readout
            full_output_dict["tiles"][tile_countup]  =  individual_tile  
            
            
            
            
            # Ok so now we need to grab the textures for the walls and the floors.
            
            # we need to go back to the start of this data, so texture_def_position
            #print(individual_tile["bunch_of_crap"])
            
            #print(texture_def_position)
            #input("Press Enter to continue...")
            #pdb.set_trace()
            
            loop=0
            current_texture_position=texture_def_position
            
            while loop <4:
                floor_texture_countup=0
                wall_texture_countup=0

                while floor_texture_countup < number_of_floors:
                    #individual_tile[][]
                    #full_output_dict["tiles"][tile_countup]["floors"][floor_texture_countup].append("x")
                    full_output_dict["tiles"][tile_countup]["floors"][floor_texture_countup]["floor_texture_array"][loop]= decimal_array[current_texture_position:current_texture_position + 2]
                    full_output_dict["tiles"][tile_countup]["floors"][floor_texture_countup]["floor_texture_name_array"][loop]="{}_{}.gif".format(MAP_FLOORS,number_to_letter(decimal_array[current_texture_position+1]))
                    current_texture_position=current_texture_position+2
                    floor_texture_countup=floor_texture_countup+1
                    
                    
                while wall_texture_countup < number_of_walls:
                    #individual_tile[][]
                    this_wall_texture_length=0
                    this_wall_texture_loops=full_output_dict["tiles"][tile_countup]["walls"][wall_texture_countup]["texture_repeat"]
                    #print(this_wall_texture_loops)
                    #input("check the above")
                    if this_wall_texture_loops == False:
                        this_wall_texture_length=full_output_dict["tiles"][tile_countup]["walls"][wall_texture_countup]["tile_count"]
                    elif this_wall_texture_loops == True:    
                        this_wall_texture_length=1
                    else:
                        print("something has broken here")
                        input("check the above")
                    #this_wall_texture_length=
                    individual_wall_texture_countup=0
                    while individual_wall_texture_countup < this_wall_texture_length:
                        #full_output_dict["tiles"][tile_countup]["walls"][wall_texture_countup]["wall_texture_array"][loop].append(decimal_array[current_texture_position:current_texture_position + (2*this_wall_texture_length)])     

                        full_output_dict["tiles"][tile_countup]["walls"][wall_texture_countup]["wall_texture_array"][loop].append([decimal_array[current_texture_position],decimal_array[current_texture_position+1] ]) 
                        full_output_dict["tiles"][tile_countup]["walls"][wall_texture_countup]["wall_texture_filenames"][loop].append("{}{}_{}.png".format(MAP_WALLS,decimal_array[current_texture_position] +1 , decimal_array[current_texture_position+1] )) 
                        
                        current_texture_position=current_texture_position+2
                        individual_wall_texture_countup=individual_wall_texture_countup+1
                  
                    #full_output_dict["tiles"][tile_countup]["walls"][floor_texture_countup]["floor_texture_array"][loop]= decimal_array[current_texture_position:current_texture_position + 2]
                    #full_output_dict["tiles"][tile_countup]["walls"][floor_texture_countup]["floor_texture_name_array"][loop]="kfloor_{}.gif".format(number_to_letter(decimal_array[current_texture_position+1]))
                    
                    wall_texture_countup=wall_texture_countup+1            

                loop=loop+1
            tile_countup=tile_countup+1
            
        
        
        print(full_output_dict)
        with open('{}/modeldef/tile_config_{}.json'.format(output_folder,MAP_CURRENT_MAP), 'w') as f:
            json.dump(full_output_dict, f) 
            
        #return(full_output_dict)
        #return JSONResponse(content=full_output_dict)
        
        
        
        
def write_full_types(original_gamedata,output_folder): # This is an old script. note that I changed the way that the wall textures are being read.
        print("attempting to write full types")
        startstops = load_startstop_data()
        tile_data = parse_pcity_blk(original_gamedata)       
        position=2
        print(tile_data)
        
        texture_outputs={}
        print()
        
       # number of tiles = 
        
        with open("{}/{}".format(original_gamedata,MAP_BLK), 'rb') as file:
            binary_data = file.read()
            decimal_array = [int(byte) for byte in binary_data]
        
        return_value=decimal_array[2]
        
        #-----------
        initial_setup_bytes = 4
        tile_count=int(decimal_array[2])
        setup_bytes_length = 4
        two_for_16b = 2
        position_after_tiledefs=(initial_setup_bytes + (setup_bytes_length * ( two_for_16b * tile_count   )))
        current_position=position_after_tiledefs
        
        
        
        
        type_value_dict = {
            "Sprite": ["sprite_eastwest", "sprite_northsouth", "sprite_move_vertical", "sprite_firstpart", "sprite_texture", "sprite_resize_vertical"],
            "fourv_Floor": ["resize_floor", "floorheight_rotate", "vertex_count", "vertex_move", "vertex_move", "vertex_move","vertex_move","vertex_move","vertex_move"],
            "Floor_textures": ["floor_texture"],
            "wall_texture": ["wall_texture"],
            "Clear":["clear"],
            "wall_def":["block_count","rotation","rotation","resizevertical","movenorthsouth","rotation","updown","unknown","unknown"],
            "total_tiles":["tile_count"],
            "tile_setup":["floor_count","wall_count","unknown_variable","sprite_count"]
        }	
        
        
        
        
        tile_countup=1
        tile_startstops={}
        startstop_data = load_startstop_data()
        
        
        
        try:
            # Load existing v2 notes
            with open('{}/modeldef/byte_notes_v4_{}.json'.format(output_folder,MAP_CURRENT_MAP), 'r') as f:
                    notes_v2 = json.loads(f.read())
        except FileNotFoundError:
            notes_v2 = {}
            
        
        while tile_countup < ( tile_count + 1):
            
            texture_outputs[tile_countup]={}
            time_length =    tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["full_tile_length"]    
            
            
            tile_startstops[tile_countup]={}
            tile_startstops[tile_countup]["start"]=current_position
            tile_startstops[tile_countup]["stop"]=(current_position  +time_length )-1
            current_position=current_position+time_length
            
            #set_startstops(tile_countup, tile_startstops[tile_countup]["start"], tile_startstops[tile_countup]["stop"])
                                
            startstop_data[tile_countup] = {"start": tile_startstops[tile_countup]["start"], "stop": tile_startstops[tile_countup]["stop"]}
            
            #setting the floor tiles
            floor_tile_countup=0
            
            
            position=tile_startstops[tile_countup]["start"]
            print("tile {} {}".format(tile_countup,  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   ))
            while floor_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   :
                    i=0
                    while i< 9:
                        notes_v2[str(position)] = type_value_dict["fourv_Floor"][i]
                        position=position+2
                        i=i+1
                    floor_tile_countup=floor_tile_countup+1
                    
            wall_tile_countup=0   

            walltexture_lengths=[]
            # this is where we grab the wall texture length as it is the first id

            while wall_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["wallCount"]   :
                    i=0
                    walltexture_lengths.append(int(decimal_array[position]))
                    
                    while i< 9:
                        notes_v2[str(position)] = type_value_dict["wall_def"][i]
                        #this is where we grab that sneaky line that sets a tile to repeat. you might need to fix this later on when you do the parsing script
                        if i == 7:
                            #then we need to check the value after this and if it is 0 then the set most recent walltexture_lengths to 0
                            #import pdb
                            #pdb.set_trace()
                            if decimal_array[position+1]==0:
                                print("it's a looping texture!")
                                walltexture_lengths[-1]=1
                        position=position+2
                        i=i+1
                    wall_tile_countup=wall_tile_countup+1            
            
            # this is to come back to it later
            sprite_position=position+     (  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["padding"] *2 )
            
            
            print(walltexture_lengths)
            texture_outputs[tile_countup]["walls"]={}
            # needs to the floor and wall textures.
            
            
            #loop1
            floor_tile_countup=0
            while floor_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   :
                    notes_v2[str(position)] = type_value_dict["Floor_textures"][0]
                    position=position+2
                    floor_tile_countup=floor_tile_countup+1            
            wall_tile_countup=0
            texture_outputs[tile_countup]["walls"]["loop1"]={}
            while wall_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["wallCount"]   :
                j=0
                texture_outputs[tile_countup]["walls"]["loop1"]["wall{}".format(wall_tile_countup)]=[]
                while j <   walltexture_lengths[wall_tile_countup]:  
                    texture_outputs[tile_countup]["walls"]["loop1"]["wall{}".format(wall_tile_countup)].append("{}/{}{}_{}.png".format(  MAP_WALLS,MAP_WALLS,(decimal_array[position]+1)  ,decimal_array[position+1]  ))
                    notes_v2[str(position)] = type_value_dict["wall_texture"][0]
                    position=position+2
                    j=j+1
                wall_tile_countup=wall_tile_countup+1                 
            
             #loop2
            floor_tile_countup=0
            while floor_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   :
                    notes_v2[str(position)] = type_value_dict["Floor_textures"][0]
                    position=position+2
                    floor_tile_countup=floor_tile_countup+1            
            wall_tile_countup=0
            texture_outputs[tile_countup]["walls"]["loop2"]={}
            while wall_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["wallCount"]   :
                j=0
                texture_outputs[tile_countup]["walls"]["loop2"]["wall{}".format(wall_tile_countup)]=[]
                while j <   walltexture_lengths[wall_tile_countup]: 
                    
                    notes_v2[str(position)] = type_value_dict["wall_texture"][0]
                    
                    texture_outputs[tile_countup]["walls"]["loop2"]["wall{}".format(wall_tile_countup)].append("{}/{}{}_{}.png".format(  MAP_WALLS,MAP_WALLS,(decimal_array[position]+1)  ,decimal_array[position+1]  ))
                    position=position+2
                    j=j+1
                wall_tile_countup=wall_tile_countup+1                   
            
            #loop3
            floor_tile_countup=0
            while floor_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   :
                    notes_v2[str(position)] = type_value_dict["Floor_textures"][0]
                    position=position+2
                    floor_tile_countup=floor_tile_countup+1            
            wall_tile_countup=0
            texture_outputs[tile_countup]["walls"]["loop3"]={}
            while wall_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["wallCount"]   :
                j=0
                texture_outputs[tile_countup]["walls"]["loop3"]["wall{}".format(wall_tile_countup)]=[]
                while j <   walltexture_lengths[wall_tile_countup]:  
                    notes_v2[str(position)] = type_value_dict["wall_texture"][0]
                    texture_outputs[tile_countup]["walls"]["loop3"]["wall{}".format(wall_tile_countup)].append("{}/{}{}_{}.png".format(  MAP_WALLS,MAP_WALLS,(decimal_array[position]+1)  ,decimal_array[position+1]  ))
                    
                    position=position+2
                    j=j+1
                wall_tile_countup=wall_tile_countup+1                   
            
            #loop4
            floor_tile_countup=0
            while floor_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   :
                    notes_v2[str(position)] = type_value_dict["Floor_textures"][0]
                    
                    position=position+2
                    floor_tile_countup=floor_tile_countup+1            
            wall_tile_countup=0
            
            
            texture_outputs[tile_countup]["walls"]["loop4"]={}
            while wall_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["wallCount"]   :
                j=0
                #texture_outputs[tile_countup]["walls"]={}
                texture_outputs[tile_countup]["walls"]["loop4"]["wall{}".format(wall_tile_countup)]=[]
                while j <   walltexture_lengths[wall_tile_countup]:  
                    notes_v2[str(position)] = type_value_dict["wall_texture"][0]
                    
                    texture_outputs[tile_countup]["walls"]["loop4"]["wall{}".format(wall_tile_countup)].append("{}/{}{}_{}.png".format(  MAP_WALLS,MAP_WALLS,(decimal_array[position]+1)  ,decimal_array[position+1]  ))
                    
                    
                    position=position+2
                    j=j+1
                wall_tile_countup=wall_tile_countup+1                     
            
            
            #  #loop5
            #floor_tile_countup=0
            #while floor_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["floorCount"]   :
            #        notes_v2[str(position)] = type_value_dict["Floor_textures"][0]
            #        
            #        position=position+2
            #        floor_tile_countup=floor_tile_countup+1            
            #wall_tile_countup=0
            #
            #
            #texture_outputs[tile_countup]["walls"]["loop5"]={}
            #while wall_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["wallCount"]   :
            #    j=0
            #    #texture_outputs[tile_countup]["walls"]={}
            #    texture_outputs[tile_countup]["walls"]["loop5"]["wall{}".format(wall_tile_countup)]=[]
            #    while j <   walltexture_lengths[wall_tile_countup]:  
            #        notes_v2[str(position)] = type_value_dict["wall_texture"][0]
            #        
            #        texture_outputs[tile_countup]["walls"]["loop5"]["wall{}".format(wall_tile_countup)].append("{}/{}{}_{}.png".format(  MAP_WALLS,MAP_WALLS,(decimal_array[position]+1)  ,decimal_array[position+1]  ))
            #        
            #        
            #        position=position+2
            #        j=j+1
            #    wall_tile_countup=wall_tile_countup+1           
            
            
            
            
            position=sprite_position
            sprite_tile_countup=0              
            while sprite_tile_countup <  tile_data ["tiles"]["Tile{}".format(tile_countup)]  ["spriteCount"]   :
                    i=0
                    while i< 6:
                        notes_v2[str(position)] = type_value_dict["Sprite"][i]
                        position=position+2
                        i=i+1
                    sprite_tile_countup=sprite_tile_countup+1              
            
            
            

            tile_countup = tile_countup+1
        
        
        save_startstop_data(startstop_data)
        
        # Save updated notes to v2 file
        with open('{}/modeldef/byte_type_v4_{}.json'.format(output_folder,MAP_CURRENT_MAP), 'w') as f:
            json.dump(notes_v2, f)        
        
        # setting the startstops
        
        #for each in tile_startstops:
        #   #set_startstops(tile_num: int, start: int, stop: int):
            
        
        print(tile_startstops)
        #input("------------")
        
    
        '''
        check length fropm dict
        get the 
        
        it needs to be setting them too, but first tryt the startstop and see if that works
        
        
        
        '''        
        
if __name__ == "__main__":
    original_gamedata="C:/2025_projects/Quarantine_fullsetRENAMETEST/test4git/Original_Game"
    output_folder="C:/2025_projects/Quarantine_fullsetRENAMETEST/test4git/output"
    
    

    
    pass        
        
        
#pick_map(MAP_CURRENT_MAP)        
#write_full_types()        
#parse_full_blk_dict_inner("test","C:/2025_projects/Quarantine_fullset/output/")        