
import os
import string
import shutil
import json
from PIL import Image



def initialize_tracking_file(output_folder):
    tracking_file = os.path.join(output_folder, "doom", "doomid_tracking.json")
    with open(tracking_file, "w") as f:
        json.dump({"next_wall_id": 10000,"next_object_id": 20000, "wall_name_mapping": {}, "object_name_mapping": {}}, f)
    print(f"Tracking file initialized at {tracking_file}")
  

def generate_decorate(output_folder, wall, preceding_doomid):
    tracking_file = os.path.join(output_folder, "doom", "doomid_tracking.json")
    os.makedirs("{}/doom/decorate".format(output_folder), exist_ok=True)
    

    # Load the tracking file
    if os.path.exists(tracking_file):
        with open(tracking_file, "r") as f:
            tracking_dict = json.load(f)
    else:
        tracking_dict = {"next_wall_id": 1000, "wall_name_mapping": {}}

    next_wall_id = tracking_dict["next_wall_id"]
    wall_name_mapping = tracking_dict["wall_name_mapping"]
    entries = []
    wall_sprite_folder = f"{output_folder}/sprites/walls/{wall.lower()}"
    print(wall_sprite_folder)
    #input("wall_sprite_folder")

    # Get all PNG files from the directory
    for filename in sorted(os.listdir(wall_sprite_folder)):
        if filename.endswith(".png"):
            base_name = filename[:-4]  # Remove .png extension
            parts = base_name.split('_')

            if len(parts) == 2 and parts[0].startswith(wall):
                formatted_number = next_wall_id
                next_wall_id += 1

                # Save the base_name to formatted_number mapping
                wall_name_mapping[base_name] = formatted_number

                actor_entry = f"""
actor {base_name} {formatted_number}
{{
    +NOGRAVITY
    Radius 32
    Height 32
    +SOLID
    +SHOOTABLE
    +NODAMAGE
    +NOGRAVITY
    +NOBLOOD
    -CANPASS
    States
    {{
    Spawn:
        POSS A -1
        Stop
    }}
}}
                """.strip()

                entries.append(actor_entry)

    with open(f'{output_folder}/doom/decorate/wall_decorate_{wall.lower()}', 'w') as f:
        f.write("\n\n".join(entries))

    # Update the tracking file with the next available number and base_name mappings
    tracking_dict["next_wall_id"] = next_wall_id
    tracking_dict["wall_name_mapping"] = wall_name_mapping
    with open(tracking_file, "w") as f:
        json.dump(tracking_dict, f, indent=4)


# Endpoint to generate modeldef file

def generate_modeldef(output_folder,wall):
    os.makedirs("{}/doom/modeldef".format(output_folder), exist_ok=True)
    entries = []
    wall_folder="{}/sprites/walls/{}".format(output_folder,wall.lower())
    print(wall_folder)
    #input("---?----")
    # Get all PNG files from the directory
    for filename in sorted(os.listdir(wall_folder)):
        if filename.endswith(".png"):
            base_name = filename[:-4]  # Remove .png extension

            modeldef_entry = f"""
Model {base_name}
{{
    Path "models"
    Model 0 "fplane.md3"
    scale 65.0 65.0 65.0
    Skin 0 "walls\\{wall}\\{base_name}.png  "
    FrameIndex POSS A 0 0
}}
 """.strip()

            entries.append(modeldef_entry)
            
    #print(modeldef_entry)    
    #input(" check this ")
            

    with open('{}/doom/modeldef/modeldef_{}'.format(output_folder,wall), 'w') as f:
        f.write("\n\n".join(entries))



def combine_modeldefs(output_folder):
    modeldef_dir = os.path.join(output_folder, "doom", "modeldef")
    combined_file = os.path.join(modeldef_dir, "modeldef_combined.txt")

    # List of specific files to combine
    files_to_combine = [
        "modeldef_JWALL.txt",
        "modeldef_KWALL.txt",
        "modeldef_PWALL.txt",
        "modeldef_SWALL.txt",
        "modeldef_WALL.txt",
        "modeldef_WWALL.txt"
    ]

    # Ensure the modeldef directory exists
    if not os.path.exists(modeldef_dir):
        print(f"Error: Directory '{modeldef_dir}' does not exist.")
        return

    # Overwrite (or create) modeldef_combined.txt
    with open(combined_file, "w") as combined:
        for filename in files_to_combine:
            file_path = os.path.join(modeldef_dir, filename)

            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    combined.write(f.read() + "\n\n")  # Add spacing between files
            else:
                print(f"Warning: {filename} not found, skipping.")

    print(f"Combined modeldef files into {combined_file}")


def number_to_letter(num):
    if 0 <= num <= 25:
        return chr(ord('A') + num)
    raise ValueError(f"Number {num} out of range (0-25)")

def number_to_two_letters(num):
    first_digit = num // 10
    second_digit = num % 10
    return number_to_letter(first_digit) + number_to_letter(second_digit)

