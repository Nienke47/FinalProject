#!/usr/bin/env python3
"""
Test pedestrian behavior directly to understand why they mark themselves as done.
"""

import sys
import os

# Add the traffic_sim directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'traffic_sim'))

import pygame
from core.testapp import App
from domain.actors.pedestrian import Pedestrian

def test_pedestrian_behavior():
    """Test pedestrian behavior directly."""
    
    print("🚶 Testing pedestrian behavior directly")
    print("=" * 80)
    
    # Initialize pygame
    pygame.init()
    
    # Initialize the app to get proper paths and traffic controller
    app = App()
    
    print(f"🔧 Creating test pedestrians...")
    
    # Test 1: Create pedestrian with always-true can_cross
    ped_always = Pedestrian(
        path_px=app.peds_ew_right_px, 
        speed_px_s=70, 
        can_cross_ok=lambda: True  # Always allowed to cross
    )
    
    # Test 2: Create pedestrian with EW ped crossing logic  
    ped_ew_only = Pedestrian(
        path_px=app.peds_ew_right_px, 
        speed_px_s=70, 
        can_cross_ok=app.ctrl.can_ped_cross_ew  # Original logic
    )
    
    # Test 3: Create pedestrian with EW car OR ped crossing logic
    def ew_flexible_cross():
        return app.ctrl.can_cars_cross_ew() or app.ctrl.can_ped_cross_ew()
    
    ped_flexible = Pedestrian(
        path_px=app.peds_ew_right_px, 
        speed_px_s=70, 
        can_cross_ok=ew_flexible_cross  # New logic
    )
    
    pedestrians = [
        ("Always Cross", ped_always),
        ("EW Ped Only", ped_ew_only), 
        ("EW Flexible", ped_flexible)
    ]
    
    print(f"📍 Pedestrian path: {app.peds_ew_right_px}")
    print(f"🚦 Initial traffic state:")
    print(f"   Cars EW: {app.ctrl.can_cars_cross_ew()}")
    print(f"   Peds EW: {app.ctrl.can_ped_cross_ew()}")
    print()
    
    # Test their behavior over several updates
    for i in range(10):  # 10 frames
        dt = 1/60  # 60 FPS
        
        print(f"Frame {i+1}:")
        
        # Update traffic controller
        app.ctrl.update(dt)
        
        print(f"   Traffic - Cars EW: {app.ctrl.can_cars_cross_ew()}, Peds EW: {app.ctrl.can_ped_cross_ew()}")
        
        for name, ped in pedestrians:
            if not ped.done:
                old_pos = list(ped.pos)
                ped.update(dt)
                new_pos = list(ped.pos)
                
                moved = (abs(new_pos[0] - old_pos[0]) > 0.1 or abs(new_pos[1] - old_pos[1]) > 0.1)
                
                print(f"   {name}: Pos=({ped.pos[0]:.1f}, {ped.pos[1]:.1f}), Done={ped.done}, Moved={moved}")
                
                if ped.done:
                    reason = getattr(ped, 'completion_reason', 'unknown')
                    print(f"      -> MARKED DONE! Reason: {reason}")
            else:
                reason = getattr(ped, 'completion_reason', 'unknown') 
                print(f"   {name}: ALREADY DONE (reason: {reason})")
        
        print()
        
        # Stop if all are done
        if all(ped.done for name, ped in pedestrians):
            print("All pedestrians are done. Stopping test.")
            break
    
    print("=" * 80)
    print("📊 Final Status:")
    for name, ped in pedestrians:
        reason = getattr(ped, 'completion_reason', 'unknown')
        print(f"   {name}: Done={ped.done}, Pos=({ped.pos[0]:.1f}, {ped.pos[1]:.1f}), Reason={reason}")

if __name__ == "__main__":
    test_pedestrian_behavior()