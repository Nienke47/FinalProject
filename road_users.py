from typing import List, Tuple, Callable, Optional
import math

Vec2 = Tuple[float, float]

class RoadUser:
    def __init__(self, path_px: List[Vec2], speed_px_s: float, can_cross_ok: Callable[[], bool]):
        self.path = path_px
        self.i = 0
        self.pos = list(path_px[0]) if path_px else [0.0, 0.0]
        self.speed = speed_px_s
        self.radius = 10
        self.done = False
        self._can_cross = can_cross_ok
        # kruispunt-regel: index van punt dicht bij de kruising waar we moeten kunnen oversteken
        self.cross_index: Optional[int] = self._guess_cross_index()
        self.last_rotation = 0.0  # in graden, voor tekenwerk e.d.

    def get_rotation(self) -> float:
        """Calculate the angle in degrees the actor should face based on movement direction."""
        # If we're in exit mode (past last waypoint), use exit direction
        if hasattr(self, '_exit_direction') and self._exit_direction:
            dx, dy = self._exit_direction
            angle = math.degrees(math.atan2(-dy, dx)) - 90
            self.last_rotation = angle
            return angle
            
        if len(self.path) <= self.i + 1:
            return self.last_rotation
            
        # Calculate angle from current position to next path point
        current = self.pos
        next_point = self.path[self.i + 1]
        dx = next_point[0] - current[0]
        dy = next_point[1] - current[1]
        
        # Skip tiny movements to prevent jittering
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            return self.last_rotation
            
        # Calculate angle: atan2(dy, dx) gives angle from x-axis
        # Convert to degrees, adjust for pygame's coordinate system
        angle = math.degrees(math.atan2(-dy, dx)) - 90
        
        self.last_rotation = angle
        return angle

    def _guess_cross_index(self) -> Optional[int]:
        """Find the waypoint just before the intersection (stop line)"""
        if len(self.path) < 3: 
            return None
        
        # The stop line should be at waypoint index 1 (second point in path)
        # This is typically positioned just before the intersection
        # Cars will wait at this point when approaching if the light is red
        return 1

    def update(self, dt: float):
        if self.done:
            return

        # Voor de "kruispunt" drempel: check stoplicht via callback
        # Check if we're approaching or at the stop line waypoint
        if self.cross_index is not None and self.i <= self.cross_index:
            # If we're before the stop line, check if we should stop
            if not self._can_cross():
                # If we're at the stop line waypoint itself, don't move forward
                if self.i == self.cross_index:
                    return  # wachten voor rood
                # If we're approaching the stop line, stop when we get close
                elif self.i == self.cross_index - 1:
                    if self.i + 1 < len(self.path):
                        target = self.path[self.i + 1]  # This is the stop line waypoint
                        dx = target[0] - self.pos[0]
                        dy = target[1] - self.pos[1]
                        dist = math.hypot(dx, dy)
                        # Stop if we're within 15 pixels of the stop line
                        if dist < 5:
                            return  # wachten voor rood

        # Check if we've gone past all waypoints
        if self.i >= len(self.path) - 1:
            # We're at or past the last waypoint - keep moving in the exit direction
            if hasattr(self, '_exit_direction') and self._exit_direction:
                dx, dy = self._exit_direction
                self.pos[0] += dx * self.speed * dt
                self.pos[1] += dy * self.speed * dt
                # Track distance traveled past last waypoint
                if not hasattr(self, '_exit_distance'):
                    self._exit_distance = 0.0
                self._exit_distance += self.speed * dt
                # Despawn after traveling far enough
                if self._exit_distance > 100:  # 100 pixels past last waypoint
                    self.done = True
            else:
                # No exit direction set, mark as done
                self.done = True
            return

        # Get target (next waypoint)
        target = self.path[self.i + 1]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        
        # Check if we've reached this waypoint
        if dist < 5:
            # Move to next waypoint
            self.i += 1
            
            # If this was the second-to-last waypoint, calculate exit direction
            if self.i == len(self.path) - 1:
                # We just reached the last waypoint - calculate exit direction
                if len(self.path) >= 2:
                    last = self.path[-1]
                    second_last = self.path[-2]
                    dx_exit = last[0] - second_last[0]
                    dy_exit = last[1] - second_last[1]
                    dist_exit = math.hypot(dx_exit, dy_exit)
                    if dist_exit > 0:
                        self._exit_direction = (dx_exit / dist_exit, dy_exit / dist_exit)
                        self._exit_distance = 0.0
            
            # Continue moving this frame - recalculate target if not at end
            if self.i < len(self.path) - 1:
                target = self.path[self.i + 1]
                dx = target[0] - self.pos[0]
                dy = target[1] - self.pos[1]
                dist = math.hypot(dx, dy)
            else:
                # We're now at the last waypoint, continue in exit direction
                return

        # Move towards target
        if dist > 0:
            vx = (dx / dist) * self.speed
            vy = (dy / dist) * self.speed
            self.pos[0] += vx * dt
            self.pos[1] += vy * dt
