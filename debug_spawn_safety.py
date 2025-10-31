#!/usr/bin/env python3

"""
Debug spawn safety to see what distances are being calculated.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_spawn_safety():
    """Debug spawn safety calculations."""
    try:
        from traffic_sim.domain.actors.car import Car
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.core.testapp import App
        from traffic_sim.services.physics import get_rotated_collision_points, rotated_rectangles_collide
        import math
        
        print("🔍 Debugging spawn safety calculations...")
        
        # Create test vehicles
        path1 = [(100, 100), (100, 200)]
        path2 = [(100, 100), (100, 200)]  # Same starting point
        path3 = [(150, 100), (150, 200)]  # Different starting point (50px away)
        
        car1 = Car(path1)
        truck = Truck(path2)  # Same position as car1
        car2 = Car(path3)     # Different position
        
        print("📍 Vehicle positions:")
        print(f"   Car1: {car1.pos}")
        print(f"   Truck: {truck.pos}")
        print(f"   Car2: {car2.pos}")
        
        # Test collision detection
        print()
        print("🔄 Collision detection:")
        collision1 = rotated_rectangles_collide(car1, truck)
        collision2 = rotated_rectangles_collide(car1, car2)
        print(f"   Car1 vs Truck: {'COLLISION' if collision1 else 'NO COLLISION'}")
        print(f"   Car1 vs Car2: {'COLLISION' if collision2 else 'NO COLLISION'}")
        
        # Test distance calculations
        print()
        print("📏 Distance calculations:")
        
        # Get collision points
        car1_points = get_rotated_collision_points(car1)
        car2_points = get_rotated_collision_points(car2)
        truck_points = get_rotated_collision_points(truck)
        
        # Calculate minimum distances between rectangles
        def min_rect_distance(points1, points2):
            min_dist = float('inf')
            for p1 in points1:
                for p2 in points2:
                    dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                    min_dist = min(min_dist, dist)
            return min_dist
        
        dist_car1_truck = min_rect_distance(car1_points, truck_points)
        dist_car1_car2 = min_rect_distance(car1_points, car2_points)
        
        print(f"   Car1-Truck min distance: {dist_car1_truck:.1f}px")
        print(f"   Car1-Car2 min distance: {dist_car1_car2:.1f}px")
        
        # Test with different safety buffers
        print()
        print("🛡️ Safety buffer tests:")
        for buffer in [5, 10, 15, 20, 25]:
            safe_truck = (not collision1) and (dist_car1_truck >= buffer)
            safe_car2 = (not collision2) and (dist_car1_car2 >= buffer)
            print(f"   Buffer {buffer}px: Truck={'✅' if safe_truck else '❌'}, Car2={'✅' if safe_car2 else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging spawn safety system...")
    print("=" * 60)
    
    debug_spawn_safety()
    
    print()
    print("=" * 60)
    print("Analysis complete. Use this info to adjust safety buffer.")