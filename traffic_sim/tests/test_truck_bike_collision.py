#!/usr/bin/env python3

"""
Test script to analyze truck-bike collision issues.
"""

import sys
from pathlib import Path
import math

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_truck_bike_collisions():
    """Analyze truck-bike collision behavior."""
    try:
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.domain.actors.cyclist import Cyclist
        from traffic_sim.services.pathing import CARS_NS_UP, BIKES_NS_UP, to_pixels
        from traffic_sim.services.physics import (
            get_rotated_collision_points, 
            rotated_rectangles_collide,
            get_collision_rect
        )
        from traffic_sim.configuration import Config
        
        config = Config()
        print("🔍 Analyzing truck-bike collision behavior...")
        print()
        
        # Screen size
        screen_size = (1280, 720)
        
        # Create paths
        truck_path = to_pixels(CARS_NS_UP, *screen_size)
        bike_path = to_pixels(BIKES_NS_UP, *screen_size)
        
        print("📍 Vehicle Collision Dimensions:")
        
        # Check collision radii
        truck_radius = config.COLLISION_RADIUS.get("TRUCK", 25)
        bike_radius = config.COLLISION_RADIUS.get("CYCLIST", 25)
        
        print(f"   Truck collision radius: {truck_radius}px")
        print(f"   Bike collision radius: {bike_radius}px")
        
        # Create vehicles at same position to test hitbox dimensions
        truck = Truck(truck_path)
        bike = Cyclist(bike_path)
        
        # Set same position for comparison
        test_pos = [400, 300]
        truck.pos = test_pos[:]
        bike.pos = test_pos[:]
        
        # Get collision rectangles
        truck_rect = get_collision_rect(truck)
        bike_rect = get_collision_rect(bike)
        
        print()
        print(f"📏 Collision Rectangle Dimensions:")
        print(f"   Truck: {truck_rect.width:.1f}w × {truck_rect.height:.1f}h")
        print(f"   Bike:  {bike_rect.width:.1f}w × {bike_rect.height:.1f}h")
        
        # Get rotated collision points
        truck_points = get_rotated_collision_points(truck)
        bike_points = get_rotated_collision_points(bike)
        
        print()
        print(f"📐 Rotated Collision Points:")
        print(f"   Truck corners: {truck_points}")
        print(f"   Bike corners: {bike_points}")
        
        # Test collision at same position
        same_pos_collision = rotated_rectangles_collide(truck, bike)
        print(f"   Same position collision: {same_pos_collision}")
        
        print()
        print("🚛🚴 Testing Different Scenarios:")
        
        # Scenario 1: Truck and bike side by side
        truck.pos = [400, 300]
        bike.pos = [450, 300]  # 50px to the right
        
        collision_1 = rotated_rectangles_collide(truck, bike)
        distance_1 = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"   Scenario 1 - Side by side (50px apart):")
        print(f"     Collision: {collision_1}")
        print(f"     Distance: {distance_1:.1f}px")
        
        # Scenario 2: Truck behind bike
        truck.pos = [400, 350]  # 50px behind
        bike.pos = [400, 300]
        
        collision_2 = rotated_rectangles_collide(truck, bike)
        distance_2 = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"   Scenario 2 - Truck behind bike (50px apart):")
        print(f"     Collision: {collision_2}")
        print(f"     Distance: {distance_2:.1f}px")
        
        # Scenario 3: Overlapping paths (realistic scenario)
        truck.pos = [400, 300]
        bike.pos = [410, 300]  # 10px to the right (close but different lanes)
        
        collision_3 = rotated_rectangles_collide(truck, bike)
        distance_3 = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"   Scenario 3 - Close lanes (10px apart):")
        print(f"     Collision: {collision_3}")
        print(f"     Distance: {distance_3:.1f}px")
        
        # Check if truck width is reasonable
        truck_width = truck_radius * 1.0  # Current multiplier from physics.py
        print()
        print(f"✅ Truck Width Analysis:")
        print(f"   Radius: {truck_radius}px")
        print(f"   Width multiplier: 1.0")
        print(f"   Actual width: {truck_width:.1f}px")
        print(f"   Height: {truck_radius * 3.8:.1f}px")
        
        if truck_width < 10:
            print(f"   🚨 WARNING: Truck width ({truck_width:.1f}px) is too narrow!")
            print(f"      This could cause collision detection issues.")
        else:
            print(f"   ✅ Truck dimensions look reasonable for collision detection.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Analyzing truck-bike collision issues...")
    print("=" * 70)
    
    success = test_truck_bike_collisions()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Truck-bike collision analysis completed!")
    else:
        print("❌ Truck-bike collision analysis failed.")