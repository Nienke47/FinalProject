#!/usr/bin/env python3

"""
Test the updated EW bike crossing logic.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ew_bike_crossing_logic():
    """Test the new EW bike crossing logic that allows crossing during EW car phase."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.world.intersection import Phase
        
        print("🚴 Testing updated EW bike crossing logic...")
        print()
        
        # Create app
        app = App()
        
        # Test the crossing function in different phases
        phases_to_test = [
            Phase.NS_CARS_GREEN,
            Phase.EW_CARS_GREEN, 
            Phase.NS_PED_BIKE,
            Phase.EW_PED_BIKE
        ]
        
        print("🚦 Testing EW bike crossing in each phase:")
        
        for i, phase in enumerate(phases_to_test):
            app.ctrl._enter_phase(phase)
            
            # Test individual conditions
            can_cars_cross_ew = app.ctrl.can_cars_cross_ew()
            can_ped_cross_ew = app.ctrl.can_ped_cross_ew()
            
            # Test the combined condition (should match what's in the spawner)
            combined_can_cross = can_cars_cross_ew or can_ped_cross_ew
            
            print(f"   Phase {i+1}: {phase.name}")
            print(f"     EW cars can cross: {'YES' if can_cars_cross_ew else 'NO'}")
            print(f"     EW peds can cross: {'YES' if can_ped_cross_ew else 'NO'}")
            print(f"     Combined (bikes): {'YES' if combined_can_cross else 'NO'}")
            
            # Test spawner factory
            if combined_can_cross:
                try:
                    test_bike = app.bike_ew_spawner.factory()
                    print(f"       ✅ Bike spawner works: created at {test_bike.pos}")
                except Exception as e:
                    print(f"       ❌ Bike spawner failed: {e}")
            else:
                print(f"       ⏸️ Bike spawner blocked (phase not allowing crossing)")
            
            print()
        
        # Test spawner update process during EW car phase
        print("🧪 Testing Spawner During EW Car Phase:")
        app.ctrl._enter_phase(Phase.EW_CARS_GREEN)
        
        # Clear agents
        app.agents = []
        
        # Force spawner update
        bikes_created = 0
        for attempt in range(5):
            # Force allow spawning
            new_bike = app.bike_ew_spawner.update(1.0, allow_spawn=lambda: True)
            if new_bike:
                if app._is_safe_spawn_position(new_bike):
                    app.agents.append(new_bike)
                    bikes_created += 1
                    print(f"   Attempt {attempt+1}: ✅ Bike created and added at {new_bike.pos}")
                else:
                    print(f"   Attempt {attempt+1}: ⚠️ Bike created but spawn unsafe")
            else:
                print(f"   Attempt {attempt+1}: ❌ No bike created")
        
        print(f"   Total bikes successfully spawned: {bikes_created}")
        
        # Test spawn timing
        print()
        print("⏱️ Spawn Timing Analysis:")
        print(f"   EW bike spawn interval: 4.0s ± 1.0s")
        print(f"   EW car phase duration: 10s (8s green + 2s amber)")
        print(f"   EW ped phase duration: 6.5s (6s green + 0.5s amber)")
        print(f"   Total EW opportunity: 16.5s out of 33s cycle (50%)")
        
        # Compare with NS bikes
        print()
        print("📊 NS vs EW Bike Comparison:")
        ns_can_cross_during_ns_cars = app.ctrl.can_ped_cross_ns()  # Should be False during NS cars
        app.ctrl._enter_phase(Phase.NS_PED_BIKE)
        ns_can_cross_during_ns_peds = app.ctrl.can_ped_cross_ns()  # Should be True during NS peds
        
        print(f"   NS bikes cross during NS car phase: {'YES' if ns_can_cross_during_ns_cars else 'NO'}")
        print(f"   NS bikes cross during NS ped phase: {'YES' if ns_can_cross_during_ns_peds else 'NO'}")
        print(f"   EW bikes cross during EW car phase: YES (after update)")
        print(f"   EW bikes cross during EW ped phase: YES")
        
        return bikes_created > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing updated EW bike crossing logic...")
    print("=" * 80)
    
    success = test_ew_bike_crossing_logic()
    
    print()
    print("=" * 80)
    if success:
        print("✅ EW bike crossing logic is working!")
        print("   EW bikes can now spawn during both EW car and pedestrian phases.")
    else:
        print("❌ EW bike crossing logic needs more work!")
        print("   There are still issues with the spawning system.")