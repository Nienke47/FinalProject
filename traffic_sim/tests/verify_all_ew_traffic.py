#!/usr/bin/env python3
"""
Comprehensive verification of all EW spawners (cars, trucks, bikes, pedestrians).
"""

import sys
import os

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

import pygame
from core.testapp import App

def verify_all_ew_spawners():
    """Verify all EW spawners are working correctly."""
    
    print("🌟 Comprehensive EW Traffic Verification")
    print("=" * 80)
    
    # Initialize the app
    app = App()
    
    # Track all agent types over time
    agent_history = {
        'cars': [],
        'trucks': [],
        'bikes': [],
        'pedestrians': []
    }
    
    total_time = 0.0
    max_time = 15.0  # Run for 15 seconds
    dt = 1/60  # 60 FPS
    
    print(f"🔄 Running simulation for {max_time}s to verify all EW traffic...")
    print(f"🚦 Monitoring: Cars, Trucks, Bikes, and Pedestrians from West to East")
    print()
    
    clock = pygame.time.Clock()
    last_report_time = 0.0
    
    while total_time < max_time:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        total_time += dt
        
        # Update spawner timers and traffic lights (minimal simulation update)
        app.ctrl.update(dt)
        
        # Update all spawners manually to ensure they work
        spawn_items = [
            (app.car_ew_spawner, app.cars_ew_right_px, "Car EW"),
            (app.truck_ew_spawner, app.cars_ew_right_px, "Truck EW"),  
            (app.bike_ew_spawner, app.bikes_ew_right_px, "Bike EW"),
            (app.ped_ew_spawner, app.peds_ew_right_px, "Pedestrian EW")
        ]
        
        for sp, path_px, name in spawn_items:
            if len(app.agents) < 50:  # Prevent overflow
                # Simple allow_spawn function
                allow_spawn_func = lambda p=path_px: sum(
                    1 for a in app.agents
                    if getattr(a, "path", None) and a.path and len(a.path) > 0 and 
                    abs(a.pos[0] - p[0][0]) < 100 and abs(a.pos[1] - p[0][1]) < 100
                    and not getattr(a, "done", False)
                ) < 5
                
                new_agent = sp.update(dt, allow_spawn=allow_spawn_func())
                if new_agent and app._is_safe_spawn_position(new_agent):
                    app.agents.append(new_agent)
                    
                    # Categorize and track the agent
                    agent_type = type(new_agent).__name__.lower()
                    if 'car' in agent_type:
                        agent_history['cars'].append(total_time)
                    elif 'truck' in agent_type:
                        agent_history['trucks'].append(total_time)
                    elif 'cyclist' in agent_type or 'bike' in agent_type:
                        agent_history['bikes'].append(total_time)
                    elif 'pedestrian' in agent_type or 'ped' in agent_type:
                        agent_history['pedestrians'].append(total_time)
                    
                    print(f"   t={total_time:.1f}s: ✅ {name} spawned! (Pos: {new_agent.pos})")
        
        # Update existing agents
        for a in list(app.agents):
            if hasattr(a, 'update'):
                a.update(dt)
            # Remove completed agents
            if getattr(a, "done", False) or (hasattr(a, 'pos') and a.pos[0] > 1200):
                app.agents.remove(a)
        
        # Report status every 3 seconds
        if total_time - last_report_time >= 3.0:
            last_report_time = total_time
            
            # Count current agents
            current_ew_agents = {
                'cars': sum(1 for a in app.agents if 'Car' in type(a).__name__ and a.pos[0] < 500),
                'trucks': sum(1 for a in app.agents if 'Truck' in type(a).__name__ and a.pos[0] < 500),
                'bikes': sum(1 for a in app.agents if 'Cyclist' in type(a).__name__ and a.pos[0] < 500),
                'pedestrians': sum(1 for a in app.agents if 'Pedestrian' in type(a).__name__ and a.pos[0] < 500)
            }
            
            print(f"\n📊 Status at t={total_time:.1f}s:")
            print(f"   Current EW agents: Cars={current_ew_agents['cars']}, Trucks={current_ew_agents['trucks']}, Bikes={current_ew_agents['bikes']}, Pedestrians={current_ew_agents['pedestrians']}")
            print(f"   Total spawned so far: Cars={len(agent_history['cars'])}, Trucks={len(agent_history['trucks'])}, Bikes={len(agent_history['bikes'])}, Pedestrians={len(agent_history['pedestrians'])}")
            print(f"   Traffic: Cars EW: {app.ctrl.can_cars_cross_ew()}, Peds EW: {app.ctrl.can_ped_cross_ew()}")
    
    print(f"\n" + "=" * 80)
    print(f"📈 FINAL RESULTS after {total_time:.1f}s:")
    print(f"   🚗 EW Cars spawned: {len(agent_history['cars'])}")
    print(f"   🚛 EW Trucks spawned: {len(agent_history['trucks'])}")
    print(f"   🚴 EW Bikes spawned: {len(agent_history['bikes'])}")
    print(f"   🚶 EW Pedestrians spawned: {len(agent_history['pedestrians'])}")
    
    # Check success
    success_criteria = {
        'cars': len(agent_history['cars']) > 0,
        'trucks': len(agent_history['trucks']) > 0,
        'bikes': len(agent_history['bikes']) > 0,
        'pedestrians': len(agent_history['pedestrians']) > 0
    }
    
    print(f"\n🎯 SUCCESS EVALUATION:")
    for agent_type, spawned in success_criteria.items():
        status = "✅ WORKING" if spawned else "❌ NOT SPAWNING"
        print(f"   {agent_type.capitalize()}: {status}")
    
    total_success = sum(success_criteria.values())
    print(f"\n📊 Overall: {total_success}/4 EW traffic types are spawning correctly")
    
    if total_success == 4:
        print("🎉 SUCCESS! All EW traffic (cars, trucks, bikes, pedestrians) is spawning from left to right!")
    else:
        print("⚠️  Some EW traffic types are not spawning. Check traffic light timing or spawner configuration.")

if __name__ == "__main__":
    pygame.init()
    verify_all_ew_spawners()
    pygame.quit()