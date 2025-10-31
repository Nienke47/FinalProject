#!/usr/bin/env python3
"""
Test script to verify collision prevention system.
This script runs a quick simulation and reports any collisions detected.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from traffic_sim.core.testapp import App
from traffic_sim.services.physics import check_collisions

def test_collision_prevention():
    """Run a brief simulation to test collision prevention."""
    print("Testing collision prevention system...")
    print("=" * 50)
    
    # Create app instance
    app = App()
    
    # Run simulation for a limited time
    test_duration = 30.0  # 30 seconds
    frame_count = 0
    collision_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < test_duration:
            # Simulate one frame
            dt = 1/60.0  # 60 FPS
            
            # Update traffic controller
            app.ctrl.update(dt)
            
            # Spawn new agents (simplified spawning)
            if frame_count % 120 == 0:  # Every 2 seconds
                for spawner in [app.car_ns_spawner, app.car_ew_spawner]:
                    new_agent = spawner.update(dt, allow_spawn=True)
                    if new_agent and len(app.agents) < 15:  # Limit agents for test
                        if app._add_agent(new_agent):
                            print(f"Spawned {type(new_agent).__name__} at {new_agent.pos}")
            
            # Update all agents
            for agent in list(app.agents):
                agent.update(dt)
                if getattr(agent, 'done', False):
                    print(f"Agent completed journey: {type(agent).__name__}")
                    app.agents.remove(agent)
            
            # Check for collisions
            collisions = check_collisions(app.agents, min_dist=10.0)
            if collisions:
                collision_count += 1
                print(f"COLLISION DETECTED at frame {frame_count}!")
                
                # Force separation if collision detected
                app._separate_colliding_vehicles()
            
            frame_count += 1
            
            # Print status every 5 seconds
            if frame_count % 300 == 0:
                elapsed = time.time() - start_time
                print(f"Time: {elapsed:.1f}s, Agents: {len(app.agents)}, Collisions: {collision_count}")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    # Final report
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("COLLISION PREVENTION TEST RESULTS")
    print("=" * 50)
    print(f"Test duration: {elapsed:.1f} seconds")
    print(f"Total frames: {frame_count}")
    print(f"Total collisions detected: {collision_count}")
    print(f"Final agent count: {len(app.agents)}")
    
    if collision_count == 0:
        print("✅ SUCCESS: No collisions detected!")
    else:
        print(f"⚠️  WARNING: {collision_count} collisions were detected and corrected")
    
    print("\nAgent positions at test end:")
    for i, agent in enumerate(app.agents):
        print(f"  Agent {i}: {type(agent).__name__} at ({agent.pos[0]:.1f}, {agent.pos[1]:.1f})")
    
    return collision_count == 0

if __name__ == "__main__":
    success = test_collision_prevention()
    sys.exit(0 if success else 1)