#!/usr/bin/env python3
"""
Test if EW pedestrians are currently spawning.
"""

import sys
import os

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

import pygame
from core.testapp import App

def test_pedestrian_spawning():
    """Test if pedestrians spawn in the current setup."""
    
    print("🚶 Testing EW pedestrian spawning...")
    print("=" * 80)
    
    # Initialize the app
    app = App()
    
    print(f"📊 EW Pedestrian Spawner Configuration:")
    print(f"   interval: {app.ped_ew_spawner.interval}")
    print(f"   random_offset: {app.ped_ew_spawner.random_offset}")
    print(f"   max_count: {app.ped_ew_spawner.max_count}")
    print(f"   _acc: {app.ped_ew_spawner._acc}")
    print(f"   _spawned: {app.ped_ew_spawner._spawned}")
    print()
    
    # Check pedestrian path
    print(f"📍 Pedestrian Path:")
    print(f"   Path: {app.peds_ew_right_px}")
    print(f"   Start position: {app.peds_ew_right_px[0] if app.peds_ew_right_px else 'None'}")
    print()
    
    # Test traffic light conditions
    print(f"🚦 Traffic Light State:")
    print(f"   Can peds cross EW: {app.ctrl.can_ped_cross_ew()}")
    print(f"   Can cars cross EW: {app.ctrl.can_cars_cross_ew()}")
    print()
    
    # Test direct spawning
    print(f"🧪 Direct Spawn Test:")
    try:
        test_ped = app.ped_ew_spawner.factory()
        print(f"   ✅ Factory created: {type(test_ped).__name__} at {test_ped.pos}")
        print(f"   Path start: {test_ped.path[0] if test_ped.path else 'No path'}")
        print(f"   Can cross: {test_ped.can_cross_ok() if hasattr(test_ped, 'can_cross_ok') else 'No method'}")
    except Exception as e:
        print(f"   ❌ Factory error: {e}")
    
    # Test spawner timing with large time step
    dt_large = 6.0  # 6 seconds - should definitely trigger
    print(f"\n⏱️ Testing spawner with large time step ({dt_large}s):")
    
    # Clear agents first
    app.agents = []
    
    print(f"   Before: _acc={app.ped_ew_spawner._acc:.2f}")
    
    # Test direct spawner update
    allow_spawn_func = lambda p=app.peds_ew_right_px: sum(
        1 for a in app.agents
        if getattr(a, "path", None) and a.path[0] == p[0] and not getattr(a, "done", False)
        and ((a.pos[0]-p[0][0])**2 + (a.pos[1]-p[0][1])**2)**0.5 < 180
    ) < 3
    
    # Check allow_spawn first
    can_spawn = allow_spawn_func()
    print(f"   allow_spawn check: {can_spawn}")
    
    # Update spawner
    new_ped = app.ped_ew_spawner.update(dt_large, allow_spawn=can_spawn)
    
    print(f"   After: _acc={app.ped_ew_spawner._acc:.2f}")
    print(f"   _spawned count: {app.ped_ew_spawner._spawned}")
    print(f"   Spawner result: {new_ped}")
    
    if new_ped:
        print(f"   ✅ Spawned pedestrian: {type(new_ped).__name__} at {new_ped.pos}")
        print(f"   Pedestrian path start: {new_ped.path[0] if new_ped.path else 'No path'}")
    else:
        print(f"   ❌ No pedestrian spawned")

if __name__ == "__main__":
    pygame.init()
    test_pedestrian_spawning()
    pygame.quit()