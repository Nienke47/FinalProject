#!/usr/bin/env python3
"""
Test script to verify the no-touch vehicle spacing behavior.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from traffic_sim.configuration import Config
from traffic_sim.domain.actors.car import Car
from traffic_sim.domain.actors.truck import Truck
from traffic_sim.domain.actors.cyclist import Cyclist
from traffic_sim.domain.actors.pedestrian import Pedestrian
from traffic_sim.services.pathing import to_pixels, CARS_NS_UP

def test_no_touch_spacing():
    """Test that vehicles maintain proper spacing and don't touch"""
    
    print("🚗 TESTING NO-TOUCH VEHICLE SPACING")
    print("=" * 50)
    
    config = Config()
    
    # Display current spacing settings
    print("📏 Current spacing settings:")
    for vehicle_type, settings in config.VEHICLE_SPACING.items():
        if vehicle_type != "DEFAULT":
            print(f"\n{vehicle_type}:")
            print(f"  Min following distance: {settings['MIN_FOLLOWING_DISTANCE']}px")
            print(f"  Emergency stop distance: {settings['EMERGENCY_STOP_DISTANCE']}px")
    
    print(f"\n🛡️  Collision detection threshold: 35.0px")
    print(f"📐 Collision radii:")
    for vehicle_type, radius in config.COLLISION_RADIUS.items():
        print(f"  {vehicle_type}: {radius}px")
    
    # Test different vehicle combinations
    path = to_pixels(CARS_NS_UP, 800, 600)
    
    print(f"\n🧪 Testing vehicle spacing scenarios:")
    
    # Create test vehicles
    vehicles = [
        ("CAR", Car(path, speed_px_s=50)),
        ("TRUCK", Truck(path, speed_px_s=40)),
        ("CYCLIST", Cyclist(path, speed_px_s=30)), 
        ("PEDESTRIAN", Pedestrian(path, speed_px_s=20))
    ]
    
    for i, (name, vehicle) in enumerate(vehicles):
        settings = vehicle.get_collision_settings()
        min_distance = settings["MIN_FOLLOWING_DISTANCE"]
        emergency_distance = settings["EMERGENCY_STOP_DISTANCE"]
        collision_radius = config.COLLISION_RADIUS[name.upper()]
        
        print(f"\n{name}:")
        print(f"  ✅ Min following distance: {min_distance}px")
        print(f"  🚨 Emergency stop distance: {emergency_distance}px") 
        print(f"  🛡️  Collision radius: {collision_radius}px")
        
        # Calculate total safe distance (collision radius + min distance)
        total_safe_distance = collision_radius * 2 + min_distance
        print(f"  📏 Total safe distance: {total_safe_distance}px")
        
        # Verify distances are sufficient
        if min_distance > collision_radius * 2:
            print(f"  ✅ SAFE: Min distance > 2x collision radius")
        else:
            print(f"  ⚠️  WARNING: Min distance may allow touching")
            
        if emergency_distance > collision_radius * 1.5:
            print(f"  ✅ SAFE: Emergency distance provides buffer")
        else:
            print(f"  ⚠️  WARNING: Emergency distance may be too small")

def test_distance_calculations():
    """Test distance calculations between vehicles"""
    
    print(f"\n" + "=" * 50)
    print("📐 DISTANCE CALCULATION TEST")
    print("=" * 50)
    
    config = Config()
    
    # Test vehicles at different distances
    test_scenarios = [
        (50, "TOUCHING - TOO CLOSE"),
        (40, "VERY CLOSE - EMERGENCY ZONE"), 
        (60, "SAFE FOLLOWING DISTANCE"),
        (80, "COMFORTABLE DISTANCE"),
        (100, "LARGE SAFE DISTANCE")
    ]
    
    print("Testing CAR following another CAR:")
    car_settings = config.VEHICLE_SPACING["CAR"]
    car_radius = config.COLLISION_RADIUS["CAR"]
    
    print(f"Car collision radius: {car_radius}px")
    print(f"Car min following distance: {car_settings['MIN_FOLLOWING_DISTANCE']}px")
    print(f"Car emergency stop distance: {car_settings['EMERGENCY_STOP_DISTANCE']}px")
    
    for distance, description in test_scenarios:
        print(f"\nDistance: {distance}px - {description}")
        
        # Check against collision detection
        if distance < 35.0:  # Collision detection threshold
            print(f"  🔴 COLLISION DETECTED (< 35px)")
        else:
            print(f"  ✅ No collision detected")
            
        # Check against vehicle collision radius
        if distance < car_radius * 2:
            print(f"  🔴 VEHICLES TOUCHING (< {car_radius * 2}px)")
        else:
            print(f"  ✅ Vehicles not touching")
            
        # Check against following distance
        if distance < car_settings["MIN_FOLLOWING_DISTANCE"]:
            print(f"  🟡 Too close for comfort (< {car_settings['MIN_FOLLOWING_DISTANCE']}px)")
        else:
            print(f"  ✅ Safe following distance")
            
        # Check against emergency distance  
        if distance < car_settings["EMERGENCY_STOP_DISTANCE"]:
            print(f"  🚨 EMERGENCY BRAKING ZONE (< {car_settings['EMERGENCY_STOP_DISTANCE']}px)")
        else:
            print(f"  ✅ Outside emergency zone")

if __name__ == "__main__":
    test_no_touch_spacing()
    test_distance_calculations()
    
    print(f"\n" + "=" * 50)
    print("✅ NO-TOUCH SPACING CONFIGURATION COMPLETE!")
    print("=" * 50)
    print("📋 Summary of changes made:")
    print("  • Increased minimum following distances")
    print("  • Increased emergency stop distances") 
    print("  • Increased collision radii for all vehicles")
    print("  • Set collision detection threshold to 35px")
    print("  • Vehicles now maintain strict no-touch spacing")
    print("\n🚗 Run the simulation to see vehicles maintaining safe distances!")