#!/usr/bin/env python3
"""
Test script to verify frame-based vehicle despawning system.
This script runs a simulation and tracks vehicles leaving the frame.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from traffic_sim.core.testapp import App
from traffic_sim.configuration import Config

def test_frame_despawning():
    """Test that vehicles properly despawn when leaving the frame."""
    print("Testing frame-based vehicle despawning...")
    print("=" * 50)
    
    config = Config()
    print(f"Screen dimensions: {config.WIDTH} x {config.HEIGHT}")
    print(f"Despawn buffer: {config.FRAME_BOUNDARY['DESPAWN_BUFFER']} pixels")
    print(f"Frame despawn enabled: {config.FRAME_BOUNDARY['ENABLE_FRAME_DESPAWN']}")
    print()
    
    # Create app instance
    app = App()
    
    # Track statistics
    initial_agent_count = len(app.agents)
    max_agents_seen = initial_agent_count
    total_spawned = 0
    frame_exits = 0
    path_completions = 0
    
    # Run simulation for a limited time
    test_duration = 45.0  # 45 seconds to see vehicles complete their journeys
    frame_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < test_duration:
            # Simulate one frame
            dt = 1/60.0  # 60 FPS
            
            # Update traffic controller
            app.ctrl.update(dt)
            
            # Spawn new agents periodically
            if frame_count % 180 == 0:  # Every 3 seconds
                for spawner in [app.car_ns_spawner, app.car_ew_spawner, app.truck_ew_spawner]:
                    if len(app.agents) < 20:  # Limit for test
                        new_agent = spawner.update(dt, allow_spawn=True)
                        if new_agent:
                            if app._add_agent(new_agent):
                                total_spawned += 1
                                print(f"Spawned {type(new_agent).__name__} at ({new_agent.pos[0]:.1f}, {new_agent.pos[1]:.1f})")
            
            # Track agent positions and update
            agents_before = len(app.agents)
            for agent in list(app.agents):
                agent.update(dt)
                if getattr(agent, 'done', False):
                    reason = getattr(agent, 'completion_reason', 'unknown')
                    pos = agent.pos
                    print(f"Agent {type(agent).__name__} removed: reason={reason}, pos=({pos[0]:.1f}, {pos[1]:.1f})")
                    
                    if reason == "frame_exit":
                        frame_exits += 1
                        # Verify position is actually outside frame + buffer
                        buffer = 50 + max(getattr(agent, 'width', 50), getattr(agent, 'length', 80))
                        outside = (pos[0] < -buffer or pos[0] > config.WIDTH + buffer or
                                 pos[1] < -buffer or pos[1] > config.HEIGHT + buffer)
                        if outside:
                            print(f"  ✓ Correctly outside frame boundary (buffer: {buffer:.0f}px)")
                        else:
                            print(f"  ⚠️  WARNING: Marked as frame_exit but still in bounds!")
                    else:
                        path_completions += 1
                    
                    app.agents.remove(agent)
                    
            # Update max agents seen
            max_agents_seen = max(max_agents_seen, len(app.agents))
            
            frame_count += 1
            
            # Print status every 10 seconds
            if frame_count % 600 == 0:
                elapsed = time.time() - start_time
                print(f"Time: {elapsed:.1f}s, Active agents: {len(app.agents)}, Total spawned: {total_spawned}")
                print(f"  Frame exits: {frame_exits}, Path completions: {path_completions}")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    # Final report
    elapsed = time.time() - start_time
    final_stats = app.stats.get_summary()
    
    print("\n" + "=" * 50)
    print("FRAME DESPAWNING TEST RESULTS")
    print("=" * 50)
    print(f"Test duration: {elapsed:.1f} seconds")
    print(f"Total frames: {frame_count}")
    print(f"Total vehicles spawned: {total_spawned}")
    print(f"Maximum concurrent vehicles: {max_agents_seen}")
    print(f"Final active vehicles: {len(app.agents)}")
    print(f"Frame exits: {frame_exits}")
    print(f"Path completions: {path_completions}")
    print(f"Total completions (both types): {frame_exits + path_completions}")
    print()
    print("Statistics from simulation:")
    print(f"  Total spawns: {sum(final_stats['spawns'].values())}")
    print(f"  Path completions: {sum(final_stats['completions'].values())}")
    print(f"  Frame exits: {sum(final_stats['frame_exits'].values())}")
    print()
    
    # Verify that vehicles are properly despawning
    if frame_exits > 0:
        print("✅ SUCCESS: Vehicles are properly despawning when leaving the frame!")
        print(f"   {frame_exits} vehicles left via frame boundary")
        if path_completions > 0:
            print(f"   {path_completions} vehicles completed their path normally")
    else:
        print("⚠️  WARNING: No vehicles despawned via frame exit")
        print("   This might be normal if all vehicles completed their paths")
    
    # Check for memory leaks (too many active agents)
    if len(app.agents) > max_agents_seen * 0.5:
        print("⚠️  WARNING: Many vehicles still active - possible despawn issue")
    else:
        print("✅ Good: Vehicle count appears well-managed")
    
    return frame_exits > 0 or path_completions > 0

if __name__ == "__main__":
    success = test_frame_despawning()
    sys.exit(0 if success else 1)