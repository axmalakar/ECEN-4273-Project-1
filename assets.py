"""
Asset management system for loading and caching game resources.
"""
import os
import pygame as pg
from config import CASINO_TILESET_DIR


def load_image(path: str) -> pg.Surface:
    try:
        image = pg.image.load(path)
        return image.convert_alpha() if image.get_alpha() else image.convert()
    except pg.error:
        print(f'Could not load image: {path}')
        return None


class AssetManager:
    def __init__(self):
        self.loaded_images = {}
        self.decorative_elements = {}
        self.casino_props = {}
        self.background_elements = {}
        # Cache for already loaded tileset surfaces to avoid repeated disk IO
        self._tileset_cache: dict[str, pg.Surface] = {}
        
    def load_decorative_image(self, name: str, category: str = "general") -> pg.Surface:
        from config import ASSET_DIR
        
        key = f"{category}_{name}"
        if key not in self.loaded_images:
            # Try multiple possible paths
            possible_paths = [
                os.path.join(ASSET_DIR, name),
                os.path.join(ASSET_DIR, "decorations", name),
                os.path.join(ASSET_DIR, "casino", name),
                os.path.join(ASSET_DIR, "props", name)
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        image = pg.image.load(path).convert_alpha()
                        self.loaded_images[key] = image
                        print(f"Loaded asset: {name} from {path}")
                        return image
                    except Exception as e:
                        print(f"Error loading {path}: {e}")
            
            # Create placeholder if image not found
            print(f"Asset not found: {name}, creating placeholder")
            placeholder = self.create_placeholder(name, category)
            self.loaded_images[key] = placeholder
            return placeholder
        
        return self.loaded_images[key]
    
    def create_placeholder(self, name: str, category: str) -> pg.Surface:
        """Create placeholder graphics for missing assets"""
        size = (32, 32)
        surface = pg.Surface(size, pg.SRCALPHA)
        
        # Different colors for different categories
        colors = {
            "furniture": (139, 69, 19),    # Brown
            "lighting": (255, 255, 0),     # Yellow
            "decoration": (255, 20, 147),  # Pink
            "props": (0, 255, 255),        # Cyan
            "general": (128, 128, 128)     # Gray
        }
        
        color = colors.get(category, colors["general"])
        pg.draw.rect(surface, color, (0, 0, size[0], size[1]))
        pg.draw.rect(surface, (255, 255, 255), (0, 0, size[0], size[1]), 2)
        
        # Add text label
        font = pg.font.SysFont(None, 12)
        text = font.render(name[:4], True, (255, 255, 255))
        text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
        surface.blit(text, text_rect)
        
        return surface
    
    def register_prop(self, name: str, image: pg.Surface, pos: tuple, category: str = "prop"):
        """Register a decorative prop with position"""
        self.casino_props[name] = {
            'image': image,
            'pos': pos,
            'category': category
        }
    
    def get_prop(self, name: str):
        """Get a registered prop"""
        return self.casino_props.get(name)
    
    def extract_from_tileset(self, tileset_path: str, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extract a specific region from a tileset image"""
        try:
            # Load once & cache
            if tileset_path not in self._tileset_cache:
                if not os.path.exists(tileset_path):
                    print(f"[ERROR] Tileset not found: {tileset_path}")
                    return self.create_placeholder("nof", "general")
                self._tileset_cache[tileset_path] = pg.image.load(tileset_path).convert_alpha()
            tileset = self._tileset_cache[tileset_path]

            sheet_w, sheet_h = tileset.get_width(), tileset.get_height()
            # Bounds check
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                print(f"[WARN] Invalid dimensions ({x},{y},{width},{height})")
                return self.create_placeholder("bad", "general")
            if x + width > sheet_w or y + height > sheet_h:
                print(f"[WARN] Out-of-bounds extract ({x},{y},{width},{height}) on sheet {sheet_w}x{sheet_h}")
                return self.create_placeholder("oob", "general")

            extracted = pg.Surface((width, height), pg.SRCALPHA)
            extracted.blit(tileset, (0, 0), (x, y, width, height))
            print(f"Successfully extracted from ({x}, {y}) with size ({width}, {height})")
            return extracted
        except Exception as e:
            print(f"Error extracting from tileset {tileset_path} at ({x}, {y}, {width}, {height}): {e}")
            return self.create_placeholder("err", "general")
    
    def load_animated_sheet(self, sheet_path: str) -> pg.Surface:
        """Load an animated sprite sheet"""
        try:
            return pg.image.load(sheet_path).convert_alpha()
        except Exception as e:
            print(f"Error loading animated sheet {sheet_path}: {e}")
            return self.create_placeholder("anim", "general")
    
    def find_table_coordinates(self, tileset_path: str):
        """Debug method to help find the correct blackjack table coordinates"""
        # This will help us locate the exact table image
        possible_coordinates = [
            (256, 288, 128, 64),   # Location 1
            (384, 288, 128, 64),   # Location 2  
            (320, 256, 128, 64),   # Location 3
            (256, 320, 128, 64),   # Location 4
            (448, 288, 128, 64),   # Location 5
            (256, 352, 128, 64),   # Location 6
        ] 
        
        for i, (x, y, w, h) in enumerate(possible_coordinates):
            try:
                table = self.extract_from_tileset(tileset_path, x, y, w, h)
                print(f"Successfully extracted table {i+1} from coordinates ({x}, {y}, {w}, {h})")
                return table
            except Exception as e:
                print(f"Failed to extract table {i+1} from ({x}, {y}, {w}, {h}): {e}")
                continue
        
        # If none work, return a placeholder
        return self.create_placeholder("table", "furniture")


def load_image_for_cutscene(name: str) -> pg.Surface | None:
    """Load an image for cutscene use."""
    from config import ASSET_DIR
    
    path = os.path.join(ASSET_DIR, name)
    try:
        return pg.image.load(path).convert_alpha()
    except Exception as e:
        print(f"Could not load cutscene image {name}: {e}")
        return None
    

def debug_extract(self, screen: pg.Surface, tileset_path: str, x: int, y: int, width: int, height: int, position: tuple = (10, 10)):
    """Overlay the extracted image onto the given screen for debugging"""
    extracted = self.extract_from_tileset(tileset_path, x, y, width, height)
    screen.blit(extracted, position)
    print(f"Overlayed extraction at {position} on screen")
    return extracted