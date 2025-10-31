#!/usr/bin/env python3

"""
Debug the spawn filtering logic that might be preventing EW bikes.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_spawn_filtering():
    """Debug the spawn filtering logic."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.world.intersection import Phase
        
        print("🔍 Debugging spawn filtering logic...")
        print()
        
        # Create app
        app = App()
        
        print("📍 Spawn Point Analysis:")
        print(f"   EW bike spawn path: {app.bikes_ew_right_px[0]} (first point)")
        print(f"   NS bike spawn path: {app.bikes_ns_up_px[0]} (first point)")
        
        # Test the allow_spawn lambda logic
        print()
        print("🧪 Testing allow_spawn Logic:")
        
        # Clear agents for clean test
        app.agents = []
        
        # Test 1: Empty agents list (should allow spawn)
        ew_spawn_point = app.bikes_ew_right_px
        allow_spawn_ew = lambda p=ew_spawn_point: sum(
            1 for a in app.agents
            if getattr(a, "path", None) and a.path[0] == p[0] and not getattr(a, "done", False)
            and ((a.pos[0]-p[0][0])**2 + (a.pos[1]-p[0][1])**2)**0.5 < 180
        ) < 3
        
        result_empty = allow_spawn_ew()
        print(f"   Empty agents list: {'✅ ALLOW' if result_empty else '❌ BLOCK'}")
        
        # Test 2: Add some unrelated agents
        from traffic_sim.domain.actors.car import Car
        car1 = Car(app.cars_ns_up_px)
        car1.pos = [500, 400]  # Different position
        app.agents.append(car1)
        
        result_with_car = allow_spawn_ew()
        print(f"   With unrelated car: {'✅ ALLOW' if result_with_car else '❌ BLOCK'}")
        
        # Test 3: Add an EW bike (should eventually block if too many)
        bike1 = app.bike_ew_spawner.factory()
        app.agents.append(bike1)
        
        result_with_ew_bike = allow_spawn_ew()
        print(f"   With 1 EW bike: {'✅ ALLOW' if result_with_ew_bike else '❌ BLOCK'}")
        print(f"     EW bike position: {bike1.pos}")
        print(f"     EW spawn point: {ew_spawn_point[0]}")
        
        # Check the distance calculation
        import math
        distance = math.sqrt((bike1.pos[0] - ew_spawn_point[0][0])**2 + (bike1.pos[1] - ew_spawn_point[0][1])**2)
        print(f"     Distance to spawn point: {distance:.1f}px (threshold: 180px)")
        
        # Test 4: Traffic light phase check
        print()
        print("🚦 Traffic Light Phase Check:")
        
        phases = [Phase.NS_CARS_GREEN, Phase.EW_CARS_GREEN, Phase.NS_PED_BIKE, Phase.EW_PED_BIKE]
        
        for phase in phases:
            app.ctrl._enter_phase(phase)
            
            # Test the actual spawner
            can_spawn = app.bike_ew_spawner.factory() is not None
            print(f"   {phase.name}: {'✅ CAN SPAWN' if can_spawn else '❌ BLOCKED'}")
            
            # Check the crossing function
            ew_bike_can_cross = app.ctrl.can_cars_cross_ew() or app.ctrl.can_ped_cross_ew()
            print(f"     EW crossing allowed: {ew_bike_can_cross}")
        
        # Test 5: Full spawner update process
        print()
        print("🔄 Full Spawner Update Test:")
        
        app.ctrl._enter_phase(Phase.EW_CARS_GREEN)
        app.agents = []  # Clear agents
        
        # Test spawner update with different conditions
        for i in range(5):
            print(f"   Attempt {i+1}:")
            
            # Test allow_spawn condition
            allow_result = allow_spawn_ew()
            print(f"     allow_spawn: {'YES' if allow_result else 'NO'}")
            
            # Test spawner update
            new_agent = app.bike_ew_spawner.update(1.0, allow_spawn=allow_spawn_ew)
            if new_agent:
                print(f"     Spawner created agent: {type(new_agent).__name__} at {new_agent.pos}")
                
                # Test _add_agent
                added = app._add_agent(new_agent)
                print(f"     Agent added to simulation: {'YES' if added else 'NO'}")
                
            else:
                print(f"     Spawner created: NO")
        
        print(f"   Final agent count: {len(app.agents)}")
        
        # Count bikes
        ew_bikes = [a for a in app.agents if hasattr(a, 'path') and a.path and abs(a.path[0][0] + 102) < 50]
        print(f"   EW bikes in simulation: {len(ew_bikes)}")
        
        return len(ew_bikes) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging spawn filtering logic...")
    print("=" * 80)
    
    success = debug_spawn_filtering()
    
    print()
    print("=" * 80)
    if success:
        print("✅ EW bike spawning logic is working!")
    else:
        print("❌ Found issues with EW bike spawning logic!")