#!/usr/bin/env python3
"""
Test script to debug traffic light ignore behavior after path point 2.
This script will create vehicles and test their traffic light behavior at different path points.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from traffic_sim.domain.actors.car import Car
from traffic_sim.services.pathing import to_pixels, CARS_NS_UP

def mock_can_cross_red():
    """Mock function that always returns False (red light)"""
    return False

def mock_can_cross_green():
    """Mock function that always returns True (green light)"""
    return True

def test_traffic_light_behavior():
    """Test how vehicles respond to traffic lights at different path points"""
    
    print("🚦 Testing Traffic Light Behavior After Path Point 2")
    print("=" * 60)
    
    # Create a test path with multiple points (using 800x600 screen size)
    path = to_pixels(CARS_NS_UP, 800, 600)
    print(f"Test path has {len(path)} points: {path}")
    
    # Test with red light (should stop before path point 2)
    print("\n🔴 Testing with RED LIGHT:")
    car_red = Car(path, speed_px_s=50, can_cross_ok=mock_can_cross_red)
    
    # Test at different path indices
    for i in range(min(5, len(path))):
        # Reset car position to test each path point
        car_red.i = i
        car_red.pos = list(path[i]) if i < len(path) else car_red.pos
        
        print(f"\n  Path Index {i}:")
        print(f"    cross_index = {car_red.cross_index}")
        print(f"    Position: {car_red.pos}")
        
        # Check if vehicle will obey traffic light
        will_check_light = car_red.cross_index is not None and i < 2
        print(f"    Will check traffic light: {will_check_light}")
        
        if will_check_light:
            print(f"    🛑 Vehicle STOPS (obeys red light)")
        else:
            print(f"    ✅ Vehicle CONTINUES (ignores traffic light)")
    
    print("\n" + "=" * 60)
    print("\n🟢 Testing with GREEN LIGHT:")
    car_green = Car(path, speed_px_s=50, can_cross_ok=mock_can_cross_green)
    
    for i in range(min(5, len(path))):
        car_green.i = i
        car_green.pos = list(path[i]) if i < len(path) else car_green.pos
        
        print(f"\n  Path Index {i}:")
        will_check_light = car_green.cross_index is not None and i < 2
        print(f"    Will check traffic light: {will_check_light}")
        
        if will_check_light:
            print(f"    ✅ Vehicle CONTINUES (green light)")
        else:
            print(f"    ✅ Vehicle CONTINUES (ignores traffic light)")

def test_specific_scenario():
    """Test the specific scenario: vehicle waits at red, light turns green, then red again"""
    
    print("\n" + "=" * 60)
    print("🎯 SPECIFIC SCENARIO TEST:")
    print("Vehicle waits at red light, light turns green, vehicle enters intersection,")
    print("light turns red again - vehicle should continue through!")
    print("=" * 60)
    
    path = to_pixels(CARS_NS_UP, 800, 600)
    
    # Start with red light
    light_is_green = False
    
    def dynamic_can_cross():
        return light_is_green
    
    car = Car(path, speed_px_s=50, can_cross_ok=dynamic_can_cross)
    
    # Scenario 1: At path index 0 or 1 with red light
    print("\n📍 STEP 1: Vehicle at path index 1 (stop line) with RED light")
    car.i = 1  # At stop line
    will_check = car.cross_index is not None and car.i < 2
    can_cross = dynamic_can_cross()
    print(f"  Path index: {car.i}")
    print(f"  cross_index: {car.cross_index}")
    print(f"  Will check light: {will_check}")
    print(f"  Light is green: {can_cross}")
    print(f"  Result: {'WAIT' if will_check and not can_cross else 'GO'}")
    
    # Scenario 2: Light turns green, vehicle moves to path index 2
    print("\n📍 STEP 2: Light turns GREEN, vehicle moves to path index 2")
    light_is_green = True
    car.i = 2  # Moved to path index 2
    will_check = car.cross_index is not None and car.i < 2
    can_cross = dynamic_can_cross()
    print(f"  Path index: {car.i}")
    print(f"  cross_index: {car.cross_index}")
    print(f"  Will check light: {will_check}")
    print(f"  Light is green: {can_cross}")
    print(f"  Result: {'WAIT' if will_check and not can_cross else 'GO'}")
    
    # Scenario 3: Light turns red again, but vehicle is past commitment point
    print("\n📍 STEP 3: Light turns RED again, but vehicle is at path index 2+")
    light_is_green = False
    car.i = 2  # Still at path index 2
    will_check = car.cross_index is not None and car.i < 2
    can_cross = dynamic_can_cross()
    print(f"  Path index: {car.i}")
    print(f"  cross_index: {car.cross_index}")
    print(f"  Will check light: {will_check}")
    print(f"  Light is green: {can_cross}")
    print(f"  Result: {'WAIT' if will_check and not can_cross else 'GO'}")
    
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("  - Step 1: Vehicle WAITS (red light, before commitment)")
    print("  - Step 2: Vehicle GOES (green light)")  
    print("  - Step 3: Vehicle CONTINUES (ignores red light after commitment)")

if __name__ == "__main__":
    test_traffic_light_behavior()
    test_specific_scenario()
    
    print("\n" + "=" * 60)
    print("✅ Test complete! Check the results above.")
    print("If vehicles are still waiting at traffic lights, the issue might be")
    print("that they're not progressing past path index 1 in the first place.")