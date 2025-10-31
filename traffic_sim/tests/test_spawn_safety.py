#!/usr/bin/env python3

"""
Test script to verify spawn safety with collision hitboxes.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_spawn_safety():
    """Test spawn safety with collision rectangles."""
    try:
        from traffic_sim.domain.actors.car import Car
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.core.testapp import App
        from traffic_sim.services.physics import get_rotated_collision_points
        
        print("🔍 Testing spawn safety system...")
        
        # Create test vehicles on the same path
        path1 = [(100, 100), (100, 200)]
        path2 = [(100, 100), (100, 200)]  # Same starting point
        path3 = [(150, 100), (150, 200)]  # Different starting point
        
        car1 = Car(path1)
        truck = Truck(path2)  # Same position as car1
        car2 = Car(path3)     # Different position
        
        # Create app instance to test spawn safety
        app = App()
        app.agents = [car1]  # Add first car to agents list
        
        print("📍 Testing spawn positions:")
        print(f"   Car1 at: {car1.pos}")
        print(f"   Truck at: {truck.pos} (same as car1)")
        print(f"   Car2 at: {car2.pos} (different position)")
        
        print()
        print("🛡️ Spawn safety checks:")
        
        # Test 1: Try to spawn truck at same position as existing car
        safe1 = app._is_safe_spawn_position(truck)
        print(f"   Truck at same position as car1: {'❌ BLOCKED' if not safe1 else '✅ ALLOWED'}")
        
        # Test 2: Try to spawn car2 at different position
        safe2 = app._is_safe_spawn_position(car2)
        print(f"   Car2 at different position: {'❌ BLOCKED' if not safe2 else '✅ ALLOWED'}")
        
        # Test 3: Show collision rectangles for context
        car1_points = get_rotated_collision_points(car1)
        truck_points = get_rotated_collision_points(truck)
        
        print()
        print("📏 Collision rectangle info:")
        car1_width = abs(car1_points[1][0] - car1_points[0][0])
        car1_height = abs(car1_points[2][1] - car1_points[1][1])
        truck_width = abs(truck_points[1][0] - truck_points[0][0])
        truck_height = abs(truck_points[2][1] - truck_points[1][1])
        
        print(f"   Car1 rectangle: {car1_width:.1f}px × {car1_height:.1f}px")
        print(f"   Truck rectangle: {truck_width:.1f}px × {truck_height:.1f}px")
        
        print()
        print("🎯 Expected behavior:")
        print("   - Truck should be BLOCKED (overlaps with car1)")
        print("   - Car2 should be ALLOWED (far enough away)")
        
        return safe1 == False and safe2 == True  # We expect truck blocked, car2 allowed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing spawn safety with collision hitboxes...")
    print("=" * 60)
    
    success = test_spawn_safety()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Spawn safety system working correctly!")
        print("Vehicles will now wait for hitboxes to be fully clear before spawning.")
    else:
        print("❌ Spawn safety test failed. Check the results above.")
        print("The spawn safety system may need adjustment.")