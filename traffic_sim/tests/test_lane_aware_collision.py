#!/usr/bin/env python3

"""
Test script to verify lane-aware collision detection fixes truck-bike issues.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_lane_aware_collision():
    """Test the new lane-aware collision detection."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.domain.actors.cyclist import Cyclist
        
        print("🔍 Testing lane-aware collision detection...")
        print()
        
        # Create app to get proper setup
        app = App()
        
        # Create vehicles using simulation paths
        truck = app.truck_ns_spawner.factory()
        bike = app.bike_ns_spawner.factory()
        
        # Set up agents list for collision detection
        truck.all_agents = [truck, bike]
        bike.all_agents = [truck, bike]
        
        print("📍 Vehicle Setup:")
        print(f"   Truck path start: {truck.path[0]}")
        print(f"   Bike path start: {bike.path[0]}")
        
        # Test path conflict detection
        print()
        print("🛣️ Path Conflict Analysis:")
        paths_conflict = truck._are_paths_conflicting(bike)
        print(f"   Paths conflicting: {'YES' if paths_conflict else 'NO'}")
        
        # Calculate lane separation
        lane_separation = abs(truck.path[0][0] - bike.path[0][0])
        print(f"   Lane separation: {lane_separation:.1f}px")
        
        # Test collision detection with vehicles in their lanes
        print()
        print("🚛🚴 Lane-Aware Collision Testing:")
        
        # Test 1: Vehicles in separate lanes (normal operation)
        truck.pos = list(truck.path[0])
        bike.pos = list(bike.path[0])
        
        # Test with truck's normal following distance (88px)
        truck_collision = truck._check_collision_ahead(truck.pos, safe_distance=88)
        bike_collision = bike._check_collision_ahead(bike.pos, safe_distance=55)
        
        print(f"   Test 1 - Normal lanes:")
        print(f"     Truck collision check (88px): {'🚨 BLOCKED' if truck_collision else '✅ FREE'}")
        print(f"     Bike collision check (55px): {'🚨 BLOCKED' if bike_collision else '✅ FREE'}")
        
        # Test 2: Same lane scenario
        print(f"   Test 2 - Same lane (bike in truck lane):")
        bike.pos = [truck.path[0][0], truck.path[0][1] - 60]  # Bike 60px ahead in truck lane
        
        truck_same_lane = truck._check_collision_ahead(truck.pos, safe_distance=88)
        bike_same_lane = bike._check_collision_ahead(bike.pos, safe_distance=55)
        
        print(f"     Truck collision check (88px): {'🚨 BLOCKED' if truck_same_lane else '✅ FREE'}")
        print(f"     Bike collision check (55px): {'🚨 BLOCKED' if bike_same_lane else '✅ FREE'}")
        
        # Test 3: Edge case - very close but different lanes
        print(f"   Test 3 - Close but different lanes:")
        truck.pos = list(truck.path[0])
        bike.pos = [bike.path[0][0], truck.path[0][1]]  # Same Y, different X (lanes)
        
        truck_close = truck._check_collision_ahead(truck.pos, safe_distance=88)
        bike_close = bike._check_collision_ahead(bike.pos, safe_distance=55)
        
        print(f"     Truck collision check (88px): {'🚨 BLOCKED' if truck_close else '✅ FREE'}")
        print(f"     Bike collision check (55px): {'🚨 BLOCKED' if bike_close else '✅ FREE'}")
        
        # Show effective distances used
        print()
        print("📊 Effective Safety Distances:")
        
        # Simulate the internal logic
        if not paths_conflict:
            effective_distance = 25  # Parallel lanes
        else:
            effective_distance = 88  # Same lane for truck
        
        print(f"   For parallel lanes: 25px (reduced from {lane_separation:.0f}px separation)")
        print(f"   For same lane: 88px (truck) / 55px (bike)")
        print(f"   Current effective distance: {effective_distance}px")
        
        # Summary
        print()
        print("🎯 Test Results Summary:")
        success_count = 0
        if not truck_collision and not bike_collision:
            print("   ✅ Normal lane operation: PASS")
            success_count += 1
        else:
            print("   ❌ Normal lane operation: FAIL")
            
        if truck_same_lane or bike_same_lane:
            print("   ✅ Same lane blocking: PASS")
            success_count += 1
        else:
            print("   ❌ Same lane blocking: FAIL")
            
        print(f"   Success rate: {success_count}/2")
        
        return success_count == 2
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing lane-aware collision detection fix...")
    print("=" * 80)
    
    success = test_lane_aware_collision()
    
    print()
    print("=" * 80)
    if success:
        print("✅ Lane-aware collision detection working correctly!")
        print("   Trucks and bikes should no longer interfere in separate lanes.")
    else:
        print("❌ Lane-aware collision detection needs more work.")
        print("   There are still issues with the collision system.")