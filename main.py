import sys
import os
import pygame as pg
from enum import Enum, auto
from dataclasses import dataclass

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()


@dataclass
class Player:
    pos: pg.math.Vector2
    speed: float = 200.0  # pixels per second
    image: pg.Surface = None

    def __post_init__(self):
        # create placeholder if no image provided
        if self.image is None:
            surf = pg.Surface((40, 40), pg.SRCALPHA)
            pg.draw.circle(surf, (50, 150, 250), (20, 20), 20)
            self.image = surf
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def handle_input(self, dt):
        keys = pg.key.get_pressed()
        move = pg.math.Vector2(0, 0)
        if keys[pg.K_w] or keys[pg.K_UP]:
            move.y = -1
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            move.y = 1
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            move.x = -1
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            move.x = 1

        if move.length_squared() > 0:
            move = move.normalize()
            self.pos += move * self.speed * dt
            # clamp to screen bounds
            self.pos.x = max(self.rect.width // 2, min(WIDTH - self.rect.width // 2, self.pos.x))
            self.pos.y = max(self.rect.height // 2, min(HEIGHT - self.rect.height // 2, self.pos.y))
            self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def load_image(name, colorkey=None):
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.isfile(path):
        return None
    try:
        image = pg.image.load(path).convert_alpha()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image
    except Exception as e:
        print(f"Warning: failed to load image '{path}': {e}")
        return None


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Top-Down Casino - Prototype")
    clock = pg.time.Clock()

    # Ensure assets directory exists
    if not os.path.isdir(ASSETS_DIR):
        try:
            os.makedirs(ASSETS_DIR, exist_ok=True)
        except Exception:
            pass

    # Load player image if provided
    player_img = load_image("player.png")

    player = Player(pos=pg.math.Vector2(WIDTH // 2, HEIGHT // 2), image=player_img)

    state = GameState.PLAYING

    # preload font
    font = pg.font.SysFont(None, 24)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if state == GameState.PLAYING:
                        state = GameState.PAUSED
                    elif state == GameState.PAUSED:
                        state = GameState.PLAYING

        if state == GameState.PLAYING:
            player.handle_input(dt)

        # Draw
        screen.fill((30, 30, 30))
        if state in (GameState.PLAYING, GameState.PAUSED):
            player.draw(screen)

        # Simple HUD
        text = font.render(f"State: {state.name} - Use WASD/Arrows to move, Esc to pause", True, (220, 220, 220))
        screen.blit(text, (10, 10))

        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()