def rename_files(output_folder, obj, preceding_doomid, sprite_start_char):
    
    
    tracking_file = os.path.join(output_folder, "doom", "doomid_tracking.json")
    if os.path.exists(tracking_file):
        with open(tracking_file, "r") as f:
            tracking_dict = json.load(f)
    else:
        tracking_dict = {"next_object_id": 5000, "object_name_mapping": {}}
    
    next_object_id = tracking_dict["next_object_id"]
    object_name_mapping = tracking_dict["object_name_mapping"]
    
    input_path = f"{output_folder}/sprites/objects/{obj}"
    output_path = f"{output_folder}/doom/objects/{obj}"
    os.makedirs(output_path, exist_ok=True)

    files = [f for f in os.listdir(input_path) if f.endswith(".png")]
    files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    
    actor_entries = []
    
    for file in files:
        # Get original name without extension
        original_name = file.replace(".png", "")
        
        
        # Get the file path
        file_path = os.path.join(input_path, file)
        
        # Get the size of the file in bytes
        file_size = os.path.getsize(file_path)
        # Open the image to get the width and height (x, y size)
        with Image.open(file_path) as img:
            width, height = img.size
        
        # Now, you have the width and height of the image
        print(f"File: {file}, Width: {width}, Height: {height}")
        
        if height < 25 and width > height:
            blocking="-"
            non_blocking="+"
        elif height < 20: 
            blocking="-"   
            non_blocking="-"        
        else:
            blocking="+"
            non_blocking="-"
        #input("----")
        
        # Get number after underscore
        number_after_underscore = int(original_name.split("_")[1])
        
        # Get number before underscore (if exists)
        name_parts = original_name.split("_")[0]
        number_before_underscore = None
        for char in name_parts:
            if char.isdigit():
                number_before_underscore = int(char)
                break
                
        # Generate new name
        third_letter = number_to_letter(number_before_underscore) if number_before_underscore is not None else 'Z'
        last_two_letters = number_to_two_letters(number_after_underscore)
        new_name = f"{sprite_start_char}O{third_letter}{last_two_letters}"
        
        # Get the base name (without the last letter) and frame letter for state
        base_name = f"{sprite_start_char}O{third_letter}{last_two_letters[0]}"
        frame_letter = last_two_letters[1]
        
        # Copy file
        source = os.path.join(input_path, file)
        dest = os.path.join(output_path, f"{new_name}0.png")
        shutil.copy(source, dest)
        print(f"Copied: {source} -> {dest}")
        
        # Assign and increment ID
        formatted_number = next_object_id
        next_object_id += 1
        # Save the mapping
        object_name_mapping[original_name] = formatted_number
        
        # Fix for objects that you should be able to pass
        
        
        
        actor_entry = f"""actor {original_name} {formatted_number}
{{    
    +NOGRAVITY
    Radius 20
    Height 53
    {blocking}SOLID
    {blocking}SHOOTABLE
    +NODAMAGE
    +NOBLOOD
    +NOGRAVITY
    {non_blocking}CANPASS
    States
    {{
    Spawn:
        {base_name} {frame_letter} -1
        Stop
    }}
}}"""
        actor_entries.append(actor_entry)
    
    # Write DECORATE file
    decorate_path = f'{output_folder}/doom/decorate/obj_decorate_{obj.lower()}'
    with open(decorate_path, 'w') as f:
        f.write("\n\n".join(actor_entries))
        
    # Save updated tracking info
    tracking_dict["next_object_id"] = next_object_id
    tracking_dict["object_name_mapping"] = object_name_mapping
    with open(tracking_file, "w") as f:
        json.dump(tracking_dict, f, indent=4)        
        
## Endpoint to rename files - I think this is the one for kobjects
##@app.post("/rename_files/")
#def rename_files(output_folder,obj,preceding_doomid,sprite_start_chars):
#    
#    #C:\2025_projects\Quarantine_fullset\output\sprites\objects\obj
#    input_object_path="{}/sprites/objects/{}".format(output_folder,obj)
#    output_object_path="{}/doom/objects/{}".format(output_folder,obj)
#    os.makedirs(output_object_path, exist_ok=True)
#    #files = [f for f in os.listdir(object_path) if f.startswith("kobject1_") and f.endswith(".png")]
#    files = [f for f in os.listdir(input_object_path) ]
#    files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
#
#    letters = string.ascii_uppercase
#    index = 0
#    actor_entries = []
#
#    for i in range(len(letters)):
#        for j in range(len(letters)):
#            if index >= len(files):
#                break
#
#            original_name = files[index].replace(".png", "")
#            num_part = int(original_name.split("_")[1])
#            # This needs to take the first 3 letters and split it there. That shouldn't cause an issue for the ones that are pbjects/pobject, but it will for object
#            new_sprite_name = f"{sprite_start_chars}{letters[i]}{letters[j]}"
#
#            old_path = os.path.join(input_object_path, files[index])
#            new_path = os.path.join(output_object_path, f"{new_sprite_name}0.png")
#
#            shutil.copy(old_path, new_path)
#            print(f"Copied: {old_path} -> {new_path}")
#
#            actor_entries.append(f"actor {original_name} {preceding_doomid}00{num_part:02d} \n{{\n    +NOGRAVITY\n    Radius 20\n    Height 53\n    +SOLID\n    +SHOOTABLE\n    +NODAMAGE\n    +NOBLOOD\n    -CANPASS\n    States\n    {{\n    Spawn:\n        {new_sprite_name[:-1]} {new_sprite_name[4]} -1\n        Stop\n    }}\n}}\n")
#
#            index += 1
#
#    # Return the generated content as a JSON response
#    #return JSONResponse(content={"actor_file": "\n\n".join(actor_entries)})
#    with open('{}/doom/decorate/obj_decorate_{}.txt'.format(output_folder,obj.lower()), 'w') as f:
#        f.write("\n\n".join(actor_entries))




if __name__ == "__main__":
    #DONT RUN THIS LIKE THIS AS IT WILL MESS UP THE NUMBERS IN TRACKING
    #output_folder="C:/2025_projects/Quarantine_fullset/output"
    #rename_files(output_folder,"jobjects",6,"J")
    pass

else:
    print("Script has been imported.")

