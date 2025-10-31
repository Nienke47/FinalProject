#!/usr/bin/env python3

"""
Test EW bike spawning and traffic light cycling.
"""

import sys
from pathlib import Path
import time

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ew_bike_spawning_with_lights():
    """Test EW bike spawning through traffic light cycles."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.world.intersection import Phase
        
        print("🚴 Testing EW bike spawning with traffic light cycles...")
        print()
        
        # Create app
        app = App()
        
        print("📍 EW Bike Configuration:")
        print(f"   EW bike paths available: {len(app.bikes_ew_right_px)} points in right path")
        print(f"   EW bike spawner interval: 6.0s ± 1.5s")
        print(f"   EW bike spawner max count: 25")
        
        # Check current traffic light state
        print()
        print("🚦 Current Traffic Light Status:")
        print(f"   Current phase: {app.ctrl.phase}")
        print(f"   EW ped light: {app.ctrl.ped_ew.state}")
        print(f"   Can EW bikes cross: {'YES' if app.ctrl.can_ped_cross_ew() else 'NO'}")
        
        # Test spawning in different phases
        print()
        print("🔄 Testing Through All Traffic Light Phases:")
        
        phases_tested = []
        bikes_spawned = 0
        total_attempts = 0
        
        for phase_num, phase in enumerate([Phase.NS_CARS_GREEN, Phase.EW_CARS_GREEN, 
                                          Phase.NS_PED_BIKE, Phase.EW_PED_BIKE]):
            
            # Force set the phase
            app.ctrl._enter_phase(phase)
            
            print(f"   Phase {phase_num + 1}: {phase.name}")
            print(f"     EW ped light: {app.ctrl.ped_ew.state}")
            print(f"     Can cross: {'YES' if app.ctrl.can_ped_cross_ew() else 'NO'}")
            
            # Test spawner during this phase
            initial_agents = len(app.agents)
            
            # Try spawning multiple times in this phase
            for attempt in range(3):
                total_attempts += 1
                
                # Force allow spawning by providing a lambda that always returns True
                new_agent = app.bike_ew_spawner.update(1.0, allow_spawn=lambda: True)
                
                if new_agent:
                    # Check if spawn position is safe
                    if app._is_safe_spawn_position(new_agent):
                        app.agents.append(new_agent)
                        bikes_spawned += 1
                        print(f"       Attempt {attempt + 1}: ✅ Bike spawned at {new_agent.pos}")
                    else:
                        print(f"       Attempt {attempt + 1}: ⚠️ Bike created but spawn unsafe")
                else:
                    print(f"       Attempt {attempt + 1}: ❌ No bike created")
            
            phases_tested.append((phase.name, app.ctrl.can_ped_cross_ew()))
        
        print()
        print("📊 Spawning Test Results:")
        print(f"   Total spawn attempts: {total_attempts}")
        print(f"   Bikes successfully spawned: {bikes_spawned}")
        print(f"   Success rate: {bikes_spawned/total_attempts*100:.1f}%")
        
        print()
        print("🚦 Phase Analysis:")
        for phase_name, can_cross in phases_tested:
            print(f"   {phase_name}: {'✅ Can cross' if can_cross else '❌ Cannot cross'}")
        
        # Test if EW_PED_BIKE phase allows crossing
        ew_ped_phase_works = phases_tested[3][1]  # EW_PED_BIKE is index 3
        
        if ew_ped_phase_works:
            print()
            print("✅ EW_PED_BIKE phase allows bike crossing!")
            print("   The issue might be timing - bikes only spawn during this phase.")
        else:
            print()
            print("❌ EW_PED_BIKE phase doesn't allow bike crossing!")
            print("   There's a configuration issue with traffic lights.")
        
        # Test current spawn safety
        print()
        print("🛡️ Spawn Safety Test:")
        
        # Reset to EW_PED_BIKE phase
        app.ctrl._enter_phase(Phase.EW_PED_BIKE)
        
        # Clear existing agents
        app.agents = []
        
        # Try creating an EW bike
        test_bike = app.bike_ew_spawner.factory()
        print(f"   Created EW bike at: {test_bike.pos}")
        
        # Test spawn safety
        is_safe = app._is_safe_spawn_position(test_bike)
        print(f"   Spawn position safe: {'YES' if is_safe else 'NO'}")
        
        if is_safe:
            app.agents.append(test_bike)
            print(f"   ✅ EW bike added to simulation!")
        else:
            print(f"   ❌ EW bike rejected by spawn safety")
        
        return bikes_spawned > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing EW bike spawning with traffic lights...")
    print("=" * 80)
    
    success = test_ew_bike_spawning_with_lights()
    
    print()
    print("=" * 80)
    if success:
        print("✅ EW bike spawning is working!")
        print("   Bikes should spawn from the left side during EW pedestrian phase.")
    else:
        print("❌ EW bike spawning has issues!")
        print("   Need to investigate traffic light timing or spawn safety.")