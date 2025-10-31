#!/usr/bin/env python3

"""
Test script to debug EW bike spawning issues.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ew_bike_spawning():
    """Test EW bike spawning simulation."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.actors.cyclist import Cyclist
        from traffic_sim.services.pathing import BIKES_EW_RIGHT, to_pixels
        
        print("🚴 Testing EW bike spawning process...")
        print()
        
        # Create app instance
        app = App()
        
        # Test 1: Create EW cyclist directly
        print("📍 Test 1: Direct EW cyclist creation")
        bikes_ew_right_px = to_pixels(BIKES_EW_RIGHT, 1280, 720)
        cyclist_ew = Cyclist(
            bikes_ew_right_px, 
            speed_px_s=90, 
            can_cross_ok=app.ctrl.can_ped_cross_ew
        )
        print(f"   ✅ EW cyclist created")
        print(f"     Position: {cyclist_ew.pos}")
        print(f"     Path: {cyclist_ew.path}")
        
        # Test 2: Check spawn safety
        print()
        print("📍 Test 2: Spawn safety check")
        safe = app._is_safe_spawn_position(cyclist_ew)
        print(f"   Spawn safe: {'✅ YES' if safe else '❌ NO'}")
        
        # Test 3: Test spawner factory
        print()
        print("📍 Test 3: EW Bike spawner factory")
        try:
            new_cyclist = app.bike_ew_spawner.factory()
            print(f"   ✅ Spawner factory works")
            print(f"     Position: {new_cyclist.pos}")
            print(f"     Path start: {new_cyclist.path[0] if new_cyclist.path else 'No path'}")
        except Exception as e:
            print(f"   ❌ Spawner factory failed: {e}")
        
        # Test 4: Test spawner update
        print()
        print("📍 Test 4: Spawner update process")
        initial_agent_count = len(app.agents)
        print(f"   Initial agent count: {initial_agent_count}")
        
        # Allow spawning
        allow_spawn = lambda: len(app.agents) < 30
        
        # Try to spawn
        new_agent = app.bike_ew_spawner.update(1.0, allow_spawn=allow_spawn)
        if new_agent:
            print(f"   ✅ Spawner created agent: {type(new_agent).__name__}")
            print(f"     Position: {new_agent.pos}")
            
            # Try to add agent
            added = app._add_agent(new_agent)
            print(f"   Agent added: {'✅ YES' if added else '❌ NO'}")
            if added:
                print(f"     New agent count: {len(app.agents)}")
        else:
            print(f"   ❌ Spawner did not create agent")
        
        # Test 5: Traffic light status
        print()
        print("📍 Test 5: Traffic light status for EW pedestrians/cyclists")
        can_cross = app.ctrl.can_ped_cross_ew()
        print(f"   Can EW cyclists cross: {'✅ YES' if can_cross else '❌ NO'}")
        print(f"   EW ped light state: {app.ctrl.ped_ew.state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging EW bike spawning...")
    print("=" * 70)
    
    success = test_ew_bike_spawning()
    
    print()
    print("=" * 70)
    if success:
        print("✅ EW bike spawning test completed!")
    else:
        print("❌ EW bike spawning test failed.")