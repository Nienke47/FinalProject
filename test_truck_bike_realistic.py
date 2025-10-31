#!/usr/bin/env python3

"""
Test script to verify truck-bike collision behavior is working properly.
"""

import sys
from pathlib import Path
import math

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_realistic_scenarios():
    """Test truck-bike behavior in realistic traffic scenarios."""
    try:
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.domain.actors.cyclist import Cyclist
        from traffic_sim.services.pathing import CARS_NS_UP, BIKES_NS_UP, to_pixels
        from traffic_sim.services.physics import rotated_rectangles_collide
        
        print("🚛🚴 Testing realistic truck-bike scenarios...")
        print()
        
        # Screen size
        screen_size = (1280, 720)
        
        # Create paths
        truck_path = to_pixels(CARS_NS_UP, *screen_size)
        bike_path = to_pixels(BIKES_NS_UP, *screen_size)
        
        print("📍 Path Information:")
        print(f"   Truck path start: {truck_path[0]}")
        print(f"   Bike path start: {bike_path[0]}")
        
        # Calculate lane separation
        lane_separation = abs(truck_path[0][0] - bike_path[0][0])
        print(f"   Lane separation: {lane_separation:.1f}px")
        
        print()
        print("🧪 Scenario Testing:")
        
        # Scenario 1: Normal lane separation
        print("   1. Normal traffic - vehicles in their own lanes:")
        truck = Truck(truck_path)
        bike = Cyclist(bike_path)
        
        # Position them at the same Y but in their lanes
        truck.pos = list(truck_path[0])
        bike.pos = list(bike_path[0])
        
        collision_normal = rotated_rectangles_collide(truck, bike)
        distance_normal = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"      Collision: {'❌ YES (Problem!)' if collision_normal else '✅ NO (Good)'}")
        print(f"      Distance: {distance_normal:.1f}px")
        
        # Scenario 2: Truck slightly drifting toward bike lane
        print("   2. Truck drifting toward bike lane:")
        truck.pos = [truck_path[0][0] - 15, truck_path[0][1]]  # Move truck 15px toward bike
        bike.pos = list(bike_path[0])
        
        collision_drift = rotated_rectangles_collide(truck, bike)
        distance_drift = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"      Collision: {'⚠️ YES' if collision_drift else '✅ NO'}")
        print(f"      Distance: {distance_drift:.1f}px")
        
        # Scenario 3: Bike slightly in truck lane
        print("   3. Bike slightly in truck lane:")
        truck.pos = list(truck_path[0])
        bike.pos = [bike_path[0][0] - 20, bike_path[0][1]]  # Move bike 20px toward truck
        
        collision_bike_drift = rotated_rectangles_collide(truck, bike)
        distance_bike_drift = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"      Collision: {'⚠️ YES' if collision_bike_drift else '✅ NO'}")
        print(f"      Distance: {distance_bike_drift:.1f}px")
        
        # Scenario 4: Following scenario (truck behind bike)
        print("   4. Truck following behind bike in same lane:")
        truck.pos = [bike_path[0][0], bike_path[0][1] + 80]  # Truck 80px behind bike
        bike.pos = list(bike_path[0])
        
        collision_following = rotated_rectangles_collide(truck, bike)
        distance_following = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"      Collision: {'❌ YES (Too close!)' if collision_following else '✅ NO (Safe distance)'}")
        print(f"      Distance: {distance_following:.1f}px")
        
        # Scenario 5: Very close following
        print("   5. Truck very close behind bike:")
        truck.pos = [bike_path[0][0], bike_path[0][1] + 40]  # Truck 40px behind bike
        bike.pos = list(bike_path[0])
        
        collision_close = rotated_rectangles_collide(truck, bike)
        distance_close = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print(f"      Collision: {'🚨 YES (Collision!)' if collision_close else '✅ NO'}")
        print(f"      Distance: {distance_close:.1f}px")
        
        print()
        print("📊 Summary:")
        scenarios = [
            ("Normal lanes", collision_normal, distance_normal),
            ("Truck drift", collision_drift, distance_drift),
            ("Bike drift", collision_bike_drift, distance_bike_drift),
            ("Following 80px", collision_following, distance_following),
            ("Following 40px", collision_close, distance_close)
        ]
        
        safe_scenarios = sum(1 for _, collision, _ in scenarios if not collision)
        print(f"   Safe scenarios: {safe_scenarios}/{len(scenarios)}")
        print(f"   Lane separation: {lane_separation:.1f}px")
        
        # Check if normal lane operation is safe
        if not collision_normal:
            print("   ✅ Normal lane operation is SAFE")
        else:
            print("   🚨 Normal lane operation has COLLISION ISSUE!")
            
        return not collision_normal  # Return True if normal lanes are safe
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing truck-bike collision behavior...")
    print("=" * 70)
    
    success = test_realistic_scenarios()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Truck-bike collision behavior is working correctly!")
        print("   Trucks and bikes can coexist safely in separate lanes.")
    else:
        print("❌ Truck-bike collision behavior needs adjustment!")
        print("   There are still collision issues in normal traffic.")