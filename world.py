"""
World class for tilemap, collision detection, and decorative elements.
"""
import os
import pygame as pg
try:
    import pytmx
    PYTMX_AVAILABLE = True
except ImportError:
    PYTMX_AVAILABLE = False
    print("pytmx not available - Tiled map loading disabled")
from assets import AssetManager
from config import TILESET_IMAGE, CASINO_TILESET_DIR, MUSIC_FILE, MUSIC_ENABLED, USE_TILED_MAP, TILED_MAP_FILE, ASSET_DIR


class World:
    """Game world with tilemap, collision detection, and decorative elements."""
    
    def __init__(self, tilesize: int = 32, tiled_map_path: str = None):
        self.tilesize = tilesize
        self.tiles = {}
        self.tilemap = []
        self.collision_map = []
        # self.asset_manager = AssetManager()  # DISABLED - no extra props
        self.decorative_objects = []  # List of decorative elements
        self.ambient_effects = []     # List of ambient effects
        self.show_collision_debug = False
        self.tmx_data = None         # Store Tiled map data
        self.tmx_surface = None      # Pre-rendered TMX surface
        self.npc_objects = []        # NPCs from Tiled object layer
        self.load_tiles()
        
        # Load ONLY your TMX map - no procedural generation
        tmx_path = os.path.join(ASSET_DIR, TILED_MAP_FILE)
        print(f"Loading TMX map only: {tmx_path}")
        self.load_tmx_only(tmx_path)
        
        # NO decorative elements setup
        self.music_loaded = False
        if MUSIC_ENABLED:
            try:
                pg.mixer.music.load(MUSIC_FILE)
                pg.mixer.music.set_volume(0.5)
                self.music_loaded = True
                pg.mixer.music.play(-1)
            except Exception:
                self.music_loaded = False
    
    def load_tiles(self):
        """Load tile images from tileset."""
        # Load the tileset image
        try:
            print(f"Attempting to load tileset: {TILESET_IMAGE}")
            tileset = pg.image.load(TILESET_IMAGE)
            if tileset:
                tileset = tileset.convert_alpha()
                print("Successfully loaded tileset")
                print(f"Tileset size: {tileset.get_width()}x{tileset.get_height()}")
            else:
                raise Exception("Failed to load tileset")
        except Exception as e:
            print(f'Error loading casino tileset: {e}')
            # Create fallback tiles
            self.create_fallback_tiles()
            return

        # Define tile regions in the tileset (x, y, width, height, is_solid)
        # NOTE: Extracting 32x32 from tileset but scaling down to 16x16 for display
        tile_definitions = {
            'floor': (32, 32, 32, 32, False),        # Regular casino floor (patterned red)
            # Map fancy floor to same red patterned tile (remove previous purple variant)
            'floor_fancy': (32, 32, 32, 32, False),  # Fancy now uses base red pattern
            'floor_dark': (32, 32, 32, 32, False),   # Dark casino floor
            'wall': (180, 425, 32, 32, True),         # Wall
            'wall_top': (128, 0, 32, 32, True),      # Wall top
            # Make decorative / gameplay objects non-solid; interaction will be handled separately
            'table': (289, 270, 32, 32, False),        # Table (walkable)
            'blackjack_table': (225, 405, 95, 50, False),  # Special blackjack table (walkable)
            'slot_machine': (595, 367, 32, 32, False), # Slot machine (walkable)
            'plant': (414, 255, 32, 32, False),        # Decorative plant (walkable)
            'decoration': (414, 255, 32, 32, False),   # General decoration (use plant tile)
            'empty': (32, 32, 32, 32, False)         # Empty space
        }

        # Extract tiles from tileset
        for tile_name, (x, y, w, h, solid) in tile_definitions.items():
            tile_surface = pg.Surface((w, h), pg.SRCALPHA)
            tile_surface.blit(tileset, (0, 0), (x, y, w, h))

            # No manual recolor: fancy floor now directly reuses the base red tile
            
            # Create special colored blackjack table
            #if tile_name == 'blackjack_table':
                # Create a green table with gold trim
                #blackjack_surface = pg.Surface((w, h), pg.SRCALPHA)
                #blackjack_surface.fill((0, 100, 0))  # Dark green
                #pg.draw.rect(blackjack_surface, (255, 215, 0), (0, 0, w, h), 3)  # Gold border
                #pg.draw.rect(blackjack_surface, (0, 150, 0), (4, 4, w-8, h-8))  # Lighter green center

                # font = pg.font.SysFont('Arial', 16, bold=True)
                # text = font.render('BJ', True, (255, 215, 0))
                # text_rect = text.get_rect(center=(w//2, h//2))
                # blackjack_surface.blit(text, text_rect)
                # tile_surface = blackjack_surface
            
            self.tiles[tile_name] = {
                'image': pg.transform.scale(tile_surface, (self.tilesize, self.tilesize)),
                'solid': solid
            }
    
    def create_demo_map(self):
        """Create the beautiful detailed casino tilemap layout."""
        # Use the detailed procedural casino map with all the beautiful elements
        print("Creating detailed procedural casino map with rich casino elements...")
        base_map = self.create_detailed_casino_map()
        self.tilemap = base_map
        
        # Create collision map based on tile properties
        self.collision_map = [
            [self.tiles[tile]['solid'] if tile in self.tiles else True
             for tile in row]
            for row in self.tilemap
        ]
    
    def create_detailed_casino_map(self):
        """Create a detailed 32x24 casino map for 16x16 tiles (zoomed in view)."""
        # Keep the same map dimensions as before but with more detail
        map_width, map_height = 32, 24
        casino_map = []
        
        for y in range(map_height):
            row = []
            for x in range(map_width):
                # Border walls
                if x == 0 or x == map_width-1 or y == 0 or y == map_height-1:
                    row.append('wall')
                # Interior areas with more detailed placement
                else:
                    # Main gaming area (center-left)
                    if 6 <= y <= 12 and 8 <= x <= 18:
                        if (x - 8) % 4 == 0 and (y - 6) % 3 == 1:
                            row.append('table')
                        elif x == 12 and y == 9:  # Main blackjack table
                            row.append('blackjack_table')
                        elif x == 16 and y == 9:  # Second blackjack table
                            row.append('blackjack_table')
                        else:
                            row.append('floor_fancy')
                    
                    # Slot machine areas (sides)
                    elif 3 <= y <= 20 and (x == 3 or x == 28) and y % 3 == 0:
                        row.append('slot_machine')
                    
                    # VIP area (top-right)
                    elif 3 <= y <= 8 and 20 <= x <= 28:
                        if x % 3 == 0 and y % 2 == 0:
                            row.append('table')
                        else:
                            row.append('floor_fancy')
                    
                    # Bottom gaming area
                    elif 15 <= y <= 20 and 8 <= x <= 24:
                        if x % 5 == 0 and y == 17:
                            row.append('slot_machine')
                        elif x % 4 == 2 and y == 18:
                            row.append('table')
                        else:
                            row.append('floor')
                    
                    # Decorative plants (corners and strategic spots)
                    elif (x == 2 and y == 2) or (x == 29 and y == 2) or \
                         (x == 2 and y == 21) or (x == 29 and y == 21) or \
                         (x == 15 and y == 2) or (x == 6 and y == 15):
                        row.append('plant')
                    
                    # Regular floor everywhere else
                    else:
                        row.append('floor')
            
            casino_map.append(row)
        
        return casino_map
    
    def load_tmx_only(self, map_path):
        """Load your TMX file and render it directly with proper collision detection."""
        if not PYTMX_AVAILABLE:
            print("ERROR: pytmx not available - cannot load TMX file!")
            return
            
        if not os.path.exists(map_path):
            print(f"ERROR: TMX file not found: {map_path}")
            return
            
        try:
            # Load your TMX map
            self.tmx_data = pytmx.load_pygame(map_path)
            print(f"Successfully loaded TMX: {map_path}")
            print(f"Map size: {self.tmx_data.width}x{self.tmx_data.height}")
            print(f"Tile size: {self.tmx_data.tilewidth}x{self.tmx_data.tileheight}")
            
            # Get all tile layers
            tile_layers = []
            for layer in self.tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    tile_layers.append(layer)
                    print(f"Found layer: {layer.name}")
            
            if not tile_layers:
                print("ERROR: No tile layers found in TMX file!")
                return
            
            # Create a surface to render the map onto
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.tmx_surface = pg.Surface((map_width, map_height))
            
            # Render all layers to the surface
            for layer in tile_layers:
                for x, y, gid in layer:
                    if gid:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            # Scale tile if needed
                            if tile.get_width() != self.tilesize or tile.get_height() != self.tilesize:
                                tile = pg.transform.scale(tile, (self.tilesize, self.tilesize))
                            self.tmx_surface.blit(tile, (x * self.tilesize, y * self.tilesize))
            
            # Create intelligent collision map using object layers
            self.collision_map = []
            self.collision_objects = []  # Store collision polygons for precise collision
            self.npc_objects = []  # Store NPC positions from object layer
            
            # Check for collision and NPC object layers
            collision_layer = None
            npc_layer = None
            
            for layer in self.tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledObjectGroup):
                    if layer.name.lower() in ['collisions', 'collision']:
                        collision_layer = layer
                        print(f"Found collision layer: {layer.name} with {len(layer)} objects")
                    elif layer.name.lower() in ['npcs', 'npc']:
                        npc_layer = layer
                        print(f"Found NPC layer: {layer.name} with {len(layer)} objects")
            
            # Load NPCs from object layer
            if npc_layer:
                for obj in npc_layer:
                    npc_data = {
                        'x': obj.x,
                        'y': obj.y,
                        'width': getattr(obj, 'width', 20),
                        'height': getattr(obj, 'height', 32),
                        'gid': getattr(obj, 'gid', None),
                        'properties': {}
                    }
                    
                    # Get custom properties
                    if hasattr(obj, 'properties'):
                        npc_data['properties'] = dict(obj.properties)
                    
                    # Get the tile image for this NPC
                    if npc_data['gid']:
                        npc_image = self.tmx_data.get_tile_image_by_gid(npc_data['gid'])
                        if npc_image:
                            npc_data['image'] = npc_image
                    
                    self.npc_objects.append(npc_data)
                    print(f"Loaded NPC at ({obj.x}, {obj.y}) with GID {npc_data['gid']}")
            
            # If we have a collision layer, use it
            if collision_layer:
                # Store collision objects for precise collision detection
                for obj in collision_layer:
                    if hasattr(obj, 'points'):  # Polygon collision
                        self.collision_objects.append({
                            'type': 'polygon',
                            'x': obj.x,
                            'y': obj.y,
                            'points': obj.points
                        })
                    else:  # Rectangle or point collision
                        # If width/height are 0 or not set, treat as a tile-sized collision area
                        width = getattr(obj, 'width', 0)
                        height = getattr(obj, 'height', 0)
                        
                        # Point objects with no size become tile-sized (16x16)
                        if width == 0:
                            width = self.tilesize
                        if height == 0:
                            height = self.tilesize
                        
                        self.collision_objects.append({
                            'type': 'rect',
                            'x': obj.x,
                            'y': obj.y,
                            'width': width,
                            'height': height
                        })
                
                # Create tile-based collision map from objects
                for y in range(self.tmx_data.height):
                    collision_row = []
                    for x in range(self.tmx_data.width):
                        # Check if tile center is inside any collision object
                        tile_center_x = (x + 0.5) * self.tilesize
                        tile_center_y = (y + 0.5) * self.tilesize
                        is_solid = self.point_in_collision_objects(tile_center_x, tile_center_y)
                        collision_row.append(is_solid)
                    self.collision_map.append(collision_row)
                
                print(f"Using collision objects for precise collision detection")
            else:
                # Fallback: Use GID-based collision detection
                print("No collision layer found, using GID-based collision")
                
                # Define collision GIDs based on your map
                wall_gids = {1478, 1542, 1479, 1477, 1414}  # Border walls
                table_gids = {1306, 1307, 1370, 1371, 1434, 1435, 1498, 1499}  # Tables (solid)
                slot_gids = {1531, 1532, 1533, 1534, 1535, 1536, 1595, 1596, 1597, 1598, 1599, 1600,
                            1659, 1660, 1661, 1662, 1663, 1664, 1723, 1724, 1725, 1726, 1727, 1728}  # Slot machines
                counter_gids = {439, 441, 442, 443, 503, 504, 505, 506, 507}  # Counters/bars
                
                for y in range(self.tmx_data.height):
                    collision_row = []
                    for x in range(self.tmx_data.width):
                        is_solid = False
                        
                        # Check all layers for collision tiles
                        for layer in tile_layers:
                            gid = layer.data[y][x]
                            
                            if gid in wall_gids or gid in table_gids or gid in slot_gids or gid in counter_gids:
                                is_solid = True
                                break
                            
                            # Check if tile has custom collision property
                            elif gid > 0:
                                tile_props = self.tmx_data.get_tile_properties_by_gid(gid)
                                if tile_props and tile_props.get('collision', False):
                                    is_solid = True
                                    break
                        
                        collision_row.append(is_solid)
                    self.collision_map.append(collision_row)
            
            print(f"TMX map rendered: {map_width}x{map_height} pixels")
            print(f"Collision map created: {len(self.collision_map)} rows x {len(self.collision_map[0])} columns")
            
            # Count solid tiles for debug
            solid_count = sum(sum(row) for row in self.collision_map)
            print(f"Total solid tiles: {solid_count}")
            
            # Print first few solid tile positions for debugging
            if solid_count > 0:
                print("Sample solid tiles:")
                count = 0
                for y, row in enumerate(self.collision_map):
                    for x, is_solid in enumerate(row):
                        if is_solid:
                            print(f"  Tile ({x}, {y}) = SOLID")
                            count += 1
                            if count >= 10:  # Show first 10
                                break
                    if count >= 10:
                        break
            
        except Exception as e:
            print(f"ERROR loading TMX: {e}")
            import traceback
            traceback.print_exc()
    
    def point_in_collision_objects(self, x, y):
        """Check if a point is inside any collision object."""
        for obj in self.collision_objects:
            if obj['type'] == 'rect':
                # Rectangle collision
                if (obj['x'] <= x <= obj['x'] + obj['width'] and
                    obj['y'] <= y <= obj['y'] + obj['height']):
                    return True
            elif obj['type'] == 'polygon':
                # Polygon collision using ray casting algorithm
                if self.point_in_polygon(x, y, obj['x'], obj['y'], obj['points']):
                    return True
        return False
    
    def point_in_polygon(self, x, y, poly_x, poly_y, points):
        """Check if point is inside polygon using ray casting algorithm.
        NOTE: pytmx returns Point objects with x,y attributes, and they're already in absolute coordinates!"""
        inside = False
        n = len(points)
        
        for i in range(n):
            # Get current point and next point (wrapping around)
            p1 = points[i]
            p2 = points[(i + 1) % n]
            
            # Points are already in absolute coordinates from pytmx
            x1 = p1.x if hasattr(p1, 'x') else p1[0]
            y1 = p1.y if hasattr(p1, 'y') else p1[1]
            x2 = p2.x if hasattr(p2, 'x') else p2[0]
            y2 = p2.y if hasattr(p2, 'y') else p2[1]
            
            # Ray casting algorithm
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        
        return inside
    
    def get_tile_from_gid(self, gid):
        """GID to tile mapping for your map1.tmx."""
        # Based on the actual GIDs in your map1.tmx:
        
        # Wall tiles (borders)
        if gid in [1478, 1542, 1479, 1477, 1414]:
            return 'wall'
        
        # Floor tiles
        elif gid in [259, 836, 1606, 1670, 579, 580, 581]:
            return 'floor'
        
        # Special tiles
        elif gid == 68:
            return 'decoration'
        elif gid in [323, 324]:
            return 'decoration'
            
        # Furniture layer items
        elif gid in [1062, 379, 439, 441, 442, 443, 125, 505, 506, 507, 503, 504, 120, 189, 184, 253, 248]:
            return 'decoration'
        elif gid in [1306, 1307, 1370, 1371, 1434, 1435, 1498, 1499]:
            return 'table'
        elif gid in [1549, 1550, 1613, 1614, 1677, 1678, 1741, 1742, 1547, 1548, 1611, 1612, 1675, 1676, 1739, 1740]:
            return 'decoration'
        elif gid in [1659, 1723, 1724, 1725, 1726, 1727, 1728, 1383, 1384, 1385, 1447, 1448, 1449]:
            return 'slot_machine'
            
        # Default to floor for any other tiles
        else:
            return 'floor'
    
    def is_solid_tile(self, gid, tile_name):
        """Collision detection for map1.tmx."""
        # Walls are solid
        if tile_name == 'wall' or gid in [1478, 1542, 1479, 1477, 1414]:
            return True
        # Tables are solid (can't walk through)
        elif tile_name == 'table':
            return True
        # Everything else is walkable
        else:
            return False

    def create_demo_map(self):
        """Create a simple fallback map if TMX fails."""
        self.tilemap = []
        self.collision_map = []
        
        # Simple 20x15 map
        for y in range(15):
            tile_row = []
            collision_row = []
            for x in range(20):
                if x == 0 or x == 19 or y == 0 or y == 14:
                    tile_row.append('wall')
                    collision_row.append(True)
                else:
                    tile_row.append('floor')
                    collision_row.append(False)
            self.tilemap.append(tile_row)
            self.collision_map.append(collision_row)

    def get_tile_name_from_gid(self, gid):
        """Map Tiled GID to our tile names based on map1.tmx casino tileset."""
        # Based on your map1.tmx with multiple layers, extensive GID mapping:
        
        # Wall/border tiles (from "Map" layer)
        if gid in [1478, 1542, 1479, 1477, 1414]:
            return 'wall'
        
        # Floor tiles (from "Map" layer)
        elif gid in [1606, 1670, 259, 68]:
            return 'floor'
        
        # Special gaming/table tiles (from "Map" layer)
        elif gid in [836, 579, 580, 581, 323, 324]:
            if gid == 836:
                return 'table'
            elif gid in [579, 580, 581]:
                return 'blackjack_table'
            elif gid in [323, 324]:
                return 'slot_machine'
            else:
                return 'floor_fancy'
        
        # Furniture layer items (make them solid obstacles)
        elif gid in [1062, 379, 125, 189, 253, 120, 184, 248, 1306, 1307, 1370, 1371, 
                     1434, 1435, 1498, 1499, 1549, 1550, 1613, 1614, 1677, 1678, 1741, 1742,
                     1547, 1548, 1611, 1612, 1675, 1676, 1739, 1740, 1659, 1723, 1724, 1725,
                     1726, 1727, 1728, 1383, 1384, 1385, 1447, 1448, 1449, 1511, 1512, 1513,
                     1575, 1576, 1577, 1601, 1602, 1603, 1665, 1666, 1667, 1729, 1730, 1731,
                     1484, 439, 441, 442, 443, 505, 506, 507, 503, 504]:
            return 'furniture'
        
        # Games layer items (slot machines, etc.)
        elif gid in [50, 51, 114, 116, 117, 178, 180, 181, 242, 244, 245, 1531, 1532, 1533,
                     1534, 1535, 1536, 1595, 1596, 1597, 1598, 1599, 1600, 1659, 1660, 1661,
                     1662, 1663, 1664, 448]:
            if gid in [1531, 1532, 1533, 1534, 1535, 1536, 1595, 1596, 1597, 1598, 1599, 1600,
                       1659, 1660, 1661, 1662, 1663, 1664]:
                return 'slot_machine'
            elif gid in [50, 51, 114, 116, 117, 178, 180, 181, 242, 244, 245]:
                return 'table'
            else:
                return 'floor_fancy'
        
        # Default to floor for any unknown tiles
        else:
            return 'floor'
    
    def is_tile_solid(self, gid):
        """Determine if a tile GID represents a solid/collision tile."""
        # Wall tiles are solid
        if gid in [1478, 1542, 1479, 1477, 1414]:
            return True
            
        # Furniture items are solid (blocking movement)
        elif gid in [1062, 379, 125, 189, 253, 120, 184, 248, 1306, 1307, 1370, 1371, 
                     1434, 1435, 1498, 1499, 1549, 1550, 1613, 1614, 1677, 1678, 1741, 1742,
                     1547, 1548, 1611, 1612, 1675, 1676, 1739, 1740, 1659, 1723, 1724, 1725,
                     1726, 1727, 1728, 1383, 1384, 1385, 1447, 1448, 1449, 1511, 1512, 1513,
                     1575, 1576, 1577, 1601, 1602, 1603, 1665, 1666, 1667, 1729, 1730, 1731,
                     1484, 439, 441, 442, 443, 505, 506, 507, 503, 504]:
            return True
            
        # Some game elements might be solid (like slot machine bases)
        elif gid in [1531, 1532, 1533, 1534, 1535, 1536, 1595, 1596, 1597, 1598, 1599, 1600,
                     1659, 1660, 1661, 1662, 1663, 1664]:
            return True
            
        # Everything else is passable
        else:
            return False
        
        # Map specific tile positions to names (customize these!)
        if tile_x == 1 and tile_y == 1:  # Example: position (1,1) = floor
            return 'floor'
        elif tile_x == 4 and tile_y == 1:  # Example: position (4,1) = wall
            return 'wall'
        elif tile_x == 6 and tile_y == 3:  # Example: blackjack table position
            return 'blackjack_table'
        else:
            return 'floor'  # Default
    
    def create_hardcoded_map(self):
        """Fallback hardcoded map creation."""
    
    def setup_decorative_elements(self):
        """Setup decorative elements for enhanced casino atmosphere"""
        # Use real casino tileset elements!
        tileset_path = TILESET_IMAGE
        
        # Extract various casino elements from the tileset (you can adjust coordinates)
        # These coordinates are examples - we'll refine them based on what you want
        
        # Slot machines from tileset
        slot_machine = self.asset_manager.extract_from_tileset(tileset_path, 224, 96, 32, 32)
        self.asset_manager.register_prop("slot1", slot_machine, (100, 150))
        self.asset_manager.register_prop("slot2", slot_machine, (900, 150))
        
        # Casino tables from tileset
        casino_table = self.asset_manager.extract_from_tileset(tileset_path, 192, 96, 32, 32)
        self.asset_manager.register_prop("table1", casino_table, (200, 200))
        self.asset_manager.register_prop("table2", casino_table, (800, 200))
        
        # GREEN BLACKJACK TABLES - Using the EXACT table from your cropped image
        # This is the curved green blackjack table you specifically pointed out
        
        try:
            # This should be the exact curved green table from your image
            # Based on the cropped section, adjusting coordinates
            green_blackjack_table = self.asset_manager.extract_from_tileset(tileset_path, 225, 352, 96, 48)
        except:
            try:
                # Alternative position for the same table
                green_blackjack_table = self.asset_manager.extract_from_tileset(tileset_path, 320, 352, 96, 48)
            except:
                try:
                    # Try with different size for the curved table
                    green_blackjack_table = self.asset_manager.extract_from_tileset(tileset_path, 288, 320, 96, 64)
                except:
                    try:
                        # The table might be slightly higher or lower
                        green_blackjack_table = self.asset_manager.extract_from_tileset(tileset_path, 256, 320, 128, 64)
                    except:
                        try:
                            # Try the coordinates that worked before but different size
                            green_blackjack_table = self.asset_manager.extract_from_tileset(tileset_path, 256, 352, 96, 48)
                        except:
                            # Final fallback to working coordinates
                            green_blackjack_table = self.asset_manager.extract_from_tileset(tileset_path, 256, 416, 64, 32)
        
        # Place blackjack tables on some of the fancy purple floor tiles in the middle area
        # Row 6 (fancy floor) - place a few tables with better spacing for larger tables
        self.asset_manager.register_prop("blackjack_main1", green_blackjack_table, (250, 180))  # Row 6, left
        self.asset_manager.register_prop("blackjack_main2", green_blackjack_table, (500, 180))  # Row 6, center
        self.asset_manager.register_prop("blackjack_main3", green_blackjack_table, (750, 180))  # Row 6, right
        
        # Row 10 (fancy floor) - add more tables with proper spacing
        self.asset_manager.register_prop("blackjack_lower1", green_blackjack_table, (200, 310))  # Row 10, left
        self.asset_manager.register_prop("blackjack_lower2", green_blackjack_table, (650, 310))  # Row 10, right
        
        # Row 18 (fancy floor) - bottom area tables
        self.asset_manager.register_prop("blackjack_bottom1", green_blackjack_table, (350, 565))  # Row 18, center
        self.asset_manager.register_prop("blackjack_bottom2", green_blackjack_table, (600, 565))  # Row 18, right
        
        # Decorative plants from the 1024x512 tileset in all 4 corners
        larger_tileset = os.path.join(CASINO_TILESET_DIR, '2D_TopDown_Tileset_Casino_1024x512.png')
        
        if os.path.exists(larger_tileset):
            print("Loading plants from 1024x512 tileset...")
            # Use confirmed in-bounds regions (sheet width 1024). Previous coordinates exceeded sheet width.
            # These should be replaced with actual plant cluster coordinates after visual verification.
            plant1 = self.asset_manager.extract_from_tileset(larger_tileset, 896, 384, 64, 64)
            plant2 = self.asset_manager.extract_from_tileset(larger_tileset, 960, 384, 64, 64)
            plant3 = self.asset_manager.extract_from_tileset(larger_tileset, 896, 448, 64, 64)
            plant4 = self.asset_manager.extract_from_tileset(larger_tileset, 960, 448, 64, 64)
            
            # Place plants in all 4 corners of the casino (adjusted positions for visibility)
            # Top-left corner - moved more inward
            self.asset_manager.register_prop("corner_plant_tl", plant1, (64, 64))
            print("Placed plant 1 at (64, 64)")
            
            # Top-right corner - moved more inward
            self.asset_manager.register_prop("corner_plant_tr", plant2, (896, 64))
            print("Placed plant 2 at (896, 64)")
            
            # Bottom-left corner - moved more inward
            self.asset_manager.register_prop("corner_plant_bl", plant3, (64, 640))
            print("Placed plant 3 at (64, 640)")
            
            # Bottom-right corner - moved more inward
            self.asset_manager.register_prop("corner_plant_br", plant4, (896, 640))
            print("Placed plant 4 at (896, 640)")
            
        else:
            print("1024 tileset not found, using fallback plants...")
            # Fallback to smaller tileset plants if 1024 version not available
            plant = self.asset_manager.extract_from_tileset(tileset_path, 320, 96, 32, 32)
            self.asset_manager.register_prop("corner_plant_tl", plant, (64, 64))
            self.asset_manager.register_prop("corner_plant_tr", plant, (896, 64))
            self.asset_manager.register_prop("corner_plant_bl", plant, (64, 640))
            self.asset_manager.register_prop("corner_plant_br", plant, (896, 640))
        
        # Load animated decorative lights
        lights_sheet_path = os.path.join(CASINO_TILESET_DIR, 'Animated Sprite Sheets', 'DecorativeLightsAnimationSheet.png')
        if os.path.exists(lights_sheet_path):
            lights_surface = self.asset_manager.load_animated_sheet(lights_sheet_path)
            lw, lh = lights_surface.get_width(), lights_surface.get_height()
            # Some animated sheets may be shorter than 32px tall; clamp height
            extract_w = min(32, lw)
            extract_h = min(32, lh)
            if extract_h < 32:
                print(f"[INFO] Decorative lights sheet height {lh} < 32; using {extract_h} for extraction to avoid OOB.")
            light_frame = self.asset_manager.extract_from_tileset(lights_sheet_path, 0, 0, extract_w, extract_h)
            y_top = 30
            y_bottom = 700 - (32 - extract_h)  # Adjust if shorter so it sits similarly
            for i, x in enumerate(range(100, 900, 150)):
                self.asset_manager.register_prop(f"light_top_{i}", light_frame, (x, y_top))
                self.asset_manager.register_prop(f"light_bot_{i}", light_frame, (x, y_bottom))
        
        # Load animated slot machines for extra flair
        slot_sheet_path = os.path.join(CASINO_TILESET_DIR, 'Animated Sprite Sheets', 'SlotMachinesAnimationSheet_0.png')
        if os.path.exists(slot_sheet_path):
            animated_slot = self.asset_manager.load_animated_sheet(slot_sheet_path)
            # Extract first frame (adjust coordinates as needed)
            slot_frame = self.asset_manager.extract_from_tileset(slot_sheet_path, 0, 0, 32, 32)
            self.asset_manager.register_prop("animated_slot1", slot_frame, (400, 100))
            self.asset_manager.register_prop("animated_slot2", slot_frame, (600, 100))
    
    def draw(self, surface: pg.Surface):
        """Draw ONLY the TMX map - no decorative elements."""
        # If we have a rendered TMX surface, use that
        if hasattr(self, 'tmx_surface') and self.tmx_surface:
            # Draw the map at its original size (no scaling)
            surface.blit(self.tmx_surface, (0, 0))
        else:
            # Fallback to tile-by-tile rendering
            missing_tiles = set()
            for y, row in enumerate(self.tilemap):
                for x, tile_key in enumerate(row):
                    if tile_key in self.tiles:
                        pos = (x * self.tilesize, y * self.tilesize)
                        surface.blit(self.tiles[tile_key]['image'], pos)
                    else:
                        missing_tiles.add(tile_key)
            
            # Report missing tiles once
            if missing_tiles:
                print(f"Missing tile types in tileset: {missing_tiles}")
                print(f"Available tiles: {list(self.tiles.keys())}")
        
        # Draw NPCs from Tiled object layer
        if hasattr(self, 'npc_objects'):
            for npc in self.npc_objects:
                if 'image' in npc:
                    # Position NPCs at their original object position
                    npc_x = npc['x']
                    npc_y = npc['y'] - npc['height']
                    surface.blit(npc['image'], (npc_x, npc_y))
        
        # NO decorative objects, NO asset manager props, NO extra rendering

        # Optional collision debug overlay (red translucent for solid tiles)
        if self.show_collision_debug:
            overlay = pg.Surface((self.tilesize, self.tilesize), pg.SRCALPHA)
            overlay.fill((255, 0, 0, 90))
            for y, row in enumerate(self.collision_map):
                for x, solid in enumerate(row):
                    if solid:
                        surface.blit(overlay, (x * self.tilesize, y * self.tilesize))
    
    def get_tile_at(self, pos: pg.math.Vector2) -> tuple:
        """Get tile coordinates at world position."""
        # Convert pixel position to tile coordinates
        tile_x = int(pos.x // self.tilesize)
        tile_y = int(pos.y // self.tilesize)
        
        # Debug info for problematic positions
        if pos.x > 960:  # Debug only for problematic positions
            print(f"Debug: pos=({pos.x}, {pos.y}) -> tiles=({tile_x}, {tile_y}), map_size=({len(self.collision_map[0]) if self.collision_map else 0}, {len(self.collision_map)})")
        
        # Check bounds with additional safety for negative coordinates
        if (tile_x >= 0 and tile_y >= 0 and 
            self.collision_map and 
            tile_y < len(self.collision_map) and
            tile_x < len(self.collision_map[0])):
            return (tile_x, tile_y)
        return None
    
    def is_solid_at(self, pos: pg.math.Vector2) -> bool:
        """Check if position is solid for collision."""
        try:
            tile_pos = self.get_tile_at(pos)
            if tile_pos is not None:
                tile_x, tile_y = tile_pos
                is_solid = self.collision_map[tile_y][tile_x]
                # Debug: Print when collision is detected
                if is_solid:
                    print(f"Collision detected at tile ({tile_x}, {tile_y}) / pos ({pos.x:.1f}, {pos.y:.1f})")
                return is_solid
            return True  # Out of bounds = solid
        except Exception as e:
            print(f"Collision error at position {pos}: {e}")
            print(f"Collision map size: {len(self.collision_map)}x{len(self.collision_map[0]) if self.collision_map else 0}")
            return True  # Safe fallback
        
    def create_fallback_tiles(self):
        """Create fallback tiles if tileset fails to load."""
        print("Creating fallback tiles...")
        floor_tile = pg.Surface((self.tilesize, self.tilesize))
        floor_tile.fill((100, 100, 100))  # Gray for floor
        
        wall_tile = pg.Surface((self.tilesize, self.tilesize))
        wall_tile.fill((50, 50, 50))  # Dark gray for walls
        
        table_tile = pg.Surface((self.tilesize, self.tilesize))
        table_tile.fill((139, 69, 19))  # Brown for tables
        
        # Create special blackjack table
        blackjack_tile = pg.Surface((self.tilesize, self.tilesize))
        blackjack_tile.fill((0, 100, 0))  # Dark green
        pg.draw.rect(blackjack_tile, (255, 215, 0), (0, 0, self.tilesize, self.tilesize), 3)  # Gold border
        pg.draw.rect(blackjack_tile, (0, 150, 0), (4, 4, self.tilesize-8, self.tilesize-8))  # Lighter green center
        # Add "BJ" text
        font = pg.font.SysFont('Arial', 16, bold=True)
        text = font.render('BJ', True, (255, 215, 0))
        text_rect = text.get_rect(center=(self.tilesize//2, self.tilesize//2))
        blackjack_tile.blit(text, text_rect)
        
        self.tiles = {
            'floor': {'image': floor_tile, 'solid': False},
            'wall': {'image': wall_tile, 'solid': True},
            'table': {'image': table_tile, 'solid': True},
            'blackjack_table': {'image': blackjack_tile, 'solid': True},
            'empty': {'image': floor_tile.copy(), 'solid': False}
        }