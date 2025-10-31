# src/traffic_sim/services/statistics.py
from typing import Dict, List, Optional
from datetime import datetime

class SimulationStats:
    """Tracks and analyzes traffic simulation statistics"""
    
    def __init__(self):
        self.vehicle_count = 0
        self.pedestrian_count = 0
        self.cyclist_count = 0
        self.collisions = 0
        self.average_wait_time = 0.0
        self.total_wait_time = 0.0
        self.vehicles_served = 0
        self.total_completed_time = 0.0
        # completions per type
        self.completions: Dict[str, int] = {}
        # spawned counts per type
        self.spawns: Dict[str, int] = {}
        self.start_time = datetime.now()
        
        # Detailed stats per type
        self.wait_times: Dict[str, List[float]] = {
            'car': [],
            'truck': [],
            'cyclist': [],
            'pedestrian': []
        }
        
        # Traffic flow stats
        self.flow_stats = {
            'north_south': {
                'vehicles_passed': 0,
                'avg_speed': 0.0
            },
            'east_west': {
                'vehicles_passed': 0,
                'avg_speed': 0.0
            }
        }
    
    def add_wait_time(self, actor_type: str, wait_time: float):
        """Record a wait time for a specific type of actor"""
        if actor_type in self.wait_times:
            self.wait_times[actor_type].append(wait_time)
            # Update overall average
            self.total_wait_time += wait_time
            self.vehicles_served += 1
            self.average_wait_time = self.total_wait_time / self.vehicles_served
    
    def record_passage(self, direction: str, speed: float):
        """Record when a vehicle passes through the intersection"""
        if direction in self.flow_stats:
            stats = self.flow_stats[direction]
            stats['vehicles_passed'] += 1
            # Update running average speed
            stats['avg_speed'] = (
                (stats['avg_speed'] * (stats['vehicles_passed'] - 1) + speed)
                / stats['vehicles_passed']
            )
    
    def record_collision(self):
        """Record a collision event"""
        self.collisions += 1

    def record_spawn(self, actor_type: str) -> None:
        """Record that an actor of given type was spawned into the simulation.

        This increments overall counters and per-type counters used by the
        UI / tests. The method is intentionally permissive about the
        actor_type string (case-insensitive).
        """
        t = (actor_type or "").lower()
        # increment per-type spawn counter
        self.spawns[t] = self.spawns.get(t, 0) + 1
        if t in ("car", "truck"):
            self.vehicle_count += 1
        if t == "truck":
            # trucks counted as vehicles too; keep vehicle_count as total
            pass
        elif t == "cyclist":
            self.cyclist_count += 1
        elif t in ("pedestrian", "ped"):
            self.pedestrian_count += 1
    
    def get_stats_summary(self) -> Dict[str, any]:
        """Get a summary of current statistics"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'runtime_seconds': runtime,
            'total_vehicles': self.vehicle_count,
            'total_pedestrians': self.pedestrian_count,
            'total_cyclists': self.cyclist_count,
            'collisions': self.collisions,
            'average_wait_time': self.average_wait_time,
            'vehicles_per_minute': (self.vehicles_served * 60) / runtime if runtime > 0 else 0,
            'flow_stats': self.flow_stats,
            'spawns': self.spawns,
            'wait_times_by_type': {
                actor_type: sum(times) / len(times) if times else 0
                for actor_type, times in self.wait_times.items()
            }
        }

    # Backwards-compatible alias expected by some callers
    def get_summary(self) -> Dict[str, any]:
        return self.get_stats_summary()

    def record_completion(self, actor_type: str, total_time: float = 0.0) -> None:
        """Record that an actor completed its journey (left the simulation).

        `total_time` is the time the actor spent in the simulation (seconds).
        """
        t = (actor_type or "").lower()
        self.completions[t] = self.completions.get(t, 0) + 1
        try:
            self.total_completed_time += float(total_time)
        except Exception:
            pass
        # Treat a completion as a served vehicle for throughput metrics
        self.vehicles_served += 1
    
    def render_stats_overlay(self, screen, font, pos=(10, 10), color=(255, 255, 255)):
        """Render statistics as an overlay on the simulation"""
        stats = self.get_stats_summary()
        lines = [
            f"Runtime: {stats['runtime_seconds']:.1f}s",
            f"Vehicles/min: {stats['vehicles_per_minute']:.1f}",
            f"Avg wait: {self.average_wait_time:.1f}s",
            f"Collisions: {self.collisions}",
            "",
            "Flow rates (vehicles/min):",
            f"N/S: {self.flow_stats['north_south']['vehicles_passed']}",
            f"E/W: {self.flow_stats['east_west']['vehicles_passed']}"
        ]
        
        y = pos[1]
        for line in lines:
            text = font.render(line, True, color)
            screen.blit(text, (pos[0], y))
            y += 20