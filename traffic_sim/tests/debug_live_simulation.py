#!/usr/bin/env python3

"""
Debug why EW bikes aren't appearing in the actual simulation.
"""

import sys
from pathlib import Path
import time

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_live_simulation():
    """Debug EW bike spawning in a live simulation."""
    try:
        from traffic_sim.core.testapp import App
        from traffic_sim.domain.world.intersection import Phase
        import pygame as pg
        
        print("🔍 Debugging live EW bike spawning simulation...")
        print()
        
        # Create app
        app = App()
        
        # Initialize display (needed for full simulation)
        pg.init()
        screen = pg.display.set_mode((1024, 768))
        clock = pg.time.Clock()
        
        print("📍 Initial State:")
        print(f"   Total agents: {len(app.agents)}")
        print(f"   Current phase: {app.ctrl.phase}")
        
        # Run simulation for a few cycles and track bike spawning
        total_time = 0
        ew_bikes_spawned = 0
        ns_bikes_spawned = 0
        phase_changes = []
        spawn_events = []
        
        print()
        print("🕐 Running simulation for 60 seconds...")
        
        for frame in range(3600):  # 60 seconds at 60 FPS
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            total_time += dt
            
            # Track phase changes
            current_phase = app.ctrl.phase
            if not phase_changes or phase_changes[-1][1] != current_phase:
                phase_changes.append((total_time, current_phase))
                print(f"   {total_time:.1f}s: Phase changed to {current_phase.name}")
            
            # Count agents before update
            agents_before = len(app.agents)
            ew_bikes_before = sum(1 for a in app.agents if hasattr(a, 'path') and a.path and abs(a.path[0][0] + 102) < 50)
            ns_bikes_before = sum(1 for a in app.agents if hasattr(a, 'path') and a.path and abs(a.path[0][1] - 844) < 50)
            
            # Update simulation
            app.update(dt)
            
            # Count agents after update
            agents_after = len(app.agents)
            ew_bikes_after = sum(1 for a in app.agents if hasattr(a, 'path') and a.path and abs(a.path[0][0] + 102) < 50)
            ns_bikes_after = sum(1 for a in app.agents if hasattr(a, 'path') and a.path and abs(a.path[0][1] - 844) < 50)
            
            # Check for new bikes
            if ew_bikes_after > ew_bikes_before:
                ew_bikes_spawned += (ew_bikes_after - ew_bikes_before)
                spawn_events.append((total_time, 'EW_BIKE', current_phase))
                print(f"   {total_time:.1f}s: ✅ EW bike spawned! (Total EW: {ew_bikes_after})")
                
            if ns_bikes_after > ns_bikes_before:
                ns_bikes_spawned += (ns_bikes_after - ns_bikes_before)
                spawn_events.append((total_time, 'NS_BIKE', current_phase))
                print(f"   {total_time:.1f}s: ✅ NS bike spawned! (Total NS: {ns_bikes_after})")
            
            # Check for events (quit simulation early if needed)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    break
            
            # Stop after 60 seconds
            if total_time >= 60.0:
                break
        
        print()
        print("📊 Simulation Results:")
        print(f"   Total simulation time: {total_time:.1f}s")
        print(f"   EW bikes spawned: {ew_bikes_spawned}")
        print(f"   NS bikes spawned: {ns_bikes_spawned}")
        print(f"   Total phase changes: {len(phase_changes)}")
        
        print()
        print("🚦 Phase Distribution:")
        phase_durations = {}
        for i in range(len(phase_changes)):
            phase_name = phase_changes[i][1].name
            if i < len(phase_changes) - 1:
                duration = phase_changes[i+1][0] - phase_changes[i][0]
            else:
                duration = total_time - phase_changes[i][0]
            
            if phase_name not in phase_durations:
                phase_durations[phase_name] = 0
            phase_durations[phase_name] += duration
        
        for phase_name, duration in phase_durations.items():
            percentage = (duration / total_time) * 100
            print(f"   {phase_name}: {duration:.1f}s ({percentage:.1f}%)")
        
        print()
        print("🎯 Spawn Analysis:")
        if ew_bikes_spawned > 0:
            print(f"   ✅ EW bikes ARE spawning!")
            print(f"   Rate: {ew_bikes_spawned / total_time * 60:.1f} bikes per minute")
        else:
            print(f"   ❌ NO EW bikes spawned!")
            
        if ns_bikes_spawned > 0:
            print(f"   ✅ NS bikes ARE spawning!")
            print(f"   Rate: {ns_bikes_spawned / total_time * 60:.1f} bikes per minute")
        else:
            print(f"   ❌ NO NS bikes spawned!")
        
        # Analyze spawn events by phase
        print()
        print("📈 Spawn Events by Phase:")
        spawn_by_phase = {}
        for time_s, vehicle_type, phase in spawn_events:
            phase_name = phase.name
            if phase_name not in spawn_by_phase:
                spawn_by_phase[phase_name] = {'EW_BIKE': 0, 'NS_BIKE': 0}
            spawn_by_phase[phase_name][vehicle_type] += 1
        
        for phase_name, counts in spawn_by_phase.items():
            print(f"   {phase_name}: EW={counts['EW_BIKE']}, NS={counts['NS_BIKE']}")
        
        # Check spawner intervals
        print()
        print("⏱️ Spawner Configuration Check:")
        print(f"   EW bike spawner interval: {app.bike_ew_spawner.interval_s}s ± {app.bike_ew_spawner.random_offset}s")
        print(f"   NS bike spawner interval: {app.bike_ns_spawner.interval_s}s ± {app.bike_ns_spawner.random_offset}s")
        print(f"   EW bike max count: {app.bike_ew_spawner.max_count}")
        print(f"   NS bike max count: {app.bike_ns_spawner.max_count}")
        
        pg.quit()
        
        return ew_bikes_spawned > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Live simulation debugging for EW bikes...")
    print("=" * 80)
    
    success = debug_live_simulation()
    
    print()
    print("=" * 80)
    if success:
        print("✅ EW bikes are spawning in the simulation!")
    else:
        print("❌ EW bikes are NOT spawning in the simulation!")
        print("   Need to investigate further...")