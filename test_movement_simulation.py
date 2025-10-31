#!/usr/bin/env python3
"""
Test script to simulate vehicle movement through traffic lights.
This will show step-by-step what happens when a vehicle approaches and moves through a traffic light.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from traffic_sim.domain.actors.car import Car
from traffic_sim.services.pathing import to_pixels, CARS_NS_UP

def test_vehicle_movement_through_intersection():
    """Simulate a vehicle moving through intersection with changing lights"""
    
    print("🚗 VEHICLE MOVEMENT SIMULATION")
    print("=" * 50)
    
    # Create path
    path = to_pixels(CARS_NS_UP, 800, 600)
    print(f"Path: {path}")
    
    # Traffic light states
    light_is_green = True  # Start with green
    
    def traffic_light_callback():
        return light_is_green
    
    # Create vehicle
    car = Car(path, speed_px_s=100, can_cross_ok=traffic_light_callback)
    
    print(f"\n🚦 Initial state:")
    print(f"  cross_index: {car.cross_index}")
    print(f"  path index: {car.i}")
    print(f"  position: {car.pos}")
    
    # Simulate movement frames
    dt = 0.016  # ~60 FPS
    
    for frame in range(100):  # Simulate 100 frames
        old_i = car.i
        old_pos = car.pos[:]
        
        # Check traffic light condition BEFORE update
        will_check_light = car.cross_index is not None and car.i < 2
        can_cross = traffic_light_callback()
        should_stop = will_check_light and not can_cross
        
        # Update vehicle
        car.update(dt)
        
        # Check if anything changed
        pos_changed = old_pos != car.pos
        index_changed = old_i != car.i
        
        if index_changed or frame % 20 == 0:  # Print every 20 frames or when index changes
            print(f"\n📍 Frame {frame}:")
            print(f"  Path index: {old_i} -> {car.i}")
            print(f"  Position: {old_pos} -> {car.pos}")
            print(f"  Light is green: {can_cross}")
            print(f"  Will check light: {will_check_light}")
            print(f"  Should stop: {should_stop}")
            print(f"  Vehicle done: {car.done}")
            
            # Change light to red when vehicle is at path index 1
            if car.i == 1 and light_is_green:
                light_is_green = False
                print(f"  🔴 LIGHT CHANGED TO RED!")
            
            # Change light back to green after a few frames
            elif frame > 50 and not light_is_green:
                light_is_green = True
                print(f"  🟢 LIGHT CHANGED TO GREEN!")
        
        if car.done:
            print(f"\n✅ Vehicle completed journey at frame {frame}")
            print(f"   Final position: {car.pos}")
            print(f"   Completion reason: {car.completion_reason}")
            break
        
        # Safety break
        if frame > 90:
            print(f"\n⚠️  Simulation stopped - vehicle might be stuck")
            break

def test_simple_light_scenario():
    """Test the exact scenario: approach red light, wait, green light, continue"""
    
    print("\n" + "=" * 50)
    print("🎯 SIMPLE LIGHT SCENARIO TEST")
    print("=" * 50)
    
    path = to_pixels(CARS_NS_UP, 800, 600)
    
    # Start with red light
    light_state = "RED"
    
    def get_light_state():
        return light_state == "GREEN"
    
    car = Car(path, speed_px_s=50, can_cross_ok=get_light_state)
    
    # Manually position vehicle near stop line
    car.i = 1  # At stop line (path index 1)
    car.pos = list(path[1])  # Position at stop line
    
    print(f"\n🚦 SCENARIO: Vehicle at stop line with RED light")
    print(f"  cross_index: {car.cross_index}")
    print(f"  path index: {car.i}")
    print(f"  position: {car.pos}")
    print(f"  light: {light_state}")
    
    # Try to update - should not move
    old_pos = car.pos[:]
    car.update(0.016)
    
    print(f"\n📍 After update with RED light:")
    print(f"  position: {old_pos} -> {car.pos}")
    print(f"  moved: {'YES' if car.pos != old_pos else 'NO'}")
    
    # Change light to green
    light_state = "GREEN"
    print(f"\n🟢 LIGHT CHANGED TO GREEN")
    
    # Update several times
    for i in range(5):
        old_pos = car.pos[:]
        old_i = car.i
        car.update(0.016)
        
        print(f"  Update {i+1}: index {old_i}->{car.i}, pos moved: {'YES' if car.pos != old_pos else 'NO'}")
        
        if car.i >= 2:
            print(f"  ✅ Vehicle reached path index 2+ - now ignoring traffic lights!")
            break

if __name__ == "__main__":
    test_vehicle_movement_through_intersection()
    test_simple_light_scenario()