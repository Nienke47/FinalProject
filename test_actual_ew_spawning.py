#!/usr/bin/env python3

"""
Test to verify EW bikes are actually spawning in the running simulation.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_actual_ew_bike_spawning():
    """Test EW bike spawning by monitoring the actual simulation."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.world.intersection import Phase
        import time
        
        print("🔍 Testing actual EW bike spawning in simulation...")
        print()
        
        # Create app
        app = App()
        
        print("📍 Initial Setup:")
        print(f"   Screen size: {app.size}")
        print(f"   EW bike spawner interval: {app.bike_ew_spawner.interval}s ± {app.bike_ew_spawner.random_offset}s")
        print(f"   EW bike paths: {len([app.bikes_ew_right_px, app.bikes_ew_left_px, app.bikes_ew_turn_right_px])}")
        
        # Check spawn configuration
        print()
        print("🔧 Spawn Configuration Check:")
        spawn_items = [
            (app.car_ns_spawner, app.cars_ns_up_px, "Car NS"),
            (app.car_ew_spawner, app.cars_ew_right_px, "Car EW"),  
            (app.truck_ns_spawner, app.cars_ns_up_px, "Truck NS"),   
            (app.truck_ew_spawner, app.cars_ew_right_px, "Truck EW"),
            (app.bike_ns_spawner, app.bikes_ns_up_px, "Bike NS"),   
            (app.bike_ew_spawner, app.bikes_ew_right_px, "Bike EW"),
            (app.ped_ew_spawner, app.peds_ew_right_px, "Ped EW"),
        ]
        
        for spawner, path, name in spawn_items:
            print(f"   {name}: spawn at {path[0] if path else 'NO PATH'}")
        
        # Test spawning manually during different phases
        print()
        print("🚦 Manual Spawning Test During Different Phases:")
        
        app.agents = []  # Clear agents
        bikes_created = 0
        
        for phase in [Phase.EW_CARS_GREEN, Phase.EW_PED_BIKE]:
            app.ctrl._enter_phase(phase)
            print(f"   Testing {phase.name}:")
            
            # Test the crossing function
            can_cross = app.ctrl.can_cars_cross_ew() or app.ctrl.can_ped_cross_ew()
            print(f"     Can cross: {'YES' if can_cross else 'NO'}")
            
            if can_cross:
                # Try to create bike directly
                try:
                    test_bike = app.bike_ew_spawner.factory()
                    print(f"     Factory created bike: {type(test_bike).__name__} at {test_bike.pos}")
                    
                    # Test spawn safety
                    is_safe = app._is_safe_spawn_position(test_bike)
                    print(f"     Spawn position safe: {'YES' if is_safe else 'NO'}")
                    
                    if is_safe:
                        app.agents.append(test_bike)
                        bikes_created += 1
                        print(f"     ✅ Bike added to agents list")
                    else:
                        print(f"     ❌ Bike rejected by spawn safety")
                        
                except Exception as e:
                    print(f"     ❌ Factory failed: {e}")
        
        print(f"   Total EW bikes manually created: {bikes_created}")
        
        # Test the actual spawning loop logic
        print()
        print("🔄 Testing Actual Spawning Loop Logic:")
        
        app.agents = []  # Clear agents
        app.ctrl._enter_phase(Phase.EW_CARS_GREEN)
        
        # Simulate the exact logic from the run() method
        max_total_agents = 30
        spawn_attempts = 0
        successful_spawns = 0
        
        for attempt in range(10):  # Try 10 times
            if len(app.agents) < max_total_agents:
                # Use the exact allow_spawn logic from testapp.py
                path_px = app.bikes_ew_right_px
                allow_spawn = lambda p=path_px: sum(
                    1 for a in app.agents
                    if getattr(a, "path", None) and a.path[0] == p[0] and not getattr(a, "done", False)
                    and ((a.pos[0]-p[0][0])**2 + (a.pos[1]-p[0][1])**2)**0.5 < 180
                ) < 3
                
                spawn_attempts += 1
                allow_result = allow_spawn()
                print(f"   Attempt {attempt + 1}: allow_spawn = {allow_result}")
                
                if allow_result:
                    new_agent = app.bike_ew_spawner.update(0.1, allow_spawn=allow_spawn)  # Small dt
                    if new_agent:
                        if app._add_agent(new_agent):
                            successful_spawns += 1
                            print(f"     ✅ Agent spawned and added: {type(new_agent).__name__} at {new_agent.pos}")
                        else:
                            print(f"     ⚠️ Agent spawned but not added (safety check failed)")
                    else:
                        print(f"     ❌ No agent created by spawner")
                else:
                    print(f"     ❌ Spawn not allowed")
        
        print(f"   Spawn attempts: {spawn_attempts}")
        print(f"   Successful spawns: {successful_spawns}")
        print(f"   Final agent count: {len(app.agents)}")
        
        # Count different types of agents
        ew_bikes = [a for a in app.agents if hasattr(a, 'path') and a.path and len(a.path) > 0 and a.path[0][0] < 0]
        ns_bikes = [a for a in app.agents if hasattr(a, 'path') and a.path and len(a.path) > 0 and a.path[0][1] > 600]
        
        print(f"   EW bikes (X < 0): {len(ew_bikes)}")
        print(f"   NS bikes (Y > 600): {len(ns_bikes)}")
        
        # Check spawner internal state
        print()
        print("⏱️ Spawner Internal State:")
        print(f"   EW bike spawner last spawn time: {getattr(app.bike_ew_spawner, 't_last_spawn', 'N/A')}")
        print(f"   EW bike spawner next spawn time: {getattr(app.bike_ew_spawner, 't_next_spawn', 'N/A')}")
        
        return len(ew_bikes) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing actual EW bike spawning...")
    print("=" * 80)
    
    success = test_actual_ew_bike_spawning()
    
    print()
    print("=" * 80)
    if success:
        print("✅ EW bikes are spawning correctly!")
    else:
        print("❌ EW bikes are still not spawning!")
        print("   Need to investigate the spawner timing or logic.")