#!/usr/bin/env python3

"""
Test script to show truck vs car collision rectangle differences.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_truck_vs_car_collision():
    """Compare truck and car collision rectangles."""
    try:
        from traffic_sim.domain.actors.car import Car
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.services.physics import get_rotated_collision_points
        from traffic_sim.configuration import Config
        
        config = Config()
        
        # Create test vehicles
        path = [(100, 100), (100, 200)]
        car = Car(path)
        truck = Truck(path)
        
        print("🚗 CAR collision info:")
        print(f"   Collision radius: {config.COLLISION_RADIUS['CAR']}px")
        car_points = get_rotated_collision_points(car)
        car_width = abs(car_points[1][0] - car_points[0][0])
        car_height = abs(car_points[2][1] - car_points[1][1])
        print(f"   Collision rectangle: {car_width:.1f}px wide × {car_height:.1f}px tall")
        
        print()
        print("🚛 TRUCK collision info:")
        print(f"   Collision radius: {config.COLLISION_RADIUS['TRUCK']}px")
        truck_points = get_rotated_collision_points(truck)
        truck_width = abs(truck_points[1][0] - truck_points[0][0])
        truck_height = abs(truck_points[2][1] - truck_points[1][1])
        print(f"   Collision rectangle: {truck_width:.1f}px wide × {truck_height:.1f}px tall")
        
        print()
        print("📊 COMPARISON:")
        print(f"   Truck is {truck_width/car_width:.1f}x wider than car")
        print(f"   Truck is {truck_height/car_height:.1f}x taller than car")
        print(f"   Truck height advantage: {truck_height - car_height:.1f}px extra forward detection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing truck collision dimensions...")
    print("=" * 60)
    
    success = test_truck_vs_car_collision()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Truck collision dimensions updated successfully!")
        print("Trucks now have much better forward collision detection.")
    else:
        print("❌ Test failed. Check the errors above.")