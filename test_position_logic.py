#!/usr/bin/env python3
"""
Test the new position-based traffic light logic.
"""

import sys
import math
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from traffic_sim.domain.actors.car import Car
from traffic_sim.services.pathing import to_pixels, CARS_NS_UP

def test_position_based_traffic_light_logic():
    """Test the new position-based traffic light logic"""
    
    print("🚦 TESTING NEW POSITION-BASED TRAFFIC LIGHT LOGIC")
    print("=" * 60)
    
    # Create path
    path = to_pixels(CARS_NS_UP, 800, 600)
    print(f"Path points:")
    for i, point in enumerate(path):
        print(f"  {i}: {point}")
    
    # Traffic light (red)
    def red_light():
        return False
    
    car = Car(path, speed_px_s=50, can_cross_ok=red_light)
    
    print(f"\nCross index (stop line): {car.cross_index}")
    stop_line_pos = path[car.cross_index]
    print(f"Stop line position: {stop_line_pos}")
    
    # Test at different positions relative to stop line
    test_positions = [
        (432, 480),    # Exactly at stop line
        (432, 470),    # 10px past stop line
        (432, 450),    # 30px past stop line
        (432, 440),    # 40px past stop line
        (432, 400),    # 80px past stop line
    ]
    
    for pos in test_positions:
        car.pos = list(pos)
        car.i = 1  # At stop line path index
        
        # Calculate distance past stop line (using the same logic as in the code)
        stop_line_pos = path[car.cross_index]
        
        # For vertical movement (north-south), check Y distance
        if abs(stop_line_pos[0] - path[0][0]) < abs(stop_line_pos[1] - path[0][1]):
            distance_past_stop = abs(car.pos[1] - stop_line_pos[1])
        else:
            distance_past_stop = abs(car.pos[0] - stop_line_pos[0])
        
        commitment_distance = 30
        will_check_light = (car.cross_index is not None and 
                           car.i <= car.cross_index and 
                           distance_past_stop <= commitment_distance)
        
        print(f"\nPosition {pos}:")
        print(f"  Distance past stop line: {distance_past_stop:.1f}px")
        print(f"  Within commitment distance ({commitment_distance}px): {distance_past_stop <= commitment_distance}")
        print(f"  Will check traffic light: {will_check_light}")
        
        if will_check_light:
            print(f"  🛑 Vehicle WAITS (red light, within commitment zone)")
        else:
            print(f"  ✅ Vehicle IGNORES light (past commitment point)")

def simulate_movement_with_new_logic():
    """Simulate vehicle movement with the new position-based logic"""
    
    print("\n" + "=" * 60)
    print("🚗 SIMULATING MOVEMENT WITH NEW LOGIC")
    print("=" * 60)
    
    path = to_pixels(CARS_NS_UP, 800, 600)
    
    # Start with red light, then turn green
    light_is_green = False
    
    def traffic_light():
        return light_is_green
    
    car = Car(path, speed_px_s=100, can_cross_ok=traffic_light)
    
    # Position vehicle approaching stop line
    car.i = 1
    car.pos = [432, 485]  # 5px before stop line at (432, 480)
    
    print(f"Initial state:")
    print(f"  Position: {car.pos}")
    print(f"  Path index: {car.i}")
    print(f"  Light is green: {light_is_green}")
    
    # Try to move with red light
    print(f"\n🔴 Testing movement with RED light:")
    for i in range(3):
        old_pos = car.pos[:]
        car.update(0.016)
        moved = car.pos != old_pos
        print(f"  Update {i+1}: {old_pos} -> {car.pos} (moved: {moved})")
        
        # Calculate distance past stop line
        stop_line_pos = path[car.cross_index]
        distance_past = abs(car.pos[1] - stop_line_pos[1])
        print(f"    Distance past stop line: {distance_past:.1f}px")
        
        if not moved:
            break
    
    # Change to green light
    light_is_green = True
    print(f"\n🟢 Light changed to GREEN - continuing movement:")
    
    for i in range(10):
        old_pos = car.pos[:]
        car.update(0.016)
        
        # Calculate distance past stop line
        stop_line_pos = path[car.cross_index]
        distance_past = abs(car.pos[1] - stop_line_pos[1])
        
        # Check if traffic light would be checked
        will_check = (car.cross_index is not None and 
                     car.i <= car.cross_index and 
                     distance_past <= 30)
        
        print(f"  Update {i+1}: pos {car.pos[1]:.1f}, past stop: {distance_past:.1f}px, checks light: {will_check}")
        
        if distance_past > 35:  # Past commitment point
            print(f"    ✅ Vehicle is now past commitment point - ignores traffic lights!")
            break

if __name__ == "__main__":
    test_position_based_traffic_light_logic()
    simulate_movement_with_new_logic()