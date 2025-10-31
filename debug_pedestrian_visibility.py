#!/usr/bin/env python3
"""
Debug pedestrian visibility by monitoring agent list in real-time.
"""

import sys
import os

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

import pygame
from core.testapp import App

def debug_pedestrian_visibility():
    """Debug pedestrian visibility in real-time."""
    
    print("🔍 Debugging pedestrian visibility in live simulation")
    print("=" * 80)
    
    # Initialize the app
    app = App()
    
    # Track pedestrian lifecycle
    pedestrian_lifecycle = []
    total_time = 0.0
    max_time = 10.0  # Run for 10 seconds
    dt = 1/60  # 60 FPS
    
    print(f"🔄 Running live simulation for {max_time}s...")
    print(f"👀 Monitoring pedestrian spawning, movement, and removal...")
    print()
    
    clock = pygame.time.Clock()
    last_agent_count = 0
    
    while total_time < max_time:
        dt_actual = clock.tick(60) / 1000.0  # Convert to seconds
        total_time += dt_actual
        
        # Update traffic controller (needed for traffic lights)
        app.ctrl.update(dt_actual)
        
        # Process spawning (copied from main loop)
        spawn_items = [
            (app.car_ns_spawner, app.cars_ns_up_px),
            (app.car_ew_spawner, app.cars_ew_right_px),
            (app.truck_ns_spawner, app.cars_ns_up_px),
            (app.truck_ew_spawner, app.cars_ew_right_px),
            (app.bike_ns_spawner, app.bikes_ns_up_px),
            (app.bike_ew_spawner, app.bikes_ew_right_px),
            (app.ped_ew_spawner, app.peds_ew_right_px),  # This is our pedestrian spawner
        ]
        
        max_total_agents = 30
        
        for sp, path_px in spawn_items:
            if len(app.agents) < max_total_agents:
                # Use the same logic as in the actual app
                if sp == app.bike_ew_spawner:
                    # Special handling for EW bike spawner (multiple paths)
                    ew_bike_paths = [app.bikes_ew_right_px, app.bikes_ew_left_px, app.bikes_ew_turn_right_px]
                    allow_spawn = lambda: sum(
                        1 for a in app.agents
                        if getattr(a, "path", None) and any(
                            a.path[0] == bp[0] for bp in ew_bike_paths
                        ) and not getattr(a, "done", False)
                        and any(
                            ((a.pos[0]-bp[0][0])**2 + (a.pos[1]-bp[0][1])**2)**0.5 < 180 
                            for bp in ew_bike_paths
                        )
                    ) < 8
                else:
                    # Standard single-path spawning (including pedestrians)
                    allow_spawn = lambda p=path_px: sum(
                        1 for a in app.agents
                        if getattr(a, "path", None) and a.path[0] == p[0] and not getattr(a, "done", False)
                        and ((a.pos[0]-p[0][0])**2 + (a.pos[1]-p[0][1])**2)**0.5 < 180
                    ) < 3
                
                new_agent = sp.update(dt_actual, allow_spawn=allow_spawn)
                if new_agent:
                    # Only add agent if spawn position is safe
                    if app._add_agent(new_agent):
                        agent_type = type(new_agent).__name__
                        print(f"   t={total_time:.1f}s: ✅ Spawned {agent_type} at {new_agent.pos}")
                        
                        # Special tracking for pedestrians
                        if 'Pedestrian' in agent_type:
                            pedestrian_lifecycle.append({
                                'spawn_time': total_time,
                                'position': list(new_agent.pos),
                                'path': new_agent.path,
                                'agent_id': id(new_agent)
                            })
                            print(f"      🚶 PEDESTRIAN SPAWNED! Path: {new_agent.path}")
        
        # Update agents
        for a in list(app.agents):
            a.update(dt_actual)
            if getattr(a, "done", False):
                agent_type = type(a).__name__
                print(f"   t={total_time:.1f}s: ❌ Removed {agent_type} (done)")
                app.agents.remove(a)
        
        # Count current agents
        current_agents = {
            'total': len(app.agents),
            'pedestrians': sum(1 for a in app.agents if 'Pedestrian' in type(a).__name__),
            'cars': sum(1 for a in app.agents if 'Car' in type(a).__name__),
            'trucks': sum(1 for a in app.agents if 'Truck' in type(a).__name__),
            'bikes': sum(1 for a in app.agents if 'Cyclist' in type(a).__name__)
        }
        
        # Report every 2 seconds
        if int(total_time * 2) % 4 == 0 and int(total_time * 20) % 40 == 0:  # Every 2 seconds
            print(f"\n📊 t={total_time:.1f}s: {current_agents['total']} agents ({current_agents['pedestrians']} peds, {current_agents['cars']} cars, {current_agents['trucks']} trucks, {current_agents['bikes']} bikes)")
            print(f"   Traffic lights: Cars EW={app.ctrl.can_cars_cross_ew()}, Peds EW={app.ctrl.can_ped_cross_ew()}")
            
            # Show pedestrian positions if any exist
            pedestrians = [a for a in app.agents if 'Pedestrian' in type(a).__name__]
            if pedestrians:
                print(f"   Active pedestrians:")
                for i, ped in enumerate(pedestrians):
                    print(f"     {i+1}: Pos=({ped.pos[0]:.0f}, {ped.pos[1]:.0f}), Done={getattr(ped, 'done', False)}")
            else:
                print(f"   ❌ No active pedestrians in agent list")
    
    print(f"\n" + "=" * 80)
    print(f"📈 FINAL ANALYSIS:")
    print(f"   Total pedestrians spawned: {len(pedestrian_lifecycle)}")
    print(f"   Current pedestrians: {sum(1 for a in app.agents if 'Pedestrian' in type(a).__name__)}")
    
    if pedestrian_lifecycle:
        print(f"   ✅ Pedestrians DID spawn!")
        for i, ped_data in enumerate(pedestrian_lifecycle):
            print(f"     {i+1}: Spawned at t={ped_data['spawn_time']:.1f}s, pos={ped_data['position']}")
    else:
        print(f"   ❌ NO pedestrians spawned during simulation")
        print(f"      Check traffic light timing - pedestrians only spawn during EW pedestrian phase")

if __name__ == "__main__":
    pygame.init()
    debug_pedestrian_visibility()
    pygame.quit()