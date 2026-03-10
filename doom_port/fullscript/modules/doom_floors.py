import json
import os 
from PIL import Image, ImageDraw
from io import BytesIO
import base64  # Add this



def create_floor_images(output_folder,map):
    
    map_letter=""
    
    if map== "kcity":
        #dict_file='C:/2025_projects/Quarantine_fullset/output/modeldef/tile_config_kcity.json'
        dict_file=f'{output_folder}/modeldef/tile_config_kcity.json'
        map_letter="k"
    elif map== "city":
        #dict_file='C:/2025_projects/Quarantine_fullset/output/modeldef/tile_config_city.json'
        dict_file=f'{output_folder}/modeldef/tile_config_city.json'
        map_letter="z"
    elif map== "jcity":
        #dict_file='C:/2025_projects/Quarantine_fullset/output/modeldef/tile_config_jcity.json'
        dict_file=f'{output_folder}/modeldef/tile_config_jcity.json'
        map_letter="j"
    elif map== "pcity":
        #dict_file='C:/2025_projects/Quarantine_fullset/output/modeldef/tile_config_pcity.json'
        dict_file=f'{output_folder}/modeldef/tile_config_pcity.json'
        map_letter="p"
    elif map== "scity":
        #dict_file='C:/2025_projects/Quarantine_fullset/output/modeldef/tile_config_scity.json'
        dict_file=f'{output_folder}/modeldef/tile_config_scity.json'
        map_letter="s"
    elif map== "wcity":
        #dict_file='C:/2025_projects/Quarantine_fullset/output/modeldef/tile_config_wcity.json'     
        dict_file=f'{output_folder}/modeldef/tile_config_wcity.json'     
        map_letter="w"

    
    def load_definition_data(dict_file):
        with open(dict_file, 'r') as file:
            definition_data = json.load(file)
        return definition_data["tiles"]

    map_definitions = load_definition_data(dict_file)
    output_dir = f'{output_folder}/floors/{map}'
    os.makedirs(output_dir, exist_ok=True)

    floor_textures_dir = f'{output_folder}/textures/game/floors'
    floor_textures = {filename.lower(): Image.open(os.path.join(floor_textures_dir, filename)).convert("RGB") for filename in os.listdir(floor_textures_dir) if filename.endswith(".gif")}

    print("Loaded floor textures:", floor_textures.keys())

    images = []

    for tile_index, tile_data in map_definitions.items():
        image = Image.new("RGB", (512, 512), "black")
        draw = ImageDraw.Draw(image)

        floordef = tile_data["floors"]

        for floor in floordef:
            texturefloor = floor["floor_texture_name_array"][0].lower()
            print(f"Processing tile {tile_index}, texture: {texturefloor}")

            if texturefloor in floor_textures:
                floor_texture = floor_textures[texturefloor]
                vertices = [
                    (floor["wall_scale_floor_vertices"][0]["x"],  floor["wall_scale_floor_vertices"][0]["y"]),
                    (floor["wall_scale_floor_vertices"][1]["x"],  floor["wall_scale_floor_vertices"][1]["y"]),
                    (floor["wall_scale_floor_vertices"][2]["x"],  floor["wall_scale_floor_vertices"][2]["y"]),
                    (floor["wall_scale_floor_vertices"][3]["x"],  floor["wall_scale_floor_vertices"][3]["y"])
                ]

                draw.polygon(vertices, outline="green")

                mask = Image.new("L", (512, 512), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.polygon(vertices, outline=255, fill=255)

                rotation = -(floor["floor_rotation"] * 90)
                rotated_texture = floor_texture.rotate(rotation, expand=True)


                if floor["floor_scale"]==0:
                    size = 64
                elif floor["floor_scale"]==1:
                    size= 123
                elif floor["floor_scale"]==2:
                    size= 256
                elif floor["floor_scale"]==3:
                    size= 512                    
                
                scaled_width = size
                scaled_height = size

                sector_image = Image.new("RGB", (512, 512), "black")
                for x in range(0, 512, scaled_width):
                    for y in range(0, 512, scaled_height):
                        sector_image.paste(rotated_texture.resize((scaled_width, scaled_height)), (x, y))

                sector_image.putalpha(mask)
                image.paste(sector_image, (0, 0), sector_image)
            else:
                print(f"Texture {texturefloor} not found in floor_textures")

            # Save the generated image to disk
            #output_path = os.path.join(output_dir, f"tile_{tile_index}.png")
            output_path = os.path.join(output_dir, f"{map_letter}_f_{tile_index}.png")
            image.save(output_path, format="PNG")
            print(f"Saved tile image: {output_path}")

            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            images.append(f"data:image/png;base64,{img_str}")
            print(f"Generated image for tile {tile_index}")

    # Return the generated images as a JSON response
    return "images created in folder : {}".format(output_dir)