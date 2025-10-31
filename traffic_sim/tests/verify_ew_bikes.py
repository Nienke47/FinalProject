#!/usr/bin/env python3
"""
Final verification - check if EW bikes are spawning in live simulation.
"""

import sys
import os
import time

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

import pygame
from core.testapp import App

def verify_ew_bikes():
    """Verify EW bikes spawn during actual simulation."""
    
    print("🎯 Final verification - EW bike spawning in live simulation")
    print("=" * 80)
    
    # Initialize and run simulation for a short time
    app = App()
    
    # Track EW bikes over time
    ew_bikes_seen = []
    total_time = 0.0
    max_time = 20.0  # Run for 20 seconds
    dt = 1/60  # 60 FPS
    
    print(f"🔄 Running simulation for {max_time}s to check EW bike spawning...")
    
    clock = pygame.time.Clock()
    
    while total_time < max_time:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        total_time += dt
        
        # Update the app (this includes spawner updates)
        app.update(dt)
        
        # Count EW bikes (bikes with X position < 0 or heading east)
        ew_bikes = [
            a for a in app.agents 
            if hasattr(a, 'pos') and hasattr(a, 'path') and a.path and 
            (a.pos[0] < 0 or a.path[0][0] < 100)  # Either off-screen left or starting from left
        ]
        
        # Record new EW bikes
        current_count = len(ew_bikes)
        if current_count > len(ew_bikes_seen):
            new_bikes = current_count - len(ew_bikes_seen)
            ew_bikes_seen.extend([None] * new_bikes)  # Just count them
            print(f"   t={total_time:.1f}s: Found {new_bikes} new EW bike(s)! (Total: {current_count})")
        
        # Print status every 5 seconds
        if int(total_time) % 5 == 0 and int(total_time * 10) % 50 == 0:
            total_agents = len(app.agents)
            cyclists = sum(1 for a in app.agents if 'Cyclist' in type(a).__name__)
            print(f"   t={total_time:.1f}s: {total_agents} total agents, {cyclists} cyclists, {current_count} EW bikes")
            print(f"     Traffic: Cars EW: {app.ctrl.can_cars_cross_ew()}, Peds EW: {app.ctrl.can_ped_cross_ew()}")
    
    print(f"\n📊 Final Results after {total_time:.1f}s:")
    print(f"   Total EW bikes spawned: {len(ew_bikes_seen)}")
    print(f"   Current EW bikes on screen: {len(ew_bikes)}")
    
    if len(ew_bikes_seen) > 0:
        print(f"   ✅ SUCCESS! EW bikes are spawning from the left side!")
        print(f"   Rate: ~{len(ew_bikes_seen) / total_time * 60:.1f} EW bikes per minute")
    else:
        print(f"   ❌ STILL BROKEN - No EW bikes spawned")
        
        # Debug info
        print(f"\n🔧 Debug Info:")
        print(f"   Total agents: {len(app.agents)}")
        print(f"   Total cyclists: {sum(1 for a in app.agents if 'Cyclist' in type(a).__name__)}")
        print(f"   EW spawner interval: {app.bike_ew_spawner.interval}s")
        print(f"   EW spawner count: {app.bike_ew_spawner._spawned}")
        print(f"   EW spawner accumulator: {app.bike_ew_spawner._acc:.2f}")
        
        # Show agent positions
        cyclists = [a for a in app.agents if 'Cyclist' in type(a).__name__]
        if cyclists:
            print(f"   Cyclist positions:")
            for i, c in enumerate(cyclists):
                print(f"     {i+1}: {type(c).__name__} at ({c.pos[0]:.0f}, {c.pos[1]:.0f})")

if __name__ == "__main__":
    pygame.init()
    verify_ew_bikes()
    pygame.quit()