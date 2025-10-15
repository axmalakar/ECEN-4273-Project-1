"""
Player character class with animation and movement.
"""
import pygame as pg
from config import TILE_SIZE


class AnimatedPlayer:
    """Animated player character with walking animations for all directions."""
    
    def __init__(self, pos: pg.math.Vector2, speed: float = 200.0):
        self.pos = pos
        self.speed = speed
        self.direction = 'down'  
        self.moving = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Time between frames in seconds
        
        # Create walking animations for all directions
        self.sprites = self.create_walking_sprites()
        self.current_sprite = self.sprites[self.direction][0]
        self.rect = self.current_sprite.get_rect(center=(round(self.pos.x), round(self.pos.y)))
    
    def create_walking_sprites(self):
        """Create animated walking sprites for all directions"""
        sprites = {
            'up': [],
            'down': [],
            'left': [],
            'right': []
        }
        
        # Character colors
        body_color = (100, 150, 255)  # Blue shirt
        skin_color = (255, 220, 177)  # Skin tone
        hair_color = (139, 69, 19)    # Brown hair
        pants_color = (50, 50, 50)    # Dark pants
        shoe_color = (0, 0, 0)        # Black shoes
        
        # Create frames for each direction
        for direction in sprites.keys():
            for frame in range(3):  # 3 walking frames per direction
                sprite = self.create_character_frame(direction, frame, 
                                                   body_color, skin_color, hair_color, 
                                                   pants_color, shoe_color)
                sprites[direction].append(sprite)
        
        return sprites
    
    def create_character_frame(self, direction, frame, body_color, skin_color, 
                             hair_color, pants_color, shoe_color):
        
        sprite = pg.Surface((32, 32), pg.SRCALPHA)
        
        # Calculate offsets for walking animation
        bob_offset = 0
        leg_offset = 0
        if frame == 1:  # Middle frame - highest step
            bob_offset = -1
            leg_offset = 1
        elif frame == 2:  # Frame 2 - other leg forward
            leg_offset = -1
        
        if direction == 'down':  # Facing down (towards camera)
            # Head
            pg.draw.circle(sprite, skin_color, (16, 8 + bob_offset), 6)
            # Hair
            pg.draw.circle(sprite, hair_color, (16, 6 + bob_offset), 5)
            # Body
            pg.draw.rect(sprite, body_color, (12, 12 + bob_offset, 8, 10))
            # Legs
            pg.draw.rect(sprite, pants_color, (13, 22 + bob_offset, 2, 6))
            pg.draw.rect(sprite, pants_color, (17, 22 + bob_offset, 2, 6))
            # Feet (animated)
            pg.draw.rect(sprite, shoe_color, (12, 27 + bob_offset + leg_offset, 3, 2))
            pg.draw.rect(sprite, shoe_color, (17, 27 + bob_offset - leg_offset, 3, 2))
            # Arms
            pg.draw.rect(sprite, skin_color, (10, 14 + bob_offset, 2, 6))
            pg.draw.rect(sprite, skin_color, (20, 14 + bob_offset, 2, 6))
            
        elif direction == 'up':  # Facing up (away from camera)
            # Head (back of head)
            pg.draw.circle(sprite, skin_color, (16, 8 + bob_offset), 6)
            # Hair (back)
            pg.draw.circle(sprite, hair_color, (16, 6 + bob_offset), 5)
            # Body
            pg.draw.rect(sprite, body_color, (12, 12 + bob_offset, 8, 10))
            # Legs
            pg.draw.rect(sprite, pants_color, (13, 22 + bob_offset, 2, 6))
            pg.draw.rect(sprite, pants_color, (17, 22 + bob_offset, 2, 6))
            # Feet (animated)
            pg.draw.rect(sprite, shoe_color, (12, 27 + bob_offset - leg_offset, 3, 2))
            pg.draw.rect(sprite, shoe_color, (17, 27 + bob_offset + leg_offset, 3, 2))
            # Arms
            pg.draw.rect(sprite, skin_color, (10, 14 + bob_offset, 2, 6))
            pg.draw.rect(sprite, skin_color, (20, 14 + bob_offset, 2, 6))
            
        elif direction == 'left':  # Facing left (side view)
            # Head
            pg.draw.circle(sprite, skin_color, (16, 8 + bob_offset), 6)
            # Hair
            pg.draw.circle(sprite, hair_color, (16, 6 + bob_offset), 5)
            # Body
            pg.draw.rect(sprite, body_color, (12, 12 + bob_offset, 8, 10))
            # Legs (walking animation)
            if frame == 0:
                pg.draw.rect(sprite, pants_color, (14, 22 + bob_offset, 3, 6))
                pg.draw.rect(sprite, pants_color, (16, 22 + bob_offset, 3, 6))
            elif frame == 1:
                pg.draw.rect(sprite, pants_color, (13, 22 + bob_offset, 3, 6))
                pg.draw.rect(sprite, pants_color, (17, 22 + bob_offset, 3, 6))
            else:
                pg.draw.rect(sprite, pants_color, (15, 22 + bob_offset, 3, 6))
                pg.draw.rect(sprite, pants_color, (15, 22 + bob_offset, 3, 6))
            # Feet
            pg.draw.rect(sprite, shoe_color, (12, 27 + bob_offset, 4, 2))
            pg.draw.rect(sprite, shoe_color, (17, 27 + bob_offset, 4, 2))
            # Arms
            pg.draw.rect(sprite, skin_color, (10, 14 + bob_offset, 2, 6))
            pg.draw.rect(sprite, skin_color, (20, 14 + bob_offset, 2, 6))
            
        elif direction == 'right':  # Facing right (side view)
            # Head
            pg.draw.circle(sprite, skin_color, (16, 8 + bob_offset), 6)
            # Hair
            pg.draw.circle(sprite, hair_color, (16, 6 + bob_offset), 5)
            # Body
            pg.draw.rect(sprite, body_color, (12, 12 + bob_offset, 8, 10))
            # Legs (walking animation)
            if frame == 0:
                pg.draw.rect(sprite, pants_color, (14, 22 + bob_offset, 3, 6))
                pg.draw.rect(sprite, pants_color, (16, 22 + bob_offset, 3, 6))
            elif frame == 1:
                pg.draw.rect(sprite, pants_color, (13, 22 + bob_offset, 3, 6))
                pg.draw.rect(sprite, pants_color, (17, 22 + bob_offset, 3, 6))
            else:
                pg.draw.rect(sprite, pants_color, (15, 22 + bob_offset, 3, 6))
                pg.draw.rect(sprite, pants_color, (15, 22 + bob_offset, 3, 6))
            # Feet
            pg.draw.rect(sprite, shoe_color, (11, 27 + bob_offset, 4, 2))
            pg.draw.rect(sprite, shoe_color, (16, 27 + bob_offset, 4, 2))
            # Arms
            pg.draw.rect(sprite, skin_color, (10, 14 + bob_offset, 2, 6))
            pg.draw.rect(sprite, skin_color, (20, 14 + bob_offset, 2, 6))
        
        return sprite
    
    def update_animation(self, dt: float):
        """Update animation frame based on movement"""
        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3
                self.current_sprite = self.sprites[self.direction][self.animation_frame]
        else:
            # Reset to idle frame when not moving
            self.animation_frame = 0
            self.current_sprite = self.sprites[self.direction][0]
    
    def handle_input(self, dt: float, world):
        """Handle player input for movement"""
        keys = pg.key.get_pressed()
        
        # Store old position for collision checking
        old_pos = pg.math.Vector2(self.pos)
        self.moving = False
        
        # Movement input
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.direction = 'up'
            new_pos = pg.math.Vector2(self.pos.x, self.pos.y - self.speed * dt)
            if not world.is_solid_at(new_pos):
                self.pos.y = new_pos.y
                self.moving = True
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.direction = 'down'
            new_pos = pg.math.Vector2(self.pos.x, self.pos.y + self.speed * dt)
            if not world.is_solid_at(new_pos):
                self.pos.y = new_pos.y
                self.moving = True
        
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.direction = 'left'
            new_pos = pg.math.Vector2(self.pos.x - self.speed * dt, self.pos.y)
            if not world.is_solid_at(new_pos):
                self.pos.x = new_pos.x
                self.moving = True
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.direction = 'right'
            new_pos = pg.math.Vector2(self.pos.x + self.speed * dt, self.pos.y)
            if not world.is_solid_at(new_pos):
                self.pos.x = new_pos.x
                self.moving = True
        
        # Update animation
        self.update_animation(dt)
        
        # Update collision rect
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    
    def draw(self, surface: pg.Surface):
        """Draw the player sprite"""
        surface.blit(self.current_sprite, self.rect)