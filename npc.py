"""
NPC classes for the casino game.
"""
import pygame as pg
import random
from typing import List, Tuple

class NPC:
    """Base NPC class."""
    
    def __init__(self, pos: pg.math.Vector2, npc_type: str = "patron"):
        self.pos = pos
        self.npc_type = npc_type
        self.dialogue = self.get_default_dialogue()
        self.sprite_color = self.get_sprite_color()
        self.size = pg.math.Vector2(24, 24)  # Slightly smaller than tiles
        self.move_timer = 0
        self.move_direction = pg.math.Vector2(0, 0)
        self.move_speed = 20  # pixels per second
        self.dialogue_shown = False
        self.sprite_image = self.load_sprite()
        
    def load_sprite(self) -> pg.Surface:
        """Load sprite image for this NPC type."""
        # Try to load from tileset first
        try:
            from assets import AssetManager
            from config import TILESET_IMAGE
            
            asset_manager = AssetManager()
            
            # Define sprite coordinates in your tileset (you'll need to adjust these)
            sprite_coords = {
                "dealer": (224, 448, 32, 32),     # Adjust based on your tileset
                "security": (256, 448, 32, 32),   # Adjust based on your tileset  
                "patron": (288, 448, 32, 32),     # Adjust based on your tileset
                "bartender": (320, 448, 32, 32),  # Adjust based on your tileset
                "hostess": (352, 448, 32, 32)     # Adjust based on your tileset
            }
            
            if self.npc_type in sprite_coords:
                x, y, w, h = sprite_coords[self.npc_type]
                sprite = asset_manager.extract_from_tileset(TILESET_IMAGE, x, y, w, h)
                return pg.transform.scale(sprite, (int(self.size.x), int(self.size.y)))
        except Exception as e:
            print(f"Could not load sprite for {self.npc_type}: {e}")
        
        # Fallback: create a simple colored sprite
        return self.create_fallback_sprite()
    
    def create_fallback_sprite(self) -> pg.Surface:
        """Create a simple sprite if image loading fails."""
        # Use the sprite creator for better looking sprites
        try:
            from sprite_creator import SpriteCreator
            return SpriteCreator.create_npc_sprite(self.npc_type, (int(self.size.x), int(self.size.y)))
        except ImportError:
            pass
        
        # Ultimate fallback: simple colored sprite
        sprite = pg.Surface((int(self.size.x), int(self.size.y)), pg.SRCALPHA)
        
        # Create different shapes for different NPC types
        if self.npc_type == "dealer":
            # Rectangle with tie (professional look)
            pg.draw.rect(sprite, self.sprite_color, (0, 0, int(self.size.x), int(self.size.y)))
            pg.draw.rect(sprite, (255, 255, 255), (8, 4, 8, 16))  # White shirt
            pg.draw.rect(sprite, (0, 0, 0), (10, 6, 4, 12))      # Black tie
        elif self.npc_type == "security":
            # Rectangle with badge
            pg.draw.rect(sprite, self.sprite_color, (0, 0, int(self.size.x), int(self.size.y)))
            pg.draw.circle(sprite, (255, 215, 0), (18, 8), 4)    # Gold badge
        elif self.npc_type == "patron":
            # Simple oval (casual look)
            pg.draw.ellipse(sprite, self.sprite_color, (0, 0, int(self.size.x), int(self.size.y)))
        else:
            # Default circle
            pg.draw.circle(sprite, self.sprite_color, 
                         (int(self.size.x//2), int(self.size.y//2)), 
                         int(self.size.x//2))
        
        # Add simple face
        eye_size = 2
        pg.draw.circle(sprite, (255, 255, 255), (int(self.size.x//2 - 4), int(self.size.y//2 - 2)), eye_size)
        pg.draw.circle(sprite, (255, 255, 255), (int(self.size.x//2 + 4), int(self.size.y//2 - 2)), eye_size)
        pg.draw.circle(sprite, (0, 0, 0), (int(self.size.x//2 - 4), int(self.size.y//2 - 2)), 1)
        pg.draw.circle(sprite, (0, 0, 0), (int(self.size.x//2 + 4), int(self.size.y//2 - 2)), 1)
        
        return sprite
        
    def get_default_dialogue(self) -> str:
        """Get default dialogue based on NPC type."""
        dialogues = {
            "dealer": "Welcome to my table! Care to play?",
            "security": "Keep it clean, folks.",
            "patron": random.choice([
                "I'm feeling lucky tonight!",
                "This place is amazing!",
                "Have you tried the blackjack table?",
                "The slots are calling my name!",
                "I love the atmosphere here!"
            ]),
            "bartender": "What can I get you to drink?",
            "hostess": "Welcome to our casino!"
        }
        return dialogues.get(self.npc_type, "Hello there!")
    
    def get_sprite_color(self) -> Tuple[int, int, int]:
        """Get sprite color based on NPC type."""
        colors = {
            "dealer": (50, 50, 150),      # Dark blue (professional)
            "security": (100, 50, 50),    # Dark red (authority)
            "patron": (100, 150, 100),    # Green (neutral)
            "bartender": (150, 100, 50),  # Brown (service)
            "hostess": (150, 50, 150)     # Purple (welcoming)
        }
        return colors.get(self.npc_type, (100, 100, 100))
    
    def update(self, dt: float, world):
        """Update NPC behavior."""
        if self.npc_type == "patron":
            self.wander(dt, world)
    
    def wander(self, dt: float, world):
        """Simple wandering behavior for patrons."""
        self.move_timer -= dt
        
        if self.move_timer <= 0:
            # Choose new random direction
            directions = [
                pg.math.Vector2(1, 0),   # Right
                pg.math.Vector2(-1, 0),  # Left
                pg.math.Vector2(0, 1),   # Down
                pg.math.Vector2(0, -1),  # Up
                pg.math.Vector2(0, 0)    # Stop
            ]
            self.move_direction = random.choice(directions)
            self.move_timer = random.uniform(1.0, 3.0)  # Move for 1-3 seconds
        
        # Move in current direction
        if self.move_direction.length() > 0:
            new_pos = self.pos + self.move_direction * self.move_speed * dt
            
            # Check collision with world
            if not world.is_solid_at(new_pos):
                self.pos = new_pos
    
    def draw(self, surface: pg.Surface):
        """Draw the NPC."""
        # Draw the sprite image
        sprite_rect = self.sprite_image.get_rect()
        sprite_rect.center = (int(self.pos.x), int(self.pos.y))
        surface.blit(self.sprite_image, sprite_rect)
        
        # Optional: Draw NPC type indicator for debugging
        # font = pg.font.SysFont('Arial', 10)
        # text = font.render(self.npc_type[0].upper(), True, (255, 255, 255))
        # text_rect = text.get_rect(center=(int(self.pos.x), int(self.pos.y - 15)))
        # surface.blit(text, text_rect)
    
    def interact(self) -> str:
        """Return dialogue when player interacts."""
        return self.dialogue
    
    def is_near_player(self, player_pos: pg.math.Vector2, distance: float = 50) -> bool:
        """Check if player is close enough to interact."""
        return self.pos.distance_to(player_pos) < distance


class NPCManager:
    """Manages all NPCs in the game."""
    
    def __init__(self):
        self.npcs: List[NPC] = []
    
    def add_npc(self, npc: NPC):
        """Add an NPC to the manager."""
        self.npcs.append(npc)
    
    def create_casino_npcs(self):
        """Create default NPCs for the casino (optimized for detailed procedural map)."""
        # Dealers at blackjack tables (positioned according to our detailed procedural map)
        self.add_npc(NPC(pg.math.Vector2(12 * 16, 8 * 16), "dealer"))  # Main blackjack table
        self.add_npc(NPC(pg.math.Vector2(16 * 16, 8 * 16), "dealer"))  # Second blackjack table
        
        # Security guards (positioned strategically around the casino)
        self.add_npc(NPC(pg.math.Vector2(5 * 16, 5 * 16), "security"))   # Top-left area
        self.add_npc(NPC(pg.math.Vector2(26 * 16, 18 * 16), "security"))  # Bottom-right area
        
        # Patrons wandering around (spread across the gaming areas)
        patron_positions = [
            (10 * 16, 10 * 16),  # Main gaming area
            (14 * 16, 11 * 16),  # Near blackjack tables
            (20 * 16, 15 * 16),  # Bottom gaming area
            (22 * 16, 6 * 16),   # VIP area
            (8 * 16, 18 * 16),   # Bottom gaming area
            (18 * 16, 17 * 16),  # Slot machine area
            (25 * 16, 12 * 16)   # Right side
        ]
        for pos in patron_positions:
            self.add_npc(NPC(pg.math.Vector2(pos[0], pos[1]), "patron"))
        
        # Hostess near entrance area
        self.add_npc(NPC(pg.math.Vector2(15 * 16, 20 * 16), "hostess"))
    
    def load_npcs_from_tiled(self, tmx_data):
        """Load NPCs from Tiled object layer."""
        for obj in tmx_data.objects:
            if hasattr(obj, 'type') and obj.type == 'npc':
                npc_type = getattr(obj, 'npc_type', 'patron')
                npc = NPC(pg.math.Vector2(obj.x, obj.y), npc_type)
                
                # Override dialogue if specified in Tiled
                if hasattr(obj, 'dialogue'):
                    npc.dialogue = obj.dialogue
                
                self.add_npc(npc)
    
    def update(self, dt: float, world):
        """Update all NPCs."""
        for npc in self.npcs:
            npc.update(dt, world)
    
    def draw(self, surface: pg.Surface):
        """Draw all NPCs."""
        for npc in self.npcs:
            npc.draw(surface)
    
    def check_interactions(self, player_pos: pg.math.Vector2) -> str:
        """Check if player can interact with any NPC."""
        for npc in self.npcs:
            if npc.is_near_player(player_pos):
                return npc.interact()
        return None