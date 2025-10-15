"""
Game configuration constants and settings.
"""
import os

# Screen constants
TILE_SIZE = 16
WIDTH = 512   # 32 tiles (512 ÷ 16) - matches the map size
HEIGHT = 384  # 24 tiles (384 ÷ 16) - matches the map size
FPS = 60

# Colors
BG_COLOR = (20, 12, 28) 
TEXT_COLOR = (230, 150, 0) 

# Asset paths
ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
CASINO_TILESET_DIR = os.path.join(ASSET_DIR, '2D Top Down Pixel Art Tileset Casino')
TILESET_IMAGE = os.path.join(CASINO_TILESET_DIR, '2D_TopDown_Tileset_Casino_1024x512.png')

# Map settings
USE_TILED_MAP = True  # Using your Tiled map design
TILED_MAP_FILE = "map1.tmx"  # Your existing TMX file

# Music settings
MUSIC_FILE = "lobby_music.mp3" 
MUSIC_ENABLED = False

# Debug print paths
print(f"Asset directory: {ASSET_DIR}")
print(f"Casino tileset directory: {CASINO_TILESET_DIR}")
print(f"Looking for tileset at: {TILESET_IMAGE}")
print(f"File exists: {os.path.exists(TILESET_IMAGE)}")
print("Directory contents:")
if os.path.exists(CASINO_TILESET_DIR):
    print(os.listdir(CASINO_TILESET_DIR))