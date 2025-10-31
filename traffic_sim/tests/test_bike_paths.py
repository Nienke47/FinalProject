#!/usr/bin/env python3

"""
Test script to verify bike path spawning is working properly.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_bike_paths():
    """Test bike path spawning."""
    try:
        from traffic_sim.services.pathing import (
            BIKES_NS_UP, BIKES_NS_LEFT, BIKES_NS_RIGHT,
            BIKES_EW_RIGHT, BIKES_EW_LEFT, BIKES_EW_TURN_RIGHT,
            to_pixels
        )
        from traffic_sim.domain.actors.cyclist import Cyclist
        
        print("🚴 Testing bike path configurations...")
        print()
        
        # Test screen size (same as in app)
        screen_size = (1280, 720)
        
        print("📍 North-South Bike Paths:")
        ns_paths = [
            ("BIKES_NS_UP", BIKES_NS_UP),
            ("BIKES_NS_LEFT", BIKES_NS_LEFT), 
            ("BIKES_NS_RIGHT", BIKES_NS_RIGHT)
        ]
        
        for name, path in ns_paths:
            path_px = to_pixels(path, *screen_size)
            start_point = path_px[0]
            end_point = path_px[-1]
            print(f"   {name}:")
            print(f"     Start: {start_point}")
            print(f"     End: {end_point}")
            print(f"     Length: {len(path_px)} points")
        
        print()
        print("📍 East-West Bike Paths:")
        ew_paths = [
            ("BIKES_EW_RIGHT", BIKES_EW_RIGHT),
            ("BIKES_EW_LEFT", BIKES_EW_LEFT),
            ("BIKES_EW_TURN_RIGHT", BIKES_EW_TURN_RIGHT)
        ]
        
        for name, path in ew_paths:
            path_px = to_pixels(path, *screen_size)
            start_point = path_px[0]
            end_point = path_px[-1]
            print(f"   {name}:")
            print(f"     Start: {start_point}")
            print(f"     End: {end_point}")
            print(f"     Length: {len(path_px)} points")
        
        print()
        print("🔧 Testing Cyclist Creation:")
        
        # Test creating cyclists with EW paths
        try:
            bikes_ew_right_px = to_pixels(BIKES_EW_RIGHT, *screen_size)
            cyclist_ew = Cyclist(bikes_ew_right_px, speed_px_s=90)
            print(f"   ✅ EW cyclist created successfully")
            print(f"     Position: {cyclist_ew.pos}")
            print(f"     Path start: {cyclist_ew.path[0]}")
        except Exception as e:
            print(f"   ❌ EW cyclist creation failed: {e}")
            
        try:
            bikes_ns_up_px = to_pixels(BIKES_NS_UP, *screen_size)
            cyclist_ns = Cyclist(bikes_ns_up_px, speed_px_s=90)
            print(f"   ✅ NS cyclist created successfully")
            print(f"     Position: {cyclist_ns.pos}")
            print(f"     Path start: {cyclist_ns.path[0]}")
        except Exception as e:
            print(f"   ❌ NS cyclist creation failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing bike path configurations...")
    print("=" * 70)
    
    success = test_bike_paths()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Bike path test completed!")
    else:
        print("❌ Bike path test failed.")