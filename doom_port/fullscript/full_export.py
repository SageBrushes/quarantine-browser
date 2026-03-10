import os
import logging
import io
from tqdm import tqdm
from contextlib import redirect_stdout
from modules.describeIMG import convert_to_gif, splitfloors
from modules.export_sprites import export_sprites
from modules.parse_talking import parse_talking
from modules.modelparser import parse_full_blk_dict_inner
from modules.doom_floors import create_floor_images
from modules.doom_modeldefs import generate_modeldef, combine_modeldefs, generate_decorate, rename_files, initialize_tracking_file
from modules.udmf import make_udmf
from modules.udmf_for_acs6 import make_json_output
from modules.make_maptiles_arrays import create_maptiles_for_acs

# ------ CONFIG ------
current_working_directory = os.path.normpath(os.getcwd()).replace("\\", "/")

#original_gamedata = "C:/2025_projects/Quarantine_fullset/Original_Game"
#output_folder = "C:/2025_projects/Quarantine_fullset/output"

original_gamedata = f"{current_working_directory}/Original_Game"
output_folder = f"{current_working_directory}/output"


print(original_gamedata)
print(output_folder)


# ------ Logging Setup ------
logging.basicConfig(
    filename="process.log", 
    level=logging.ERROR, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------ Progress Bar Wrapper ------
def run_task(task_name, func, *args):
    """Runs a function while suppressing stdout unless an error occurs."""
    try:
        with tqdm(total=1, desc=task_name, position=0, leave=True) as pbar:
            f = io.StringIO()
            with redirect_stdout(f):  # Suppress prints
                func(*args)
            pbar.update(1)
    except Exception as e:
        error_output = f.getvalue()  # Capture suppressed output
        logging.error(f"Error in {task_name}: {str(e)}\n{error_output}", exc_info=True)
        print(f"❌ Error in {task_name} — Check process.log for details.")
        print(error_output)  # Show the suppressed output only if there's an error

# ------ Main Execution ------

# Convert .IMG to .GIF
run_task("Converting IMG to GIF", convert_to_gif, original_gamedata, output_folder)
run_task("Splitting floors", splitfloors, output_folder)

# Export Sprites
run_task("Exporting Sprites", export_sprites,output_folder,original_gamedata)

# Parse Talking Data
run_task("Parsing Talking Data", parse_talking, original_gamedata, output_folder)

# Generate Model Dictionary
cities = ["kcity", "jcity", "pcity", "wcity", "scity", "city"]
for city in tqdm(cities, desc="Generating Full Model Dict", leave=True):
    run_task(f"Parsing {city}", parse_full_blk_dict_inner, original_gamedata, output_folder, city)

# Create Floor Images
for city in tqdm(cities, desc="Generating Doom Floors", leave=True):
    run_task(f"Creating Floor Images for {city}", create_floor_images, output_folder, city)

# Generate Model Definitions
walls = ["KWALL", "PWALL", "JWALL", "SWALL", "WWALL", "WALL"]
for wall in tqdm(walls, desc="Generating Model Definitions", leave=True):
    run_task(f"Generating ModelDef for {wall}", generate_modeldef, output_folder, wall)
run_task("Combining ModelDefs", combine_modeldefs, output_folder)

# Generate Wall Decorate
run_task("Initializing Tracking File", initialize_tracking_file, output_folder)
wall_decorate = [("kwall", 1), ("pwall", 3), ("jwall", 5), ("swall", 7), ("wwall", 9), ("wall", 11)]
for wall, num in tqdm(wall_decorate, desc="Generating Wall Decorate", leave=True):
    run_task(f"Generating Decorate for {wall}", generate_decorate, output_folder, wall, num)

# Rename Object Files
object_decorate = [("kobjects", 2, "K"), ("pobject", 4, "P"), ("jobjects", 6, "J"), 
                    ("sobjects", 8, "S"), ("wobjects", 10, "W"), ("objects", 12, "Z")]
for obj, num, prefix in tqdm(object_decorate, desc="Renaming Objects", leave=True):
    run_task(f"Renaming {obj}", rename_files, output_folder, obj, num, prefix)

# Generate UDMF Files
for city in tqdm(["jcity", "pcity", "wcity", "scity", "kcity"], desc="Generating UDMF", leave=True):
    run_task(f"Generating UDMF for {city}", make_udmf, output_folder, city)

os.mkdir(f"{output_folder}/acs")
# Generate acs Files
object_decorate = [("j","jcity"),("p","pcity"),("w","wcity"),("s","scity"),("k","kcity")]
for startletter, city in tqdm(object_decorate, desc="Generating ACS Files", leave=True):
    run_task(f"Creating acs files for {city}", make_json_output, startletter, city,output_folder)

#cities = ["kcity", "jcity", "pcity", "wcity", "scity", "city"]    
#generate acs script references
for startletter, city in tqdm(object_decorate, desc="Generating ACS Files", leave=True):
    run_task(f"Creating script launching array for {city}", create_maptiles_for_acs, startletter, city, original_gamedata,output_folder)
        
    
    
print("✅ All tasks completed successfully!")



