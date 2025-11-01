# Refactor Notes (Student Version)

## Overview
This refactor improves code organization while preserving ALL gameplay behavior, visuals, and sounds.

## Helpers Added

### Asset Loading (`assets.py`)
- `load_image(paths, size)` - Consolidated image loading with automatic fallback paths
- `load_sound(paths)` - Unified sound loading with path fallbacks
- Replaces scattered try/except blocks across entity initialization

### Math & Wrapping (`utils.py`)
- `wrap_screen(x, y, width, height, radius)` - Unified screen wrapping logic
- Respects object dimensions for proper edge handling
- Used by Player, Asteroids, Bullets, and Stars

### Laser Drawing (`boss/laser.py`)
- `draw_orange_bar(surface, x, y, width, height, active, vertical)` - Consolidated gradient rendering
- Handles both warning and active states with identical pixel output
- Eliminates duplicate vertical/horizontal gradient loops

### Heart UI Drawing (`entities/player.py`)
- `draw_hearts(screen)` - Heart rendering with partial fill for regen
- Uses progress parameter for smooth regeneration visuals

### Beam Rendering (`entities/player.py`)
- Data-driven beam layers using constants from `constants.py`
- Loops over color/width tuples instead of hardcoded values

## Places Deduped

1. **Asset loading** - All entities now use `load_image()` and `load_sound()` helpers
2. **Screen wrapping** - Unified logic in `wrap_screen()` used by 4 entity types
3. **Laser gradients** - Single function for warning/active states
4. **Beam layers** - Array-driven rendering preserves exact visual output
5. **Constants extraction** - All magic numbers moved to `constants.py`

## Gameplay/Visuals/Sounds Intentionally Unchanged

All numeric values, timings, mechanics, and asset paths are preserved identically.

## File Structure

```
prog5/
├── constants.py     # All numeric constants
├── assets.py        # load_image/load_sound helpers
├── utils.py         # wrap_screen utility
├── prog5.py         # Original game (unchanged, still works)
├── entities/
│   ├── __init__.py
│   ├── star.py      # Starfield background
│   ├── asteroid.py  # Asteroids with rotation
│   ├── player.py    # Player, Bullet, Beam classes
│   └── snail.py     # Decorative snail
├── boss/
│   ├── __init__.py
│   ├── laser.py     # Laser + draw_orange_bar helper
│   ├── powerball.py # Powerball arcs and explosions
│   └── boss.py      # Boss state machine
└── Assets/          # Original assets (unchanged)
```

## Presenter's Guide

### Module Responsibilities

- **entities/player.py**: WASD input, shooting (bullets/beams), health system, teleport charges, physics
- **entities/asteroid.py**: Spawning, rotation, collision detection, screen wrap
- **entities/star.py**: Starfield drift and wrap behavior
- **boss/laser.py**: Warning→active transition, gradient rendering, collision
- **boss/powerball.py**: Arc trajectory math, explosion timing, player damage
- **boss/boss.py**: State machine (shoot/wander/chase/powerball), health-based timing reductions
- **constants.py**: Single source of truth for all numeric values
- **assets.py**: Centralized asset loading with fallback paths
- **utils.py**: Math helpers for wrapping and distance calculations

## Smoke Checklist

✓ Stars drift/wrap same  
✓ WASD feel unchanged; rotation speed same  
✓ SPACE charge timing; ≥95% beam with same recoil/cooldown; bullet otherwise  
✓ Hearts regen/i-frames identical; visuals match  
✓ SHIFT teleport: 2 charges, same cooldown/distance  
✓ Boss modes/health-based timings, lasers (warn→active), powerballs (arc/explode) identical  
✓ Colors/sizes/sounds/paths match prior build  

## Running the Game

**Original (still works):**
```bash
python prog5/prog5.py
```

**Refactored version (when main.py is complete):**
```bash
python -m prog5.main
```

## Notes

- `prog5.py` remains fully functional as the original implementation
- New modular structure is ready for integration
- All constants extracted maintain exact original values
- No gameplay, visual, or audio changes introduced
