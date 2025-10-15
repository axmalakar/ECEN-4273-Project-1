"""
Cutscene system for game storytelling.
"""
import pygame as pg
from dataclasses import dataclass
from assets import load_image_for_cutscene
from config import WIDTH, HEIGHT


@dataclass
class Slide:
    """A single slide in a cutscene."""
    text: str
    duration: float = 3.0           # seconds before auto-advance (0 = no auto-advance)
    image_name: str | None = None   # optional image in /assets
    bg_color: tuple = (10, 10, 10)  # used if no image found


class Cutscene:
    """Manages cutscene playback with slides."""
    
    def __init__(self, slides: list[Slide], font: pg.font.Font):
        self.slides = slides
        self.index = 0
        self.time_in_slide = 0.0
        self.font = font
        self.image_cache: dict[str, pg.Surface] = {}

    def _get_image(self, name: str | None) -> pg.Surface | None:
        """Get cached image for slide."""
        if not name:
            return None
        if name not in self.image_cache:
            self.image_cache[name] = load_image_for_cutscene(name)
        return self.image_cache[name]

    @property
    def done(self) -> bool:
        """Check if cutscene is finished."""
        return self.index >= len(self.slides)

    def reset(self):
        """Reset cutscene to beginning."""
        self.index = 0
        self.time_in_slide = 0.0

    def handle_event(self, event):
        """Handle input events during cutscene."""
        if self.done:
            return
        if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
            self.advance()

    def advance(self):
        """Move to next slide."""
        self.index += 1
        self.time_in_slide = 0.0

    def update(self, dt: float):
        """Update cutscene timing."""
        if self.done:
            return
        
        slide = self.slides[self.index]
        self.time_in_slide += dt
        
        # Auto-advance if duration > 0
        if slide.duration > 0 and self.time_in_slide >= slide.duration:
            self.advance()

    def draw(self, surface: pg.Surface):
        """Draw current slide."""
        if self.done:
            return
        
        slide = self.slides[self.index]
        
        # Clear with background color
        surface.fill(slide.bg_color)
        
        # Draw image if available
        image = self._get_image(slide.image_name)
        if image:
            # Scale image to fit screen while maintaining aspect ratio
            img_rect = image.get_rect()
            scale_x = WIDTH / img_rect.width
            scale_y = HEIGHT / img_rect.height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
            scaled = pg.transform.scale(image, new_size)
            surface.blit(scaled, scaled.get_rect(center=(WIDTH//2, HEIGHT//2)))
        
        # Draw text with background bubble
        if slide.text:
            # Create text surface
            lines = self._wrap_text(slide.text, WIDTH - 80)
            text_surfaces = [self.font.render(line, True, (255, 255, 255)) for line in lines]
            
            # Calculate bubble size
            max_width = max(surf.get_width() for surf in text_surfaces) if text_surfaces else 0
            total_height = sum(surf.get_height() for surf in text_surfaces) + (len(text_surfaces) - 1) * 5
            bubble_width = max_width + 40
            bubble_height = total_height + 30
            
            # Draw speech bubble
            bubble_rect = pg.Rect(0, 0, bubble_width, bubble_height)
            bubble_rect.centerx = WIDTH // 2
            bubble_rect.bottom = HEIGHT - 50
            
            bubble = pg.Surface((bubble_width, bubble_height), pg.SRCALPHA)
            pg.draw.rect(bubble, (0, 0, 0, 180), bubble.get_rect(), border_radius=15)
            pg.draw.rect(bubble, (255, 255, 255), bubble.get_rect(), width=2, border_radius=15)
            surface.blit(bubble, bubble_rect.topleft)
            
            # Draw text lines
            y_offset = bubble_rect.top + 15
            for text_surf in text_surfaces:
                text_rect = text_surf.get_rect(centerx=bubble_rect.centerx, y=y_offset)
                surface.blit(text_surf, text_rect)
                y_offset += text_surf.get_height() + 5
        
        # Draw prompt
        if slide.duration == 0:  # Manual advance
            prompt = self.font.render("Press any key to continue...", True, (200, 200, 200))
        else:  # Auto advance
            remaining = max(0, slide.duration - self.time_in_slide)
            prompt = self.font.render(f"Next in {remaining:.1f}s (or press any key)", True, (200, 200, 200))
        
        surface.blit(prompt, (WIDTH - prompt.get_width() - 14, HEIGHT - prompt.get_height() - 10))

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, just add it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines