#!/usr/bin/env python3

"""
Enhanced test to debug spawn safety issues.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_spawn_safety_detailed():
    """Test spawn safety with detailed debugging."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.actors.cyclist import Cyclist
        from traffic_sim.services.pathing import BIKES_EW_RIGHT, to_pixels
        
        print("🔍 Detailed spawn safety debugging...")
        print()
        
        # Create app instance
        app = App()
        screen_width, screen_height = app.size
        print(f"Screen size: {screen_width} x {screen_height}")
        
        # Create EW cyclist
        bikes_ew_right_px = to_pixels(BIKES_EW_RIGHT, screen_width, screen_height)
        cyclist_ew = Cyclist(
            bikes_ew_right_px, 
            speed_px_s=90, 
            can_cross_ok=app.ctrl.can_ped_cross_ew
        )
        
        print(f"EW cyclist position: {cyclist_ew.pos}")
        print(f"EW cyclist path: {cyclist_ew.path}")
        
        # Check off-screen status
        new_x, new_y = cyclist_ew.pos
        off_screen = (new_x < 0 or new_x > screen_width or new_y < 0 or new_y > screen_height)
        print(f"Off-screen status: {off_screen}")
        print(f"  X < 0: {new_x < 0} (x={new_x})")
        print(f"  X > width: {new_x > screen_width} (x={new_x}, width={screen_width})")
        print(f"  Y < 0: {new_y < 0} (y={new_y})")
        print(f"  Y > height: {new_y > screen_height} (y={new_y}, height={screen_height})")
        
        # Test spawn safety step by step
        print()
        print("Checking spawn safety step by step:")
        
        # Step 1: Check if no agents
        print(f"1. No existing agents: {len(app.agents) == 0}")
        
        if len(app.agents) > 0:
            print(f"   Existing agents: {len(app.agents)}")
            for i, agent in enumerate(app.agents):
                print(f"     Agent {i}: {type(agent).__name__} at {agent.pos}")
        
        # Step 2: Try spawn safety manually
        if len(app.agents) == 0:
            # Add a dummy agent to test collision logic
            from traffic_sim.domain.actors.car import Car
            from traffic_sim.services.pathing import CARS_NS_UP
            cars_ns_up_px = to_pixels(CARS_NS_UP, screen_width, screen_height)
            dummy_car = Car(cars_ns_up_px)
            app.agents.append(dummy_car)
            print(f"   Added dummy car at: {dummy_car.pos}")
        
        # Now test spawn safety
        safe = app._is_safe_spawn_position(cyclist_ew)
        print(f"2. Spawn safety result: {safe}")
        
        # Test collision detection directly
        from traffic_sim.services.physics import rotated_rectangles_collide
        
        print("3. Direct collision checks:")
        for i, existing_agent in enumerate(app.agents):
            if getattr(existing_agent, 'done', False):
                continue
            collision = rotated_rectangles_collide(cyclist_ew, existing_agent)
            print(f"   vs Agent {i} ({type(existing_agent).__name__}): collision = {collision}")
            print(f"      EW bike: {cyclist_ew.pos}")
            print(f"      Existing: {existing_agent.pos}")
            
            # Calculate distance
            import math
            distance = math.hypot(existing_agent.pos[0] - cyclist_ew.pos[0], 
                                existing_agent.pos[1] - cyclist_ew.pos[1])
            print(f"      Distance: {distance:.1f}px")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Enhanced spawn safety debugging...")
    print("=" * 70)
    
    success = test_spawn_safety_detailed()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Spawn safety debugging completed!")
    else:
        print("❌ Spawn safety debugging failed.")