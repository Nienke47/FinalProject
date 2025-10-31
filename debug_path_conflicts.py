#!/usr/bin/env python3

"""
Debug path conflict detection logic.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_path_conflict_logic():
    """Test path conflict detection in detail."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.domain.actors.cyclist import Cyclist
        
        print("🔍 Debugging path conflict detection...")
        print()
        
        # Create app to get proper setup
        app = App()
        
        # Create vehicles
        truck = app.truck_ns_spawner.factory()
        bike = app.bike_ns_spawner.factory()
        
        print("📍 Original Paths:")
        print(f"   Truck path: {truck.path[:3]}...")  # First 3 points
        print(f"   Bike path: {bike.path[:3]}...")    # First 3 points
        
        # Test 1: Original paths (should be parallel)
        print()
        print("🧪 Test 1 - Original paths:")
        conflict_original = truck._are_paths_conflicting(bike)
        lane_sep = abs(truck.path[0][0] - bike.path[0][0])
        print(f"   Lane separation: {lane_sep:.1f}px")
        print(f"   Paths conflict: {'YES' if conflict_original else 'NO'}")
        
        # Test 2: Same starting X (same lane)
        print()
        print("🧪 Test 2 - Same lane (modified bike path):")
        
        # Modify bike to use truck's lane
        bike.path = [(truck.path[0][0], truck.path[0][1] - 60)] + truck.path[1:]
        conflict_same = truck._are_paths_conflicting(bike)
        lane_sep_same = abs(truck.path[0][0] - bike.path[0][0])
        
        print(f"   Modified bike path start: {bike.path[0]}")
        print(f"   Lane separation: {lane_sep_same:.1f}px")
        print(f"   Paths conflict: {'YES' if conflict_same else 'NO'}")
        
        # Test 3: Detailed conflict analysis
        print()
        print("🔬 Detailed Conflict Analysis:")
        
        # Restore original bike path for analysis
        bike = app.bike_ns_spawner.factory()
        
        print(f"   Truck start: {truck.path[0]}")
        print(f"   Bike start: {bike.path[0]}")
        
        my_start = truck.path[0]
        other_start = bike.path[0]
        lane_separation = abs(my_start[0] - other_start[0])
        
        print(f"   Horizontal separation: {lane_separation:.1f}px")
        print(f"   Threshold (45px): {'PASSED' if lane_separation > 45 else 'FAILED'}")
        
        if lane_separation > 45:
            if len(truck.path) > 1 and len(bike.path) > 1:
                truck_direction = (truck.path[1][1] - truck.path[0][1])
                bike_direction = (bike.path[1][1] - bike.path[0][1])
                
                print(f"   Truck Y direction: {truck_direction:.1f} ({'DOWN' if truck_direction > 0 else 'UP'})")
                print(f"   Bike Y direction: {bike_direction:.1f} ({'DOWN' if bike_direction > 0 else 'UP'})")
                
                same_direction = (truck_direction > 0 and bike_direction > 0) or (truck_direction < 0 and bike_direction < 0)
                print(f"   Same direction: {'YES' if same_direction else 'NO'}")
                print(f"   Result: {'PARALLEL' if same_direction else 'CONFLICTING'}")
        
        # Test 4: Collision check with modified distance
        print()
        print("🚛🚴 Manual Collision Test:")
        
        # Reset positions
        truck.pos = list(truck.path[0])
        bike.pos = list(bike.path[0])
        
        # Set up agents
        truck.all_agents = [truck, bike]
        bike.all_agents = [truck, bike]
        
        # Test current implementation
        print(f"   Current positions:")
        print(f"     Truck: {truck.pos}")
        print(f"     Bike: {bike.pos}")
        
        # Calculate distance
        import math
        distance = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        print(f"     Distance: {distance:.1f}px")
        
        # Test with different safe distances
        for safe_dist in [25, 50, 88]:
            collision = truck._check_collision_ahead(truck.pos, safe_distance=safe_dist)
            print(f"   Safe distance {safe_dist}px: {'🚨 COLLISION' if collision else '✅ CLEAR'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging path conflict detection logic...")
    print("=" * 80)
    
    success = test_path_conflict_logic()
    
    print()
    print("=" * 80)
    if success:
        print("✅ Path conflict debugging completed!")
    else:
        print("❌ Path conflict debugging failed!")