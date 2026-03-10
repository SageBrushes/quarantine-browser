import bpy
import math
import os
import json
from mathutils import Vector, Quaternion, Matrix

# Clear existing objects
def clear_scene():
    """Clear all objects in the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Also clear all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Clear all textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)
        
    # Clear all images
    for image in bpy.data.images:
        bpy.data.images.remove(image)

# Create a material with texture
def create_material(name, texture_path):
    """Create a material with a texture"""
    # Check if the texture exists first
    if not os.path.exists(texture_path):
        print(f"Warning: Texture {texture_path} not found")
        # Create a placeholder colored material instead
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (0.8, 0.2, 0.8, 1.0)  # Purple as default
        return mat
    
    # Create a new material
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    
    # Get the material output and BSDF nodes
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.get('Material Output')
    bsdf = nodes.get('Principled BSDF')
    
    # Create texture image node
    tex_image = nodes.new('ShaderNodeTexImage')
    
    # Load and assign the image
    try:
        img = bpy.data.images.load(texture_path)
        tex_image.image = img
    except:
        print(f"Error: Could not load image {texture_path}")
        return mat
    
    # Connect nodes
    links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
    
    return mat

# Create a floor
def create_floor(vertices, texture_name, vertical_distance, rotation, scale, offset_x, offset_y):
    """Create a floor plane using the given vertices and texture"""
    # Create a new mesh and object
    mesh = bpy.data.meshes.new("floor_mesh")
    obj = bpy.data.objects.new("floor", mesh)
    
    # Link the object to the scene
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    
    # Create vertices
    verts = []
    for v in vertices:
        verts.append(Vector((v['x'] + offset_x, -v['y'] - offset_y, vertical_distance)))
    
    # Create faces (assuming the floor is a quad)
    faces = [(0, 1, 2, 3)]
    
    # Create the mesh from vertices and faces
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Create the material
    texture_path = os.path.join("/static/floors/", texture_name)
    mat = create_material(f"floor_material_{texture_name}", texture_path)
    
    # Assign the material to the object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    # Apply rotation
    obj.rotation_euler = (math.pi/2, 0, rotation * math.pi / 180)
    
    return obj

# Create a wall
def create_wall(start_east, start_south, end_east, end_south, 
                wall_height, wall_offset_vertical, texture_path, 
                offset_x, offset_y):
    """Create a wall between two points"""
    # Calculate wall dimensions and position
    dx = end_east - start_east
    dz = end_south - start_south
    
    length = math.sqrt(dx*dx + dz*dz)
    angle = math.atan2(dz, dx)
    
    center_x = offset_x + (start_east + end_east) / 2
    center_y = offset_y + (start_south + end_south) / 2
    center_z = wall_offset_vertical + (wall_height / 2)
    
    # Create a plane for the wall
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD')
    wall = bpy.context.active_object
    wall.name = "wall"
    
    # Set dimensions
    wall.scale.x = length
    wall.scale.y = wall_height
    
    # Position wall
    wall.location = (center_x, center_y, center_z)
    
    # Rotate wall
    wall.rotation_euler = (0, 0, angle + math.pi/2)
    
    # Rotate wall to be vertical (x-z plane)
    wall.rotation_euler.x = math.pi/2
    
    # Create the material
    mat = create_material(f"wall_material_{os.path.basename(texture_path)}", texture_path)
    
    # Assign the material to the object
    if wall.data.materials:
        wall.data.materials[0] = mat
    else:
        wall.data.materials.append(mat)
    
    return wall

# Create a sprite
def create_sprite(sprite_x, sprite_y, sprite_z, sprite_height, sprite_image, offset_x, offset_y):
    """Create a sprite at the given position"""
    # Create a plane for the sprite
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD')
    sprite = bpy.context.active_object
    sprite.name = "sprite"
    
    # Calculate position
    pos_x = offset_x + sprite_x
    pos_y = offset_y + sprite_y
    pos_z = sprite_z + (sprite_height / 2)
    
    # Set position
    sprite.location = (pos_x, pos_y, pos_z)
    
    # Scale sprite
    sprite.scale.x = sprite_height / 2
    sprite.scale.y = sprite_height
    
    # Rotate to face camera (billboard effect)
    sprite.rotation_euler = (0, 0, math.pi/2)
    
    # Create the material
    texture_path = os.path.join("/static/objects/", sprite_image)
    mat = create_material(f"sprite_material_{sprite_image}", texture_path)
    
    # Assign the material to the object
    if sprite.data.materials:
        sprite.data.materials[0] = mat
    else:
        sprite.data.materials.append(mat)
    
    return sprite

# Create direction markers
def create_direction_markers():
    """Create colored markers for North, East, South, West"""
    markers = [
        {"color": (1, 0, 0, 1), "position": (206, -50, 10), "name": "N"},   # North (Red)
        {"color": (0, 1, 0, 1), "position": (550, 206, 10), "name": "E"},   # East (Green)
        {"color": (0, 0, 1, 1), "position": (256, 550, 10), "name": "S"},   # South (Blue)
        {"color": (1, 1, 0, 1), "position": (-50, 206, 10), "name": "W"}    # West (Yellow)
    ]
    
    for marker in markers:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=5, location=marker["position"])
        sphere = bpy.context.active_object
        sphere.name = f"Marker_{marker['name']}"
        
        # Create a material for the marker
        mat = bpy.data.materials.new(f"Marker_Material_{marker['name']}")
        mat.diffuse_color = marker["color"]
        
        # Assign the material
        if sphere.data.materials:
            sphere.data.materials[0] = mat
        else:
            sphere.data.materials.append(mat)

# Generate a floor for a tile
def generate_floor(floors, loop_number, offset_x, offset_y):
    """Generate floors for a tile"""
    for floor_data in floors:
        # Extract key properties
        scale = floor_data["floor_scale"]
        vertical_distance = floor_data["real_z_offset"]
        rotation = floor_data["floor_rotation"] * 90  # Convert to degrees
        
        # Select texture based on loop number (0-indexed)
        image_name = floor_data["floor_texture_name_array"][min(loop_number, 3)]
        
        # Get vertices from wall_scale_floor_vertices (512x512 scale)
        vertices = floor_data["wall_scale_floor_vertices"]
        
        # Create the floor
        create_floor(vertices, image_name, vertical_distance, rotation, scale, offset_x, offset_y)

# Generate walls for a tile
def generate_walls(walls, loop_number, offset_x, offset_y):
    """Generate walls for a tile"""
    for wall_data in walls:
        start_east = wall_data["start_east"]
        start_south = wall_data["start_south"]
        end_east = wall_data["end_east"]
        end_south = wall_data["end_south"]
        wall_offset_vertical = wall_data["real_z_offset"]
        wall_height = wall_data["wall_height"]
        tile_count = wall_data["tile_count"]
        looping = wall_data["texture_repeat"]
        texture_files = wall_data["wall_texture_filenames"][loop_number]
        
        # Calculate the total distance and direction
        total_dx = end_east - start_east
        total_dz = end_south - start_south
        total_length = math.sqrt(total_dx * total_dx + total_dz * total_dz)
        
        # Calculate segment length and direction
        segment_length = total_length / tile_count
        direction_x = total_dx / total_length
        direction_z = total_dz / total_length
        
        # Create each wall segment
        for i in range(tile_count):
            # Calculate segment start and end points
            segment_start_x = (start_east + (direction_x * segment_length * i))
            segment_start_z = (start_south + (direction_z * segment_length * i))
            segment_end_x = (segment_start_x + (direction_x * segment_length))
            segment_end_z = (segment_start_z + (direction_z * segment_length))
            
            # Determine which texture to use
            if looping == False:
                texture_index = (tile_count - i) - 1  # Use the specific texture for this segment
            else:
                texture_index = 0  # Use the first texture for all segments
                
            current_letter = "a"  # This would need to be set based on your map name
            texture_path = f"/static/walls/{current_letter}wall/{texture_files[texture_index]}"
            
            # Create the wall
            create_wall(segment_start_x, segment_start_z, segment_end_x, segment_end_z, 
                        wall_height, wall_offset_vertical, texture_path, offset_x, offset_y)

# Generate sprites for a tile
def generate_sprites(sprites, loop_number, offset_x, offset_y):
    """Generate sprites for a tile"""
    current_letter = "a"  # This would need to be set based on your map name
    
    for sprite_data in sprites:
        sprite_x = sprite_data["sprite_x"]
        sprite_y = sprite_data["sprite_y"]
        sprite_z = sprite_data["sprite_z"]
        sprite_height = sprite_data["sprite_height"]
        sprite_image = sprite_data["sprite_image"]
        
        # Create the sprite
        create_sprite(sprite_x, sprite_y, sprite_z, sprite_height, 
                      f"{current_letter}objects/{sprite_image}", offset_x, offset_y)

# Calculate loop number based on tile index
def calculate_loop(current_tile):
    """Calculate the loop number based on the tile index"""
    # Ensure currentTile is within the range 0 to 1023
    while current_tile > 1023:
        current_tile -= 1025
    
    # Determine the value of loopnum based on the range of currentTile
    if 0 <= current_tile <= 255:
        return 0
    elif 256 <= current_tile <= 511:
        return 1
    elif 512 <= current_tile <= 767:
        return 2
    elif 768 <= current_tile <= 1023:
        return 3
    else:
        return 0

# Main function to build the map
def build_hex_map(map_data_file):
    """Build a hex map from the given map data file"""
    # Clear the scene first
    clear_scene()
    
    # Create a camera
    bpy.ops.object.camera_add(location=(43795, 31658, 25614))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(90), 0, 0)  # Point downward
    bpy.context.scene.camera = camera
    
    # Add ambient light
    bpy.ops.object.light_add(type='SUN', location=(512, 512, 1000))
    light = bpy.context.active_object
    light.data.energy = 5.0
    
    # Create direction markers
    create_direction_markers()
    
    # Load map data
    with open(map_data_file, 'r') as f:
        map_data = json.load(f)
    
    # Extract map name and set current letter
    current_map = map_data["main_settings"]["city_name"]
    current_letter = current_map.replace("city", "")
    
    # Get the map array
    map_array = map_data["map_map"][2]  # Using map level 2 as in the Three.js code
    
    # Process each tile in the map
    tile_rows = len(map_array)
    for y in range(tile_rows):
        offset_x = 0  # Reset X offset for each new row
        
        # Get the length of the current row
        tile_cols = len(map_array[y]) if isinstance(map_array[y], list) else 0
        
        for x in range(tile_cols):
            current_tile = map_array[y][x]
            
            # Calculate the loop number
            wall_loop = calculate_loop(current_tile)
            
            # Normalize the tile index
            current_tile = current_tile % 128
            current_floor_tile = current_tile
            current_wall_tile = current_tile
            
            # Skip empty tiles
            if current_tile != 0:
                # Generate floor
                try:
                    generate_floor(
                        map_data["tiles"][str(current_floor_tile)]["floors"], 
                        0,  # Using 0 for floor loop as in the Three.js code
                        offset_x, 
                        offset_y
                    )
                except Exception as e:
                    print(f"Error generating floor for tile {current_tile}: {e}")
                
                # Generate walls
                try:
                    generate_walls(
                        map_data["tiles"][str(current_wall_tile)]["walls"], 
                        wall_loop, 
                        offset_x, 
                        offset_y
                    )
                except Exception as e:
                    print(f"Error generating walls for tile {current_tile}: {e}")
                
                # Generate sprites
                #try:
                #    generate_sprites(
                #        map_data["tiles"][str(current_tile)]["sprites"], 
                #        0,  # Using 0 for sprite loop
                #        offset_x, 
                #        offset_y
                #    )
                #except Exception as e:
                #    print(f"Error generating sprites for tile {current_tile}: {e}")
            
            offset_x += 512  # Move right for the next tile in the row
        
        offset_y += 512  # Move down for the next row
    
    # Set view to camera
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
            break
    
    print("Map building complete!")

# Example usage:
# Replace with the path to your JSON map data file
# build_hex_map('/path/to/your/map_data.json')

# For testing without a file, you can create a simple function that generates mock data
def create_test_map():
    """Create a simple test map with a few tiles"""
    # Clear the scene first
    clear_scene()
    
    # Create a camera
    bpy.ops.object.camera_add(location=(1000, 1000, 1000))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(45), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Add ambient light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 1000))
    light = bpy.context.active_object
    light.data.energy = 2.0
    
    # Create a simple ground plane
    bpy.ops.mesh.primitive_plane_add(size=5000, location=(2500, 2500, -1))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    # Create a grid of simple floors (colored planes) to represent tiles
    for y in range(5):
        for x in range(5):
            offset_x = x * 512
            offset_y = y * 512
            
            # Create a simple floor
            bpy.ops.mesh.primitive_plane_add(size=500, location=(offset_x + 256, offset_y + 256, 0))
            floor = bpy.context.active_object
            floor.name = f"Floor_{x}_{y}"
            
            # Create a material with a random color
            mat = bpy.data.materials.new(f"Floor_Material_{x}_{y}")
            mat.diffuse_color = (x/5, y/5, (x+y)/10, 1)
            
            # Assign the material
            if floor.data.materials:
                floor.data.materials[0] = mat
            else:
                floor.data.materials.append(mat)
            
            # Create simple walls around the perimeter of each tile
            wall_height = 100
            wall_positions = [
                # North wall
                (offset_x + 256, offset_y, wall_height/2, 500, wall_height, 0),
                # East wall
                (offset_x + 500, offset_y + 256, wall_height/2, 500, wall_height, math.pi/2),
                # South wall
                (offset_x + 256, offset_y + 500, wall_height/2, 500, wall_height, 0),
                # West wall
                (offset_x, offset_y + 256, wall_height/2, 500, wall_height, math.pi/2)
            ]
            
            for i, (wx, wy, wz, width, height, rotation) in enumerate(wall_positions):
                bpy.ops.mesh.primitive_plane_add(size=1, location=(wx, wy, wz))
                wall = bpy.context.active_object
                wall.name = f"Wall_{x}_{y}_{i}"
                wall.scale.x = width
                wall.scale.y = height
                wall.rotation_euler.z = rotation
                wall.rotation_euler.x = math.pi/2
                
                # Create a material with a color
                mat = bpy.data.materials.new(f"Wall_Material_{x}_{y}_{i}")
                mat.diffuse_color = (0.8, 0.8, 0.8, 1)
                
                # Assign the material
                if wall.data.materials:
                    wall.data.materials[0] = mat
                else:
                    wall.data.materials.append(mat)
    
    print("Test map created!")

# Uncomment one of these to run the script
# build_hex_map('/path/to/your/map_data.json')  # Use this with your real data
create_test_map()  # Use this for testing without data