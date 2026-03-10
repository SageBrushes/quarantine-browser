import json
from pprint import pprint
import math

def load_definition_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)
        
        
        
# needs to load  file:///C:/2025_projects/Quarantine_fullset/output/doom/doomid_tracking.json and then build a new one that has them all combined, or has two - one with the walls and one with thge items. it should then go into acs which is compiled
#btw you need to put the modeldef stuff into one file as zandronum doesnt like it when imported from a folder.






def make_json_output( object_pre_num, city,output_folder):
    
    # Load the tile configuration data
    #output_folder="C:/2025_projects/Quarantine_fullset/output"
    
        

    acs_map_text=""
    
   
    
    tile_config = load_definition_data(f'{output_folder}/modeldef/tile_config_{city}.json')

    json_output = []
    json_output.append([])
    
    if city == "jcity":
        floor_letter="j"
    elif city== "pcity":
        floor_letter="p"        
    elif city== "kcity":
        floor_letter="k"        
    elif city== "scity":
        floor_letter="s"        
    elif city== "wcity":
        floor_letter="w"        
    elif city== "city":
        floor_letter="z"        
  
        
    for tile in tile_config["tiles"]:
        
        acs_map_text = acs_map_text + f'script "{city}_tile_{tile}" (int db_tile_id,  int tile_player, int test3) \n{{\n'
        
        acs_map_text = acs_map_text + f'    //offsets\n'
        acs_map_text = acs_map_text + f'    int offset_x=((db_tile_id % 100) - 1) * 512 - 25600;\n'
        acs_map_text = acs_map_text + f'    int offset_y=25600 - (((db_tile_id / 100) + 1) * 512);\n\n'
        
        
        acs_map_text = acs_map_text + f"    //Set floor tile: \n"
        acs_map_text = acs_map_text +f'    ChangeFloor(db_tile_id, "{floor_letter}_f_{tile}");\n\n '
        
        this_tile_values=tile_config["tiles"][tile]

        print(this_tile_values.keys())
        print(len(this_tile_values))
        
        this_tile_additions=[]
        acs_map_text = acs_map_text + f"    //sprites: \n"
        for sprite in this_tile_values["sprites"]:
            acs_map_text = acs_map_text + f'    Spawnforced( "{sprite["sprite_image"].replace(".png","")}", ({sprite["sprite_x"]}+offset_x)<<16, ({512-sprite["sprite_y"]}+offset_y)<<16, ({20+sprite["sprite_z"]})<<16, db_tile_id, 0);\n'

        acs_map_text = acs_map_text + f"\n    //walls: \n"




        tile_width = 512
        tile_height = 512

        #walldefs = map_definitions.get("walls", [])
        for wall in this_tile_values["walls"]:
            print(wall)
            tile_count = wall["tile_count"]
            start_x = wall["start_east"] 
            start_y = (512 - wall["start_south"]) 
            end_x = wall["end_east"] 
            end_y = (512 - wall["end_south"])

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
                    reverse_index = tile_count - 1 - i  # Reverse the index order
                    if reverse_index < len(wall["wall_texture_filenames"][0]):
                        wall_texture = wall["wall_texture_filenames"][0][reverse_index].replace(".png", "")
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
                #type_value = tracking_dict["wall_name_mapping"][wall_texture]



                z = (-(wall["wall_offset_vertical"] )+20)*0.85
                # Fix for the heights being weird in Doom
                #if z == 64:
                #    z = 54

                # Calculate the actual width of the wall tile
                width = math.sqrt((step_x ** 2) + (step_y ** 2))
                size_key = (width, wall["wall_height"])



                ## Add the actor for the wall tile
                #add_actor(
                #    name=wall_texture,
                #    x=center_x,
                #    y=center_y,
                #    z=z,  # Assuming the actor's z position is half the wall height
                #    angle=round(angle_deg),  # Angle of the wall
                #    #type=type_value,
                #    scalex = width/64,
                #    scaley = wall["wall_height"]/64
                #)    
      
                #acs_map_text = acs_map_text + f'    Spawn( "mapspot", ({int(center_x)}+offset_x)<<16, ({int(center_y)}+offset_y)<<16, {int(z)}<<16, 9999, {round((angle_deg/360) * 256)});\n'
                #acs_map_text = acs_map_text + f'    SpawnSpotForced ("{wall_texture}", 9999, db_tile_id,  {round((angle_deg/360) * 256)});\n'
                #acs_map_text = acs_map_text + f'    Thing_Remove(9999);\n'
               
                #acs_map_text = acs_map_text + f'    Spawn( "{wall_texture}", {center_x}<<16, {center_y}<<16, {z}<<16, 500, {round((angle_deg/360) * 256)});\n'
                
                scalex = width/64
                scaley = wall["wall_height"]/64
                
                if scalex ==1 and scaley ==1:
                    acs_map_text = acs_map_text + f'    Spawnforced( "{wall_texture}", ({int(center_x)}+offset_x)<<16, ({ int(center_y)}+offset_y)<<16, {int(z)}<<16, db_tile_id, {round((angle_deg/360) * 256)});\n' 
                else:
                    acs_map_text = acs_map_text + f'    Spawnforced( "{wall_texture}", ({int(center_x)}+offset_x)<<16, ({ int(center_y)}+offset_y)<<16, {int(z)}<<16, 30000, {round((angle_deg/360) * 256)});\n' 
                    if scalex !=1:
                        acs_map_text = acs_map_text + f'     SetActorProperty(30000, APROP_ScaleX, {scalex});\n' 
                    if scaley !=1:
                        acs_map_text = acs_map_text + f'     SetActorProperty(30000, APROP_Scaley, {scaley});\n' 
                    acs_map_text = acs_map_text + f'     Thing_ChangeTID(30000,db_tile_id );\n'    
                   




    
 
        acs_map_text = acs_map_text + f" }} \n\n"
    
    
    

    
    

    with open(f'{output_folder}/acs/{city}tile.acs', 'w') as outfile:
        outfile.write(acs_map_text)

    
#def create_walls_from_sprites(map_definitions, udmf_map, offset_x, offset_y, tile_index,object_pre_num , wall_pre_num,tracking_dict):

def custom_angle_to_byte(custom_angle):
    # Convert based on custom angle input
    if custom_angle == 0:
        return 0     # East
    elif custom_angle == 1:
        return 64    # South
    elif custom_angle == 2:
        return 128   # West
    elif custom_angle == 3:
        return 192   # North
    else:
        return 0     # Default to East if invalid input


#make_json_output("j",  "jcity")