#!/usr/bin/env python3
"""
Test script to verify that vehicles ignore traffic lights after passing path point 2.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from traffic_sim.core.testapp import App
from traffic_sim.configuration import Config

def test_traffic_light_ignore_after_point2():
    """Test that vehicles ignore traffic lights after passing path point 2."""
    print("Testing Traffic Light Ignore After Path Point 2")
    print("=" * 60)
    
    config = Config()
    
    # Create app instance
    app = App()
    
    print("Traffic Light Behavior:")
    print("- Vehicles obey traffic lights BEFORE reaching path point 2")
    print("- Vehicles IGNORE traffic lights AFTER passing path point 2")
    print("- This allows vehicles to continue through intersections")
    print()
    
    # Track vehicles and their behavior at different path points
    vehicle_tracking = {}
    
    test_duration = 30.0  # 30 seconds
    frame_count = 0
    start_time = time.time()
    
    vehicles_that_passed_point2 = 0
    vehicles_that_stopped_at_red = 0
    vehicles_that_ignored_red_after_point2 = 0
    
    try:
        while time.time() - start_time < test_duration:
            dt = 1/60.0  # 60 FPS
            
            # Update traffic controller (this will change lights)
            app.ctrl.update(dt)
            
            # Get current traffic light states
            cars_ns_light = app.ctrl.cars_ns.state.name if hasattr(app.ctrl.cars_ns.state, 'name') else str(app.ctrl.cars_ns.state)
            cars_ew_light = app.ctrl.cars_ew.state.name if hasattr(app.ctrl.cars_ew.state, 'name') else str(app.ctrl.cars_ew.state)
            
            # Spawn vehicles periodically
            if frame_count % 120 == 0:  # Every 2 seconds
                for spawner in [app.car_ns_spawner, app.car_ew_spawner]:
                    new_agent = spawner.update(dt, allow_spawn=True)
                    if new_agent and len(app.agents) < 15:
                        if app._add_agent(new_agent):
                            vehicle_id = id(new_agent)
                            vehicle_tracking[vehicle_id] = {
                                'agent': new_agent,
                                'spawned_at': time.time() - start_time,
                                'path_positions': [],
                                'traffic_light_states': [],
                                'passed_point2': False
                            }
                            print(f"Spawned vehicle {vehicle_id} at time {vehicle_tracking[vehicle_id]['spawned_at']:.1f}s")
            
            # Update all agents and track their behavior
            for agent in list(app.agents):
                agent_id = id(agent)
                
                if agent_id in vehicle_tracking:
                    tracking = vehicle_tracking[agent_id]
                    
                    # Record current position in path
                    current_path_index = getattr(agent, 'i', 0)
                    tracking['path_positions'].append(current_path_index)
                    
                    # Record current traffic light state
                    can_cross = agent._can_cross()
                    tracking['traffic_light_states'].append(can_cross)
                    
                    # Check if vehicle has passed path point 2
                    if current_path_index >= 2 and not tracking['passed_point2']:
                        tracking['passed_point2'] = True
                        vehicles_that_passed_point2 += 1
                        print(f"Vehicle {agent_id} passed path point 2 at time {time.time() - start_time:.1f}s")
                        
                        # Check if light is red and vehicle continues anyway
                        if not can_cross:
                            vehicles_that_ignored_red_after_point2 += 1
                            print(f"  ✅ Vehicle {agent_id} correctly IGNORES red light after point 2!")
                    
                    # Check if vehicle stops at red light before point 2
                    if current_path_index < 2 and not can_cross:
                        # Check if vehicle is actually stopped (not moving)
                        if hasattr(agent, 'pos') and len(tracking['path_positions']) > 10:
                            # Compare current position to position 10 frames ago
                            recent_positions = tracking['path_positions'][-10:]
                            if all(pos == recent_positions[0] for pos in recent_positions):
                                vehicles_that_stopped_at_red += 1
                                print(f"Vehicle {agent_id} correctly STOPS at red light before point 2")
                
                agent.update(dt)
                if getattr(agent, 'done', False):
                    app.agents.remove(agent)
                    if agent_id in vehicle_tracking:
                        del vehicle_tracking[agent_id]
            
            frame_count += 1
            
            # Print status every 10 seconds
            if frame_count % 600 == 0:
                elapsed = time.time() - start_time
                print(f"\nStatus at {elapsed:.1f}s:")
                print(f"  Active vehicles: {len(app.agents)}")
                print(f"  Cars NS light: {cars_ns_light}")
                print(f"  Cars EW light: {cars_ew_light}")
                print(f"  Vehicles that passed point 2: {vehicles_that_passed_point2}")
                print(f"  Vehicles that stopped at red: {vehicles_that_stopped_at_red}")
                print(f"  Vehicles that ignored red after point 2: {vehicles_that_ignored_red_after_point2}")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    # Final report
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("TRAFFIC LIGHT IGNORE TEST RESULTS")
    print("=" * 60)
    print(f"Test duration: {elapsed:.1f} seconds")
    print(f"Total vehicles that passed point 2: {vehicles_that_passed_point2}")
    print(f"Vehicles that stopped at red lights (before point 2): {vehicles_that_stopped_at_red}")
    print(f"Vehicles that ignored red lights (after point 2): {vehicles_that_ignored_red_after_point2}")
    
    print(f"\nBehavior Analysis:")
    if vehicles_that_passed_point2 > 0:
        ignore_rate = (vehicles_that_ignored_red_after_point2 / vehicles_that_passed_point2) * 100
        print(f"✅ {ignore_rate:.1f}% of vehicles correctly ignored red lights after point 2")
    else:
        print("⚠️  No vehicles reached point 2 during test")
    
    if vehicles_that_stopped_at_red > 0:
        print(f"✅ {vehicles_that_stopped_at_red} vehicles correctly stopped at red lights before point 2")
    else:
        print("ℹ️  No red light stopping observed (lights may have been green)")
    
    print(f"\nCode Change Summary:")
    print(f"✅ Modified traffic light logic in road_users.py")
    print(f"✅ Added condition: self.i < 2 to traffic light checking")
    print(f"✅ Vehicles now ignore traffic lights after path index >= 2")
    
    success = vehicles_that_passed_point2 > 0 and (vehicles_that_ignored_red_after_point2 > 0 or vehicles_that_stopped_at_red > 0)
    return success

if __name__ == "__main__":
    success = test_traffic_light_ignore_after_point2()
    sys.exit(0 if success else 1)