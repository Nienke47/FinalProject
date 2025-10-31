#!/usr/bin/env python3

"""
Test script to isolate the collision/car creation issue.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_car_creation():
    """Test creating a simple car to see if the parameter issue is fixed."""
    try:
        from traffic_sim.domain.actors.car import Car
        from traffic_sim.services.pathing import CARS_NS_UP, to_pixels
        
        # Simple path for testing
        path = [(100, 100), (100, 200), (200, 200)]
        
        print("Creating car with default parameters...")
        car = Car(path)
        print(f"✅ Car created successfully!")
        print(f"   Width: {car.width}, Length: {car.length}")
        
        print("Creating car with custom parameters...")
        car2 = Car(path, car_width=50, car_length=70)
        print(f"✅ Car with custom size created successfully!")
        print(f"   Width: {car2.width}, Length: {car2.length}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating car: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_collision_system():
    """Test the collision detection system."""
    try:
        from traffic_sim.services.physics import get_rotated_collision_points, rotated_rectangles_collide
        from traffic_sim.domain.actors.car import Car
        
        path1 = [(100, 100), (100, 200)]
        path2 = [(150, 100), (150, 200)]
        
        car1 = Car(path1)
        car2 = Car(path2)
        
        print("Testing collision detection...")
        
        # Test collision points
        points = get_rotated_collision_points(car1)
        print(f"✅ Collision points calculated: {len(points)} points")
        
        # Test collision detection
        collision = rotated_rectangles_collide(car1, car2)
        print(f"✅ Collision detection works: {collision}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in collision system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing collision system fixes...")
    print("=" * 50)
    
    car_ok = test_car_creation()
    print()
    collision_ok = test_collision_system()
    
    print()
    print("=" * 50)
    if car_ok and collision_ok:
        print("✅ All tests passed! The fixes should work.")
    else:
        print("❌ Some tests failed. Check the errors above.")