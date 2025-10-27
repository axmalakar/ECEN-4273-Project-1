
# ECEN-4273-Project-1
Game 1 
# Casino Tycoon (ECEN-4273 Project 1)

A 2D top-down casino prototype built with [pygame](https://www.pygame.org/). Explore a tile-based resort, watch an introductory cutscene, interact with animated NPCs, and sit down for a round of blackjack using the casino's in-house ruleset. The project demonstrates modular game architecture for ECEN 4273.

## Features

- **Playable overworld:** Navigate a 32x24 tile casino rendered from a Tiled (`.tmx`) map or the procedural fallback layout, complete with collision boundaries.
- **Animated main character:** Smooth sprite-based walking animations that react to keyboard input and support collision-aware movement.
- **Blackjack table mini-game:** Adjustable bets, hit/stand decision phases, bankroll tracking, and table state management encapsulated in `ad_casino_adapter.BlackjackTable`.
- **NPC crowd simulation:** Dealers, security, patrons, and a hostess wander and deliver flavor dialogue when you interact with them.
- **Cinematic intro:** A short `cutscenes.Cutscene` sequence sets the story tone before gameplay begins.
- **Asset management:** Centralized loading and slicing of sprites/tiles through `assets.AssetManager`, with graceful fallbacks if files are missing.

## Project Structure

Key modules include:

| File | Purpose |
| --- | --- |
| `main.py` | Game entry point, state machine, event loop, cutscene, and blackjack integration. |
| `config.py` | Global constants such as resolution, frame rate, asset directories, and map configuration. |
| `world.py` | Tile loading, Tiled map rendering, collision checks, and optional ambiance. |
| `player.py` | `AnimatedPlayer` class for movement, animation, and drawing. |
| `npc.py` | `NPC` and `NPCManager` classes for populating the casino with interactive characters. |
| `assets.py` | Utility helpers for loading textures, sprites, and fallback art. |
| `cutscenes.py` | `Cutscene` and `Slide` helpers for the intro sequence. |
| `ad_casino_adapter.py` | Blackjack table logic and UI helpers. |

Asset files (tile sets, character sprites, cutscene images, etc.) live alongside the code in the repository. Ensure any zipped assets are extracted before running.

## Requirements

- Python 3.9+
- [pygame](https://pypi.org/project/pygame/) 2.5 or newer
- [pytmx](https://pypi.org/project/pytmx/) (optional, for loading the authored `.tmx` map)

Install the dependencies with pip:

```bash
python -m pip install -r requirements.txt
```

If a `requirements.txt` file is unavailable, install the core libraries manually:

```bash
python -m pip install pygame pytmx
```

## Running the Game

1. Ensure that the `assets/` directory contains the tileset (`2D_TopDown_Tileset_Casino_1024x512.png`), sprite sheets, and cutscene images referenced by the code.
2. From the project root, launch the game:

   ```bash
   python main.py
   ```

   The terminal will print asset-loading diagnostics from `config.py` and `world.py` to help troubleshoot missing files.

3. If `pytmx` cannot load `map1.tmx`, the world automatically falls back to the procedural layout defined in `world.py`.

## Controls

| Action | Keys |
| --- | --- |
| Move | `W`, `A`, `S`, `D` or arrow keys |
| Interact with blackjack table | Stand near the table and press `Space` |
| Interact with NPCs | `E` |
| Toggle collision debug overlay | `F1` |
| Pause / Resume | `Esc` |
| Blackjack – adjust bet | `←` / `→` |
| Blackjack – confirm bet | `Space` |
| Blackjack – hit / stand | `H` / `S` |
| Blackjack – restart after round | `R` |

## Troubleshooting

- If pygame cannot locate the tileset, confirm the asset path printed in the console matches the actual file location.
- When running without a display (e.g., on a headless server), set the SDL video driver to `dummy` before launching:

  ```bash
  SDL_VIDEODRIVER=dummy python main.py
  ```

- Disable music by leaving `MUSIC_ENABLED = False` in `config.py` or provide the referenced `lobby_music.mp3` file.

## License

No explicit license has been provided. Consult the course instructors or repository owner before reusing or distributing the project.
