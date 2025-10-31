#!/usr/bin/env python3
"""
Debug spawner timing to understand why EW bikes don't spawn.
"""

import sys
import os

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

from services.spawner import Spawner
from domain.actors.cyclist import Cyclist
import random

def test_spawner_timing():
    """Test spawner timing logic with detailed logging."""
    
    print("🔍 Testing spawner timing logic...")
    print("=" * 80)
    
    # Create a simple test spawner similar to EW bikes
    def test_factory():
        return Cyclist([[0, 0], [100, 0]], speed_px_s=90)
    
    spawner = Spawner(
        factory=test_factory,
        interval_s=4.0,
        random_offset=1.0,
        max_count=5
    )
    
    print(f"📊 Spawner Configuration:")
    print(f"   interval: {spawner.interval}")
    print(f"   random_offset: {spawner.random_offset}")
    print(f"   max_count: {spawner.max_count}")
    print(f"   _acc: {spawner._acc}")
    print(f"   _spawned: {spawner._spawned}")
    print()
    
    print("⏱️ Timing Logic Analysis:")
    print(f"   Condition: _acc + random_offset >= interval")
    print(f"   Required: _acc + {spawner.random_offset} >= {spawner.interval}")
    print(f"   Simplified: _acc >= {spawner.interval - spawner.random_offset}")
    print()
    
    # Simulate time steps
    dt = 1.0  # 1 second time steps
    total_time = 0.0
    spawned_count = 0
    
    print("🕐 Simulating time steps:")
    for step in range(10):
        total_time += dt
        
        print(f"   Step {step+1}: t={total_time:.1f}s, _acc={spawner._acc:.2f}")
        print(f"      Check: {spawner._acc:.2f} + {spawner.random_offset} >= {spawner.interval} -> {spawner._acc + spawner.random_offset >= spawner.interval}")
        
        result = spawner.update(dt, allow_spawn=True)
        
        if result is not None:
            spawned_count += 1
            print(f"      ✅ SPAWNED! (Total: {spawned_count})")
        else:
            print(f"      ❌ No spawn")
        
        print(f"      New _acc: {spawner._acc:.2f}")
        print()
    
    print(f"📈 Final Results:")
    print(f"   Total time simulated: {total_time}s")
    print(f"   Total spawned: {spawned_count}")
    print(f"   Spawner internal count: {spawner._spawned}")
    
    # Test with smaller time steps (more realistic)
    print("\n🔬 Testing with smaller time steps (60 FPS):")
    spawner2 = Spawner(
        factory=test_factory,
        interval_s=4.0,
        random_offset=1.0,
        max_count=5
    )
    
    dt_small = 1/60  # 60 FPS
    total_time = 0.0
    spawned_count = 0
    
    for frame in range(300):  # 5 seconds at 60 FPS
        total_time += dt_small
        
        result = spawner2.update(dt_small, allow_spawn=True)
        
        if result is not None:
            spawned_count += 1
            print(f"   Frame {frame+1}: t={total_time:.2f}s - ✅ SPAWNED! (Total: {spawned_count})")
            
        # Print status every second
        if frame % 60 == 59:
            print(f"   t={total_time:.1f}s: _acc={spawner2._acc:.3f}, spawned={spawned_count}")
    
    print(f"\n📈 Small timestep results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Total spawned: {spawned_count}")
    print(f"   Expected spawns: ~{total_time / 4.0:.1f} (every 4s)")

if __name__ == "__main__":
    test_spawner_timing()