#!/usr/bin/env python3

"""
Test script to debug ongoing truck-bike collision issues during simulation.
"""

import sys
from pathlib import Path
import math

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_simulation_collisions():
    """Test truck-bike collisions during actual simulation."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.domain.actors.cyclist import Cyclist
        from traffic_sim.services.pathing import CARS_NS_UP, BIKES_NS_UP, to_pixels
        from traffic_sim.services.physics import rotated_rectangles_collide, get_rotated_collision_points
        
        print("🔍 Debugging truck-bike collisions in simulation...")
        print()
        
        # Create app to get proper setup
        app = App()
        screen_size = app.size
        
        # Get the actual paths used in simulation
        truck_path_px = app.cars_ns_up_px
        bike_path_px = app.bikes_ns_up_px
        
        print("📍 Simulation Path Information:")
        print(f"   Screen size: {screen_size}")
        print(f"   Truck path start: {truck_path_px[0]}")
        print(f"   Bike path start: {bike_path_px[0]}")
        
        # Calculate actual lane separation
        lane_separation = abs(truck_path_px[0][0] - bike_path_px[0][0])
        print(f"   Lane separation: {lane_separation:.1f}px")
        
        # Create vehicles using the same factory functions as the simulation
        print()
        print("🚛🚴 Creating vehicles with simulation factories:")
        
        truck = app.truck_ns_spawner.factory()
        bike = app.bike_ns_spawner.factory()
        
        print(f"   Truck created at: {truck.pos}")
        print(f"   Bike created at: {bike.pos}")
        print(f"   Truck path: {truck.path[:2]}...")  # First 2 points
        print(f"   Bike path: {bike.path[:2]}...")    # First 2 points
        
        # Test collision at spawn positions
        spawn_collision = rotated_rectangles_collide(truck, bike)
        spawn_distance = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
        
        print()
        print("🎯 Spawn Position Analysis:")
        print(f"   Collision at spawn: {'🚨 YES' if spawn_collision else '✅ NO'}")
        print(f"   Spawn distance: {spawn_distance:.1f}px")
        
        # Get collision rectangles
        truck_points = get_rotated_collision_points(truck)
        bike_points = get_rotated_collision_points(bike)
        
        print()
        print("📐 Collision Rectangle Analysis:")
        print("   Truck collision points:")
        for i, point in enumerate(truck_points):
            print(f"     {i+1}: ({point[0]:.1f}, {point[1]:.1f})")
        
        print("   Bike collision points:")
        for i, point in enumerate(bike_points):
            print(f"     {i+1}: ({point[0]:.1f}, {point[1]:.1f})")
        
        # Calculate rectangle dimensions
        truck_width = max(p[0] for p in truck_points) - min(p[0] for p in truck_points)
        truck_height = max(p[1] for p in truck_points) - min(p[1] for p in truck_points)
        bike_width = max(p[0] for p in bike_points) - min(p[0] for p in bike_points)
        bike_height = max(p[1] for p in bike_points) - min(p[1] for p in bike_points)
        
        print(f"   Truck rectangle: {truck_width:.1f}w × {truck_height:.1f}h")
        print(f"   Bike rectangle: {bike_width:.1f}w × {bike_height:.1f}h")
        
        # Test different Y positions (simulating vehicles moving down the road)
        print()
        print("🛣️ Testing vehicles moving down the road:")
        
        for y_offset in [0, 50, 100, 150, 200]:
            # Position vehicles at their lane X positions but different Y positions
            truck.pos = [truck_path_px[0][0], truck_path_px[0][1] - y_offset]
            bike.pos = [bike_path_px[0][0], bike_path_px[0][1] - y_offset]
            
            collision = rotated_rectangles_collide(truck, bike)
            distance = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
            
            print(f"   Y offset {y_offset:3d}px: {'🚨 COLLISION' if collision else '✅ Safe'} (distance: {distance:.1f}px)")
        
        # Test edge case: vehicles very close together
        print()
        print("⚠️ Edge Case Testing:")
        
        # Move truck slightly toward bike lane
        for x_drift in [0, 5, 10, 15, 20, 25, 30]:
            truck.pos = [truck_path_px[0][0] + x_drift, truck_path_px[0][1]]
            bike.pos = [bike_path_px[0][0], bike_path_px[0][1]]
            
            collision = rotated_rectangles_collide(truck, bike)
            distance = math.hypot(bike.pos[0] - truck.pos[0], bike.pos[1] - truck.pos[1])
            
            print(f"   Truck drift {x_drift:2d}px: {'🚨 COLLISION' if collision else '✅ Safe'} (distance: {distance:.1f}px)")
        
        # Check if there's something wrong with the collision detection itself
        print()
        print("🔧 Collision Detection Verification:")
        
        # Test with identical positions (should always collide)
        truck.pos = [400, 300]
        bike.pos = [400, 300]
        identical_collision = rotated_rectangles_collide(truck, bike)
        print(f"   Identical positions: {'✅ Collision detected' if identical_collision else '🚨 ERROR - No collision!'}")
        
        # Test with far apart positions (should never collide)
        truck.pos = [100, 300]
        bike.pos = [500, 300]
        far_collision = rotated_rectangles_collide(truck, bike)
        print(f"   Far apart (400px): {'🚨 ERROR - Collision detected!' if far_collision else '✅ No collision'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_collision_algorithm():
    """Test the collision detection algorithm itself."""
    try:
        from traffic_sim.services.physics import rotated_rectangles_collide, project_polygon, get_rotated_collision_points
        from traffic_sim.domain.actors.truck import Truck
        from traffic_sim.domain.actors.cyclist import Cyclist
        from traffic_sim.services.pathing import CARS_NS_UP, BIKES_NS_UP, to_pixels
        
        print()
        print("🧮 Testing Collision Algorithm Details:")
        
        screen_size = (1280, 720)
        truck_path = to_pixels(CARS_NS_UP, *screen_size)
        bike_path = to_pixels(BIKES_NS_UP, *screen_size)
        
        truck = Truck(truck_path)
        bike = Cyclist(bike_path)
        
        # Set positions in separate lanes
        truck.pos = [truck_path[0][0], 300]
        bike.pos = [bike_path[0][0], 300]
        
        print(f"   Truck position: {truck.pos}")
        print(f"   Bike position: {bike.pos}")
        
        # Get collision points
        truck_points = get_rotated_collision_points(truck)
        bike_points = get_rotated_collision_points(bike)
        
        # Test SAT algorithm manually
        collision_result = rotated_rectangles_collide(truck, bike)
        
        print(f"   SAT collision result: {collision_result}")
        
        # Calculate axes for SAT
        truck_axes = []
        bike_axes = []
        
        # Get axes from truck edges
        for i in range(len(truck_points)):
            p1 = truck_points[i]
            p2 = truck_points[(i + 1) % len(truck_points)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            # Perpendicular axis
            axis = (-edge[1], edge[0])
            # Normalize
            length = math.sqrt(axis[0]**2 + axis[1]**2)
            if length > 0:
                truck_axes.append((axis[0]/length, axis[1]/length))
        
        # Get axes from bike edges  
        for i in range(len(bike_points)):
            p1 = bike_points[i]
            p2 = bike_points[(i + 1) % len(bike_points)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            # Perpendicular axis
            axis = (-edge[1], edge[0])
            # Normalize
            length = math.sqrt(axis[0]**2 + axis[1]**2)
            if length > 0:
                bike_axes.append((axis[0]/length, axis[1]/length))
        
        print(f"   Truck axes: {len(truck_axes)}")
        print(f"   Bike axes: {len(bike_axes)}")
        
        # Test projections
        all_axes = truck_axes + bike_axes
        separating_axis_found = False
        
        for i, axis in enumerate(all_axes):
            truck_proj = project_polygon(truck_points, axis)
            bike_proj = project_polygon(bike_points, axis)
            
            # Check for separation
            separated = truck_proj[1] < bike_proj[0] or bike_proj[1] < truck_proj[0]
            if separated:
                separating_axis_found = True
                print(f"   Axis {i}: SEPARATED (truck: {truck_proj[0]:.1f}-{truck_proj[1]:.1f}, bike: {bike_proj[0]:.1f}-{bike_proj[1]:.1f})")
                break
        
        if not separating_axis_found:
            print(f"   No separating axis found - collision detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in algorithm test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Comprehensive truck-bike collision debugging...")
    print("=" * 80)
    
    success1 = test_simulation_collisions()
    success2 = test_collision_algorithm()
    
    print()
    print("=" * 80)
    if success1 and success2:
        print("✅ Collision debugging completed!")
    else:
        print("❌ Collision debugging found issues!")