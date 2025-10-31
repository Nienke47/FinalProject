#!/usr/bin/env python3
"""
Test spawner timing by simulating the exact conditions in the app.
"""

import sys
import os

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

import pygame
from core.testapp import App

def test_spawner_in_app():
    """Test the spawner directly in the app environment."""
    
    print("🔍 Testing EW bike spawner timing in TestApp...")
    print("=" * 80)
    
    # Initialize the app
    app = App()
    
    print(f"📊 EW Bike Spawner Configuration:")
    print(f"   interval: {app.bike_ew_spawner.interval}")
    print(f"   random_offset: {app.bike_ew_spawner.random_offset}")
    print(f"   max_count: {app.bike_ew_spawner.max_count}")
    print(f"   _acc: {app.bike_ew_spawner._acc}")
    print(f"   _spawned: {app.bike_ew_spawner._spawned}")
    print()
    
    # Check current traffic light state
    print(f"🚦 Current traffic light phase:")
    print(f"   Can cars cross EW: {app.ctrl.can_cars_cross_ew()}")
    print(f"   Can peds cross EW: {app.ctrl.can_ped_cross_ew()}")
    print()
    
    # Test the spawner update directly with large time step
    dt_large = 5.0  # 5 seconds - definitely should trigger
    print(f"⏱️ Testing spawner with large time step ({dt_large}s):")
    
    # Clear agents first
    app.agents = []
    
    # Test direct spawner update
    print(f"   Before: _acc={app.bike_ew_spawner._acc:.2f}")
    
    # Call spawner update directly (simulating what happens in main loop)
    ew_bike_paths = [app.bikes_ew_right_px, app.bikes_ew_left_px, app.bikes_ew_turn_right_px]
    allow_spawn_func = lambda: sum(
        1 for a in app.agents
        if getattr(a, "path", None) and any(
            a.path[0] == bp[0] for bp in ew_bike_paths
        ) and not getattr(a, "done", False)
        and any(
            ((a.pos[0]-bp[0][0])**2 + (a.pos[1]-bp[0][1])**2)**0.5 < 180 
            for bp in ew_bike_paths
        )
    ) < 8
    
    # Check allow_spawn first
    can_spawn = allow_spawn_func()
    print(f"   allow_spawn check: {can_spawn}")
    
    # Update spawner
    new_bike = app.bike_ew_spawner.update(dt_large, allow_spawn=can_spawn)
    
    print(f"   After: _acc={app.bike_ew_spawner._acc:.2f}")
    print(f"   _spawned count: {app.bike_ew_spawner._spawned}")
    print(f"   Spawner result: {new_bike}")
    
    if new_bike:
        print(f"   ✅ Spawned bike: {type(new_bike).__name__} at {new_bike.pos}")
        print(f"   Bike path start: {new_bike.path[0] if new_bike.path else 'No path'}")
    else:
        print(f"   ❌ No bike spawned")
    
    # Test factory directly
    print(f"\n🏭 Testing factory directly:")
    try:
        direct_bike = app.bike_ew_spawner.factory()
        print(f"   ✅ Factory created: {type(direct_bike).__name__} at {direct_bike.pos}")
        print(f"   Factory bike path start: {direct_bike.path[0] if direct_bike.path else 'No path'}")
    except Exception as e:
        print(f"   ❌ Factory error: {e}")
    
    # Test with multiple small steps to simulate real gameplay
    print(f"\n🔄 Testing with realistic 60 FPS updates:")
    app.bike_ew_spawner._acc = 0.0  # Reset accumulator
    app.bike_ew_spawner._spawned = 0  # Reset count
    
    dt_fps = 1.0 / 60.0  # 60 FPS
    total_time = 0.0
    spawned_bikes = 0
    
    for frame in range(300):  # 5 seconds at 60 FPS
        total_time += dt_fps
        
        new_bike = app.bike_ew_spawner.update(dt_fps, allow_spawn=True)
        if new_bike:
            spawned_bikes += 1
            print(f"   Frame {frame+1}: t={total_time:.2f}s - ✅ SPAWNED! (Total: {spawned_bikes})")
            
        # Print status every second
        if frame % 60 == 59:
            print(f"   t={total_time:.1f}s: _acc={app.bike_ew_spawner._acc:.3f}, spawned={spawned_bikes}")
    
    print(f"\n📈 Final Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Total spawned: {spawned_bikes}")
    print(f"   Spawner count: {app.bike_ew_spawner._spawned}")
    print(f"   Expected spawns: ~{total_time / 3.0:.1f} (every ~3s)")

if __name__ == "__main__":
    pygame.init()
    test_spawner_in_app()
    pygame.quit()