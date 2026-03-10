import json
import os
from tqdm import tqdm

class UDMFMap:
    def __init__(self):
        self.vertices = []
        self.linedefs = []
        self.sidedefs = []
        self.sectors = []
        self.vertex_map = {}

    def add_vertex(self, x, y):
        pos = (float(x), float(y))
        if pos not in self.vertex_map:
            index = len(self.vertices)
            self.vertices.append(pos)
            self.vertex_map[pos] = index
        return self.vertex_map[pos]

    def find_shared_edge(self, v1_pos, v2_pos):
        """Find if these vertices form a shared edge with existing sectors"""
        v1 = self.vertex_map.get((float(v1_pos[0]), float(v1_pos[1])))
        v2 = self.vertex_map.get((float(v2_pos[0]), float(v2_pos[1])))

        if v1 is None or v2 is None:
            return None

        for i, linedef in enumerate(self.linedefs):
            if (linedef['v1'], linedef['v2']) in [(v1, v2), (v2, v1)]:
                return i
        return None

    def add_sector(self, v1, v2, v3, v4, sector_id, heightfloor=0, heightceiling=512, texturefloor="black", textureceiling="F_SKY1", lightlevel=192):
        # Create sector
        sector_index = len(self.sectors)
        self.sectors.append({
            'heightfloor': heightfloor,
            'heightceiling': heightceiling,
            'texturefloor': texturefloor,
            'textureceiling': textureceiling,
            'lightlevel': lightlevel,
            'id': sector_id  # Add sector ID
        })

        # Add vertices in correct order for DOOM
        vertices = []
        for v in [v1, v2, v3, v4]:  # Correct order for DOOM
            vertices.append(self.add_vertex(*v))

        # Create edges
        edges = list(zip(vertices, vertices[1:] + [vertices[0]]))

        # Add linedefs and sidedefs for each edge
        for v1_pos, v2_pos in zip([v1, v2, v3, v4], [v2, v3, v4, v1]):
            v1_idx = self.add_vertex(*v1_pos)
            v2_idx = self.add_vertex(*v2_pos)

            # Check if the linedef already exists
            shared_edge = self.find_shared_edge(v1_pos, v2_pos)

            if shared_edge is not None:
                # This is a shared edge - make it two-sided
                sidedef = {'sector': sector_index}  # No texturemiddle for shared edges
                sidedef_idx = len(self.sidedefs)
                self.sidedefs.append(sidedef)

                # Update existing linedef to be two-sided
                self.linedefs[shared_edge]['sideback'] = sidedef_idx
                self.linedefs[shared_edge]['twosided'] = True
                if 'blocking' in self.linedefs[shared_edge]:
                    del self.linedefs[shared_edge]['blocking']

                # Remove texturemiddle from the existing sidedef (if it exists)
                front_sidedef_idx = self.linedefs[shared_edge]['sidefront']
                if 'texturemiddle' in self.sidedefs[front_sidedef_idx]:
                    del self.sidedefs[front_sidedef_idx]['texturemiddle']
            else:
                # This is an outer edge - make it one-sided with a texture
                sidedef = {
                    'sector': sector_index,
                    'texturemiddle': "black"  # Only use middle texture for outer walls
                }
                sidedef_idx = len(self.sidedefs)
                self.sidedefs.append(sidedef)

                self.linedefs.append({
                    'v1': v1_idx,
                    'v2': v2_idx,
                    'sidefront': sidedef_idx,
                    'blocking': True
                })

    def generate_udmf(self):
        udmf = 'namespace = "zdoom";\n\n'

        # Generate vertices
        for i, (x, y) in enumerate(self.vertices):
            udmf += f'vertex // {i}\n{{\nx = {x};\ny = {y};\n}}\n\n'

        # Generate linedefs
        for i, linedef in enumerate(self.linedefs):
            udmf += f'linedef // {i}\n{{\n'
            udmf += f'v1 = {linedef["v1"]};\n'
            udmf += f'v2 = {linedef["v2"]};\n'
            udmf += f'sidefront = {linedef["sidefront"]};\n'
            if 'sideback' in linedef:
                udmf += f'sideback = {linedef["sideback"]};\n'
                udmf += 'twosided = true;\n'
            if linedef.get('blocking'):
                udmf += 'blocking = true;\n'
            udmf += '}\n\n'

        # Generate sidedefs
        for i, sidedef in enumerate(self.sidedefs):
            udmf += f'sidedef // {i}\n{{\n'
            udmf += f'sector = {sidedef["sector"]};\n'
            if 'texturemiddle' in sidedef:
                udmf += f'texturemiddle = "{sidedef["texturemiddle"]}";\n'
            udmf += '}\n\n'

        # Generate sectors
        for i, sector in enumerate(self.sectors):
            udmf += f'sector // {i}\n{{\n'
            for key, value in sector.items():
                if isinstance(value, str):
                    udmf += f'{key} = "{value}";\n'
                else:
                    udmf += f'{key} = {value};\n'
            udmf += '}\n\n'

        return udmf

def create_grid(udmf_map, grid_size, tile_size):
    total_grid_size = grid_size * tile_size
    start_x = - (50 * 512)
    start_y = (50 * 512)

    for row in tqdm(range(grid_size), desc="Generating Rows"):
        for col in tqdm(range(grid_size), desc="Generating Columns", leave=False):
            sector_id = row * grid_size + col + 1
            x = start_x + col * tile_size
            y = start_y - row * tile_size
            vertices = [
                (x, y),
                (x + tile_size, y),
                (x + tile_size, y - tile_size),
                (x, y - tile_size)
            ]
            udmf_map.add_sector(
                vertices[0], vertices[1], vertices[2], vertices[3],
                sector_id=sector_id
            )

def generate_udmf_file(output_folder, grid_size=100, tile_size=512):
    os.makedirs(f"{output_folder}/doom/udmf/", exist_ok=True)

    udmf_map = UDMFMap()
    create_grid(udmf_map, grid_size, tile_size)

    # Generate UDMF content
    udmf_content = udmf_map.generate_udmf()

    # Write UDMF content to a text file
    with open(f"{output_folder}/doom/udmf/udmf_grid.txt", "w") as file:
        file.write(udmf_content)

# Example usage
output_folder = "C:/2025_projects/Quarantine_fullset/output"
generate_udmf_file(output_folder)
