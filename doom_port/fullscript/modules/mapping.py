import os
import shutil


def create_folders(output_folder):
    print(" - Creating 3js map structure...") 
    map_folder = os.path.join(output_folder, "map")
    os.makedirs(map_folder, exist_ok=True)  # Creates the main map folder if it doesn't exist
    
    # Define subfolders
    subfolders = ["static", "templates", "data", "modules"]
    
    for folder in subfolders:
        folder_path = os.path.join(map_folder, folder)
        os.makedirs(folder_path, exist_ok=True)  # Creates each subfolder if it doesn't exist
        print(f"   Folder created at: {folder_path}")    

    folder_path = os.path.join(map_folder, "data","modeldefs")
    os.makedirs(folder_path, exist_ok=True)


def copy_floors(output_folder):
    print(" - Moving floor tiles...") 
    copy_folder("{}/textures/game/floors".format(output_folder), "{}/map/static/floors".format(output_folder))
    copy_folder("{}/sprites/walls".format(output_folder), "{}/map/static/walls".format(output_folder))
    copy_folder("{}/sprites/objects".format(output_folder), "{}/map/static/objects".format(output_folder))
    
    
    
def move_modeldef_files(output_folder):
    print(" - Moving modeldef files...") 
    copy_file("{}/modeldef/tile_config_city.json".format(output_folder), "{}/map/data/modeldefs/tile_config_city.json".format(output_folder))
    copy_file("{}/modeldef/tile_config_jcity.json".format(output_folder), "{}/map/data/modeldefs/tile_config_jcity.json".format(output_folder))
    copy_file("{}/modeldef/tile_config_kcity.json".format(output_folder), "{}/map/data/modeldefs/tile_config_kcity.json".format(output_folder))
    copy_file("{}/modeldef/tile_config_wcity.json".format(output_folder), "{}/map/data/modeldefs/tile_config_wcity.json".format(output_folder))
    copy_file("{}/modeldef/tile_config_scity.json".format(output_folder), "{}/map/data/modeldefs/tile_config_scity.json".format(output_folder))
    copy_file("{}/modeldef/tile_config_pcity.json".format(output_folder), "{}/map/data/modeldefs/tile_config_pcity.json".format(output_folder))

def copy_file(src, dest):
    shutil.copy2(src, dest)  # Copy the file with metadata
    print(f" - Copied {src} to {dest}")

def copy_folder(src_folder, dest_folder):
    shutil.copytree(src_folder, dest_folder, dirs_exist_ok=True)  # Copy everything, allowing existing folders
    print(f"Copied folder {src_folder} to {dest_folder}")
    
def write_text_file(folder, filename, content):
    os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
    file_path = os.path.join(folder, filename)  # Full path for the file
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f" - File written at: {file_path}")    
    
def write_requirements(output_folder):
    write_text_file("{}/map".format(output_folder), "requirements.txt", ''' 
    fastapi;
    tdqm;
    jinja2;
    ''')
    
def write_install_batch(output_folder):
    print(" - creating installer...")     
    write_text_file("{}/map".format(output_folder), "install.bat", ''' 
	call deactivate
    python -m venv venv
    call venv\\Scripts\\activate
    pip install -r requirements.txt
    run
    ''')    

def write_run_batch(output_folder):
    print(" - creating runner...")     
    write_text_file("{}/map".format(output_folder), "run.bat", ''' 
	call deactivate
    call venv\\Scripts\\activate
    start http://localhost:5555/threetile/kcity/1
    python FAST_readmodels2_k_b.py
    
    ''')    

def create_3js_map(output_folder):
    print("\n ------Starting building map-------\n")
    print("> Creating 3js map structure...") 
    create_folders(output_folder)
    move_modeldef_files(output_folder)
    os.rename("{}/map/static/objects/pobject".format(output_folder), "{}/map/static/objects/pobjects".format(output_folder))
    copy_floors(output_folder)
    
    write_requirements(output_folder)
    write_install_batch(output_folder)
    write_run_batch(output_folder)
    
    
    #Maybe needs something that extracts a zip with the threejs stuff.
    
    print("\n -------------DONE--------------\n")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    