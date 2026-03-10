from flask import Flask, render_template, request, jsonify
import pandas as pd
import subprocess
import os
import csv
import struct

app = Flask(__name__)

# Ensure the CSV directory exists within the map_editor folder
def ensure_csv_dir():
    # Get the current script directory (map_editor)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create csvs directory in the map_editor folder if it doesn't exist
    csv_dir = os.path.join(current_dir, 'csvs')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    return csv_dir

# Get path to Original_Game directory
def get_original_game_dir():
    # Get the current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the project root (two levels up from map_editor)
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    
    # Path to Original_Game directory
    original_game_dir = os.path.join(project_root, 'Original_Game')
    return original_game_dir

# Function to import the tile data from a MAP file to CSV
def export_map_to_csv(map_file, csv_file):
    with open(map_file, 'rb') as f:
        # Read width and height (2 bytes each, little-endian)
        width_bytes = f.read(2)
        height_bytes = f.read(2)
        
        width = struct.unpack('<H', width_bytes)[0]
        height = struct.unpack('<H', height_bytes)[0]
        
        # Read tile data
        tiles = []
        for _ in range(height):
            row = []
            for _ in range(width):
                tile_bytes = f.read(2)
                tile = struct.unpack('<H', tile_bytes)[0]
                row.append(tile)
            tiles.append(row)
    
    # Write to CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in tiles:
            writer.writerow(row)
    
    print(f"Map data exported to {csv_file}")
    return width, height, tiles

# Function to import the tile data from a CSV file
def import_tiles_from_csv(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        tiles_2d = [list(map(int, row)) for row in reader]  # Convert each row to integers
        height = len(tiles_2d)
        width = len(tiles_2d[0]) if height > 0 else 0
        return width, height, tiles_2d

# Function to compile the map data into a .MAP file
def compile_map_file(file_path, width, height, tiles):
    with open(file_path, 'wb') as f:
        # Write width and height as UINT16LE (2-byte little-endian format)
        f.write(struct.pack('<H', width))
        f.write(struct.pack('<H', height))
        
        # Write the tile data as UINT16LE for each tile
        for row in tiles:
            for tile in row:
                f.write(struct.pack('<H', tile))
    
    print(f"Map data saved to {file_path}")

@app.route('/mapedit_frommap/<mapname>')
def mapedit_frommap(mapname):
    # Define directories
    csv_dir = ensure_csv_dir()
    original_game_dir = get_original_game_dir()
    
    # CSV file path in the csvs directory
    csv_path = os.path.join(csv_dir, f'{mapname.upper()}.csv')
    
    # MAP file path in the Original_Game directory
    map_path = os.path.join(original_game_dir, f'{mapname.upper()}.MAP')
    
    # If the CSV doesn't exist, create it from the MAP file
    if not os.path.exists(csv_path) and os.path.exists(map_path):
        export_map_to_csv(map_path, csv_path)
    
    try:
        df = pd.read_csv(csv_path, header=None)
        grid_data = df.values.tolist()
        rows = len(grid_data)
        cols = len(grid_data[0]) if rows > 0 else 0
        return render_template('index_v4_fromcity.html', grid_data=grid_data, rows=rows, cols=cols, mapname=mapname)
    except Exception as e:
        return f"Error loading CSV: {str(e)}", 500    
        
        
@app.route('/', methods=['GET'])
def root_address():     
     return render_template('index.html')        
            
        
@app.route('/update_chosenmap', methods=['POST'])
def update_chosenmap():
    print("Trying to update chosen map...")
    try:
        # Retrieve the data sent in the request
        data = request.json
        
        # Validate input data
        if not data or 'gridData' not in data or 'mapname' not in data:
            return jsonify({"status": "error", "message": "Missing required data"}), 400
        
        grid_data = data['gridData']
        mapname = data['mapname'].lower()
        
        # Define directories
        csv_dir = ensure_csv_dir()
        original_game_dir = get_original_game_dir()
        
        # Define the list of valid map names
        valid_maps = ["city", "jcity", "kcity", "pcity", "scity", "wcity"]
        
        # Validate mapname
        if mapname not in valid_maps:
            return jsonify({"status": "error", "message": f"Invalid map name: {mapname}"}), 400
        
        # Full paths for CSV and MAP files
        csv_path = os.path.join(csv_dir, f'{mapname.upper()}.csv')
        map_path = os.path.join(original_game_dir, f'{mapname.upper()}.MAP')
        
        # Write grid data to CSV
        df = pd.DataFrame(grid_data)
        df.to_csv(csv_path, header=False, index=False)
        print(f"CSV file updated: {csv_path}")
        
        # Import tile data from CSV and compile the MAP file
        imported_width, imported_height, imported_tiles = import_tiles_from_csv(csv_path)
        compile_map_file(map_path, imported_width, imported_height, imported_tiles)
        
        return jsonify({
            "status": "success", 
            "message": f"Successfully updated map: {mapname}", 
            "width": imported_width, 
            "height": imported_height
        })
    
    except Exception as e:
        print(f"Failure: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500     

# Utility function to export all maps to CSV
@app.route('/export_all_maps')
def export_all_maps():
    try:
        original_game_dir = get_original_game_dir()
        csv_dir = ensure_csv_dir()
        
        map_files = ["CITY.MAP", "JCITY.MAP", "KCITY.MAP", "PCITY.MAP", "SCITY.MAP", "WCITY.MAP"]
        results = []
        
        for map_file in map_files:
            map_path = os.path.join(original_game_dir, map_file)
            csv_path = os.path.join(csv_dir, f"{map_file.replace('.MAP', '.csv')}")
            
            if os.path.exists(map_path):
                width, height, _ = export_map_to_csv(map_path, csv_path)
                results.append({
                    "map": map_file,
                    "csv": os.path.basename(csv_path),
                    "width": width,
                    "height": height,
                    "status": "success"
                })
            else:
                results.append({
                    "map": map_file,
                    "status": "error",
                    "message": "Map file not found"
                })
        
        return jsonify({"status": "success", "results": results})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Ensure CSV directory exists on startup
    csv_dir = ensure_csv_dir()
    
    # Get Original_Game directory
    original_game_dir = get_original_game_dir()
    
    print(f"Original Game Directory: {original_game_dir}")
    print(f"CSV Directory: {csv_dir}")
    
    map_files = ["CITY.MAP", "JCITY.MAP", "KCITY.MAP", "PCITY.MAP", "SCITY.MAP", "WCITY.MAP"]
    for map_file in map_files:
        map_path = os.path.join(original_game_dir, map_file)
        csv_path = os.path.join(csv_dir, f"{map_file.replace('.MAP', '.csv')}")
        
        if os.path.exists(map_path) and not os.path.exists(csv_path):
            try:
                export_map_to_csv(map_path, csv_path)
                print(f"Exported {map_file} to {os.path.basename(csv_path)}")
            except Exception as e:
                print(f"Error exporting {map_file}: {str(e)}")
    
    app.run(debug=True)