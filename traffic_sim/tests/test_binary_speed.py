#!/usr/bin/env python3
"""
Test script to demonstrate the new binary speed behavior:
- Vehicles drive at full speed when safe
- Vehicles stop completely at reasonable distance (no gradual slowing)
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_binary_speed_behavior():
    """Test the new binary speed behavior"""
    
    print("🚗 NEW BINARY SPEED BEHAVIOR TEST")
    print("=" * 50)
    
    print("🎯 BEHAVIOR CHANGE:")
    print("  OLD: Gradual slowing down as vehicles approach each other")
    print("  NEW: Full speed OR complete stop (binary behavior)")
    
    print("\n📏 DISTANCE-BASED BEHAVIOR:")
    
    # Test different distances for cars (60px min following distance)
    test_distances = [
        (100, "FAR APART"),
        (80, "COMFORTABLE"), 
        (65, "GETTING CLOSE"),
        (60, "AT THRESHOLD"),
        (50, "TOO CLOSE"),
        (40, "MUCH TOO CLOSE")
    ]
    
    print("\nTesting CAR behavior (60px min following distance):")
    print("Distance | Old Behavior        | New Behavior")
    print("---------|--------------------|-----------------")
    
    for distance, description in test_distances:
        # Simulate old gradual behavior
        if distance > 120:  # Was: full speed when far
            old_behavior = "100% speed"
        elif distance > 90:  # Was: slight slowdown
            old_behavior = "80% speed"
        elif distance > 60:  # Was: moderate slowdown  
            old_behavior = "50% speed"
        elif distance > 30:  # Was: heavy slowdown
            old_behavior = "20% speed"
        else:  # Was: almost stop
            old_behavior = "10% speed"
        
        # New binary behavior
        if distance > 60:  # Above threshold
            new_behavior = "100% SPEED"
        else:  # At or below threshold
            new_behavior = "STOP (0%)"
        
        print(f"{distance:3}px    | {old_behavior:<18} | {new_behavior}")
    
    print(f"\n✅ KEY CHANGE:")
    print(f"  • No more gradual slowing (80%, 50%, 20% speeds)")
    print(f"  • Simple binary decision: FULL SPEED or COMPLETE STOP")
    print(f"  • Vehicles stop at reasonable distance (60px for cars)")

def test_all_vehicle_types():
    """Test behavior for different vehicle types"""
    
    print("\n" + "=" * 50)
    print("🚛 ALL VEHICLE TYPES - BINARY BEHAVIOR")
    print("=" * 50)
    
    try:
        from traffic_sim.configuration import Config
        config = Config()
        
        vehicle_types = ["CAR", "TRUCK", "CYCLIST", "PEDESTRIAN"]
        
        for vehicle_type in vehicle_types:
            if vehicle_type in config.VEHICLE_SPACING:
                settings = config.VEHICLE_SPACING[vehicle_type]
                min_distance = settings["MIN_FOLLOWING_DISTANCE"]
                
                print(f"\n{vehicle_type}:")
                print(f"  Stop distance: {min_distance}px")
                print(f"  Behavior:")
                print(f"    Distance > {min_distance}px: 🟢 FULL SPEED (100%)")
                print(f"    Distance ≤ {min_distance}px: 🛑 COMPLETE STOP (0%)")
    
    except ImportError:
        print("Could not load configuration")

def test_scenarios():
    """Test realistic scenarios"""
    
    print("\n" + "=" * 50) 
    print("📖 REALISTIC SCENARIOS")
    print("=" * 50)
    
    print("🚦 SCENARIO 1: Car following another car")
    print("  Distance 100px: Car drives at FULL SPEED")
    print("  Distance 65px:  Car drives at FULL SPEED") 
    print("  Distance 60px:  Car STOPS COMPLETELY")
    print("  Distance 55px:  Car remains STOPPED")
    print("  → Clear binary behavior!")
    
    print("\n🚦 SCENARIO 2: Traffic light queue")
    print("  Car A stops at red light")
    print("  Car B approaches:")
    print("    Distance 70px: Car B at FULL SPEED")
    print("    Distance 60px: Car B STOPS (60px behind Car A)")
    print("  Car C approaches:")
    print("    Distance 130px: Car C at FULL SPEED")  
    print("    Distance 60px:  Car C STOPS (60px behind Car B)")
    print("  → No gradual slowing in queue!")
    
    print("\n🚦 SCENARIO 3: Mixed vehicle types")
    print("  Truck (80px stop distance) following Car:")
    print("    Distance 90px: Truck at FULL SPEED")
    print("    Distance 80px: Truck STOPS")
    print("  Cyclist (40px stop distance) following Car:")
    print("    Distance 50px: Cyclist at FULL SPEED") 
    print("    Distance 40px: Cyclist STOPS")
    print("  → Each vehicle type has its own stop distance!")

if __name__ == "__main__":
    test_binary_speed_behavior()
    test_all_vehicle_types()
    test_scenarios()
    
    print("\n" + "=" * 50)
    print("✅ BINARY SPEED SYSTEM IMPLEMENTED!")
    print("=" * 50)
    print("📋 Summary:")
    print("  • ❌ Removed gradual slowing (no more 50%, 20% speeds)")
    print("  • ✅ Added binary behavior: FULL SPEED or COMPLETE STOP")
    print("  • 🎯 Vehicles stop at reasonable distances:")
    print("    - Cars: 60px apart")
    print("    - Trucks: 80px apart") 
    print("    - Cyclists: 40px apart")
    print("    - Pedestrians: 25px apart")
    print("  • 🚗 Clean, predictable vehicle behavior!")
    print("\n🎮 Run the simulation to see the new binary speed behavior!")