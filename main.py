"""
Casino Game - Main Entry Point
A 2D casino game with blackjack, animated characters, and tilemap world.
"""
import os
import sys
import pygame as pg

# Import our modularized components
from config import *
from assets import AssetManager
from player import AnimatedPlayer
from world import World
from cutscenes import Cutscene, Slide
from game_states import GameState
from ad_casino_adapter import BlackjackTable
from npc import NPCManager

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Casino Tycoon")
    clock = pg.time.Clock()
    
    world = World(tilesize=TILE_SIZE)
    
    # Create NPC manager and populate with casino NPCs
    npc_manager = NPCManager()
    npc_manager.create_casino_npcs()
    
    # Position blackjack table for detailed procedural map
    # Place at the main blackjack table position defined in our detailed map
    table_pos = pg.math.Vector2(TILE_SIZE * 12, TILE_SIZE * 9)  # Main blackjack table position
    blackjack_table = BlackjackTable(table_pos)
    
    # Create interaction zone around the table (appropriate for 16x16 tiles)
    interaction_distance = 32  # Distance in pixels to interact with table

    # Ensure assets directory exists
    if not os.path.isdir(ASSET_DIR):
        try:
            os.makedirs(ASSET_DIR, exist_ok=True)
        except Exception:
            pass

    # Create animated player with starting position for detailed procedural map
    # Place player in a safe open area near the entrance
    start_pos = pg.math.Vector2(TILE_SIZE * 15, TILE_SIZE * 20)  # Center-bottom area
    player = AnimatedPlayer(pos=start_pos)

    state = GameState.PLAYING

    # preload font
    font = pg.font.SysFont(None, 24)

    # Define cutscene slides (customize your text/images here)
    slides = [
        Slide("Jim just lost all of his money playing blackjack", duration=3.0, image_name="Image1.png", bg_color=(20,20,35)),
        Slide("Jim is very sad because he has no money and lost his wife.", duration=0, image_name="Image2.png", bg_color=(25,18,18)),
        Slide("Help Jim overcome his fear of rejection and win his life back.", duration=3.5, image_name="Image3.png", bg_color=(10,10,10)),
    ]
    cutscene = Cutscene(slides, font)

    state = GameState.CUTSCENE
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if state == GameState.CUTSCENE:
                cutscene.handle_event(event)
                if cutscene.done:
                    state = GameState.PLAYING

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if state == GameState.PLAYING:
                        state = GameState.PAUSED
                    elif state == GameState.PAUSED:
                        state = GameState.PLAYING
                    elif state == GameState.BLACKJACK:
                        state = GameState.PLAYING
                        blackjack_table.state = 'waiting'
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Handle mouse clicks
                if state == GameState.BLACKJACK:
                    blackjack_table.handle_click(pg.mouse.get_pos())
            elif event.type == pg.KEYDOWN and event.key == pg.K_F1:
                world.show_collision_debug = not world.show_collision_debug
                print(f"Collision debug: {'ON' if world.show_collision_debug else 'OFF'}")

        # Get keyboard state
        keys = pg.key.get_pressed()
        
        # Update logic based on current state
        if state == GameState.CUTSCENE:
            cutscene.update(dt)
            if cutscene.done:
                state = GameState.PLAYING
        elif state == GameState.PLAYING:
            player.handle_input(dt, world)
            npc_manager.update(dt, world)

        if state == GameState.CUTSCENE:
            cutscene.draw(screen)


        # Get keyboard state
        keys = pg.key.get_pressed()
        
        if state == GameState.PLAYING:
            # Handle movement
            player.handle_input(dt, world)
            
            # Check for interaction with blackjack table
            distance_to_table = player.pos.distance_to(table_pos)
            near_table = distance_to_table < interaction_distance
            
            if near_table and keys[pg.K_SPACE]:
                state = GameState.BLACKJACK
                blackjack_table.start_game()
            
            # Check for NPC interactions
            if keys[pg.K_e]:  # Press E to talk to NPCs
                npc_dialogue = npc_manager.check_interactions(player.pos)
                if npc_dialogue:
                    print(f"NPC says: {npc_dialogue}")  # For now, print to console
        
        elif state == GameState.BLACKJACK:
            # Update the blackjack game logic
            blackjack_table.update()
            
            keys = pg.key.get_pressed()
            
            # Keep existing keyboard controls for compatibility
            if blackjack_table.hand_phase == 'betting':
                if keys[pg.K_LEFT]:
                    blackjack_table.adjust_bet(-10)
                elif keys[pg.K_RIGHT]:
                    blackjack_table.adjust_bet(10)
                elif keys[pg.K_SPACE]:
                    blackjack_table.place_bet()
            
            elif blackjack_table.hand_phase == 'player':
                if keys[pg.K_h]:  # Hit
                    blackjack_table.hit()
                elif keys[pg.K_s]:  # Stand
                    blackjack_table.stand()
            
            elif blackjack_table.hand_phase == 'dealer':
                blackjack_table.dealer_play()
                blackjack_table.handle_game_over()
            
            elif blackjack_table.hand_phase == 'done':
                if keys[pg.K_r]:  # Restart
                    blackjack_table.restart()
                elif blackjack_table.bankroll <= 0:
                    # Game over - return to casino
                    state = GameState.PLAYING
                    blackjack_table.state = 'waiting'

        # Draw based on current state
        if state == GameState.CUTSCENE:
            cutscene.draw(screen)
        else:
            # Draw world and game elements
            screen.fill((30, 30, 30))
            
            # Always draw the world and player when not in blackjack
            if state != GameState.BLACKJACK:
                world.draw(screen)
                npc_manager.draw(screen)
                player.draw(screen)
                
                # Real-time player coordinates display (top-left corner)
                coord_font = pg.font.SysFont('Arial', 16, bold=True)
                coord_text = f"Position: ({int(player.pos.x)}, {int(player.pos.y)})"
                coord_surface = coord_font.render(coord_text, True, (255, 255, 0))
                # Add background for better readability
                coord_bg = pg.Surface((coord_surface.get_width() + 10, coord_surface.get_height() + 4))
                coord_bg.fill((0, 0, 0))
                coord_bg.set_alpha(150)
                screen.blit(coord_bg, (5, 5))
                screen.blit(coord_surface, (10, 7))
                
                # Check for interaction with blackjack table and show prompt
                distance_to_table = player.pos.distance_to(table_pos)
                near_table = distance_to_table < interaction_distance
                if near_table:
                    prompt_font = pg.font.SysFont(None, 24)
                    prompt = prompt_font.render("Press SPACE to play Blackjack", True, (255, 255, 255))
                    screen.blit(prompt, (table_pos.x - 100, table_pos.y - 60))
            
            if state == GameState.BLACKJACK:
                blackjack_table.draw(screen)

        # Enhanced HUD
        # Create a semi-transparent overlay for the HUD
        hud_surface = pg.Surface((WIDTH, 40))
        hud_surface.fill((0, 0, 0))
        hud_surface.set_alpha(128)
        screen.blit(hud_surface, (0, 0))
        
        # Game state and controls
        if state == GameState.PLAYING:
            controls_text = ""
        elif state == GameState.BLACKJACK:
            if blackjack_table.hand_phase == 'betting':
                controls_text = "← → Adjust Bet, Space/Click to place bet, Esc to exit"
            elif blackjack_table.hand_phase == 'player':
                controls_text = "H: Hit, S: Stand (or click buttons)"
            elif blackjack_table.hand_phase == 'done':
                controls_text = "R: Play again, Esc to exit (or click Next Hand)\t"
            else:
                controls_text = "Watch the dealer play..."
        else:
            controls_text = f"State: {state.name}"
            
        text = font.render(controls_text, True, (255, 230, 150))  # Warm yellow color
        text_rect = text.get_rect(midtop=(WIDTH // 2, 10))
        screen.blit(text, text_rect)
        screen.blit(text, (10, 10))

        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()