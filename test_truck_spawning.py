#!/usr/bin/env python3

"""
Test script to verify truck spawning works with the adjusted safety system.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_truck_spawning():
    """Test truck spawning with adjusted safety system."""
    try:
        from traffic_sim.domain.actors.car import Car
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.core.testapp import App
        
        print("🚛 Testing truck spawning system...")
        
        # Create app instance
        app = App()
        
        # Test 1: Empty spawn area
        print()
        print("📍 Test 1: Empty spawn area")
        truck1 = Truck([(100, 100), (100, 200)])
        safe1 = app._is_safe_spawn_position(truck1)
        print(f"   Empty area truck spawn: {'✅ ALLOWED' if safe1 else '❌ BLOCKED'}")
        
        # Add first truck to test subsequent spawns
        if safe1:
            app.agents.append(truck1)
        
        # Test 2: Truck near existing truck (same path start)
        print()
        print("📍 Test 2: Truck near existing truck")
        truck2 = Truck([(100, 100), (100, 200)])  # Same starting position
        safe2 = app._is_safe_spawn_position(truck2)
        print(f"   Same position truck spawn: {'✅ ALLOWED' if safe2 else '❌ BLOCKED (expected)'}")
        
        # Test 3: Truck at reasonable distance
        print()
        print("📍 Test 3: Truck at reasonable distance")
        truck3 = Truck([(200, 100), (200, 200)])  # 100px away
        safe3 = app._is_safe_spawn_position(truck3)
        print(f"   100px away truck spawn: {'✅ ALLOWED' if safe3 else '❌ BLOCKED'}")
        
        # Test 4: Truck with existing car
        print()
        print("📍 Test 4: Truck with existing car")
        app.agents = [Car([(150, 150), (150, 250)])]  # Add a car
        truck4 = Truck([(100, 100), (100, 200)])  # Truck at different position
        safe4 = app._is_safe_spawn_position(truck4)
        print(f"   Truck with existing car: {'✅ ALLOWED' if safe4 else '❌ BLOCKED'}")
        
        # Test 5: Multiple spawn attempts
        print()
        print("📍 Test 5: Multiple spawn scenarios")
        spawn_success_count = 0
        test_paths = [
            [(50, 50), (50, 150)],      # Top-left
            [(150, 50), (150, 150)],    # Top-right  
            [(250, 50), (250, 150)],    # Far right
            [(350, 50), (350, 150)],    # Very far right
        ]
        
        app.agents = []  # Reset agents
        for i, path in enumerate(test_paths):
            truck = Truck(path)
            if app._is_safe_spawn_position(truck):
                app.agents.append(truck)  # Add to agents if successful
                spawn_success_count += 1
                print(f"   Spawn {i+1}: ✅ SUCCESS at {path[0]}")
            else:
                print(f"   Spawn {i+1}: ❌ BLOCKED at {path[0]}")
        
        print()
        print(f"🎯 Results summary:")
        print(f"   Empty area: {'✅' if safe1 else '❌'}")
        print(f"   Same position (should block): {'✅' if not safe2 else '❌'}")
        print(f"   Reasonable distance: {'✅' if safe3 else '❌'}")
        print(f"   With existing car: {'✅' if safe4 else '❌'}")
        print(f"   Multiple spawns successful: {spawn_success_count}/4")
        
        # Success if: empty works, same position blocked, reasonable distance works, car coexistence works
        success = safe1 and (not safe2) and safe3 and safe4 and spawn_success_count >= 3
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing truck spawning with adjusted safety system...")
    print("=" * 70)
    
    success = test_truck_spawning()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Truck spawning system working correctly!")
        print("Trucks should now spawn properly while maintaining safety.")
    else:
        print("❌ Truck spawning test failed.")
        print("The spawn safety system may need further adjustment.")