#!/usr/bin/env python3
"""
Test script to verify smaller collision fields allow closer vehicle spacing.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from traffic_sim.core.testapp import App
from traffic_sim.services.physics import check_collisions
from traffic_sim.configuration import Config

def test_smaller_collision_field():
    """Test that vehicles can now get closer with reduced collision fields."""
    print("Testing smaller collision field...")
    print("=" * 50)
    
    config = Config()
    print(f"Current settings:")
    print(f"  Min following distance: {config.VEHICLE_SPACING['MIN_FOLLOWING_DISTANCE']}px")
    print(f"  Emergency stop distance: {config.VEHICLE_SPACING['EMERGENCY_STOP_DISTANCE']}px")
    print(f"  Following distance multiplier: {config.VEHICLE_SPACING['FOLLOWING_DISTANCE_MULTIPLIER']}x")
    print()
    
    # Create app instance
    app = App()
    
    # Run simulation for a brief time to see spacing
    test_duration = 20.0  # 20 seconds
    frame_count = 0
    collision_count = 0
    start_time = time.time()
    min_distance_seen = float('inf')
    max_agents = 0
    
    try:
        while time.time() - start_time < test_duration:
            dt = 1/60.0  # 60 FPS
            
            # Update traffic controller
            app.ctrl.update(dt)
            
            # Spawn new agents more frequently for closer spacing test
            if frame_count % 60 == 0:  # Every 1 second
                for spawner in [app.car_ns_spawner, app.car_ew_spawner, app.truck_ew_spawner]:
                    new_agent = spawner.update(dt, allow_spawn=True)
                    if new_agent and len(app.agents) < 20:  # Allow more agents
                        if app._add_agent(new_agent):
                            print(f"Spawned {type(new_agent).__name__} at {new_agent.pos}")
            
            # Update all agents
            for agent in list(app.agents):
                agent.update(dt)
                if getattr(agent, 'done', False):
                    app.agents.remove(agent)
            
            # Track maximum number of agents
            max_agents = max(max_agents, len(app.agents))
            
            # Check minimum distances between vehicles
            if len(app.agents) >= 2:
                for i in range(len(app.agents)):
                    for j in range(i + 1, len(app.agents)):
                        agent1 = app.agents[i]
                        agent2 = app.agents[j]
                        if not (getattr(agent1, 'done', False) or getattr(agent2, 'done', False)):
                            dist = ((agent1.pos[0] - agent2.pos[0])**2 + 
                                   (agent1.pos[1] - agent2.pos[1])**2)**0.5
                            min_distance_seen = min(min_distance_seen, dist)
            
            # Check for collisions
            collisions = check_collisions(app.agents, min_dist=5.0)
            if collisions:
                collision_count += 1
                app._separate_colliding_vehicles()
            
            frame_count += 1
            
            # Print status every 5 seconds
            if frame_count % 300 == 0:
                elapsed = time.time() - start_time
                print(f"Time: {elapsed:.1f}s, Agents: {len(app.agents)}, Min Distance: {min_distance_seen:.1f}px")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    # Final report
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("SMALLER COLLISION FIELD TEST RESULTS")
    print("=" * 50)
    print(f"Test duration: {elapsed:.1f} seconds")
    print(f"Maximum agents simultaneously: {max_agents}")
    print(f"Minimum distance between vehicles: {min_distance_seen:.1f} pixels")
    print(f"Total collisions detected: {collision_count}")
    
    # Assessment
    if min_distance_seen < 50:
        print("✅ SUCCESS: Vehicles can now get much closer!")
    elif min_distance_seen < 70:
        print("✅ GOOD: Vehicles are closer than before")
    else:
        print("⚠️  NOTICE: Vehicles are still maintaining large distances")
    
    if collision_count == 0:
        print("✅ No collisions occurred with smaller spacing")
    else:
        print(f"⚠️  {collision_count} collisions handled by emergency separation")
    
    print(f"\nConfiguration comparison:")
    print(f"  OLD: Following distance ~160px, Emergency stop ~100px")
    print(f"  NEW: Following distance ~{config.VEHICLE_SPACING['MIN_FOLLOWING_DISTANCE']:.0f}px, Emergency stop ~{config.VEHICLE_SPACING['EMERGENCY_STOP_DISTANCE']:.0f}px")
    
    return min_distance_seen < 60  # Success if vehicles get within 60px

if __name__ == "__main__":
    success = test_smaller_collision_field()
    sys.exit(0 if success else 1)