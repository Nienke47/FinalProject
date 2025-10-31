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
        self.total_time = 0.0  # Track total time for statistics
        self.stopped_time = 0.0  # Track how long vehicle has been stopped

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

    def _check_collision_ahead(self, target_pos, safe_distance=60):
        """Check if there's another vehicle too close in front of us"""
        if not hasattr(self, 'all_agents') or not self.all_agents:
            return False
            
        current_x, current_y = self.pos
        target_x, target_y = target_pos
        
        # Calculate the direction we're moving
        move_dx = target_x - current_x
        move_dy = target_y - current_y
        move_dist = math.hypot(move_dx, move_dy)
        
        if move_dist == 0:
            return False
            
        # Normalize movement direction
        move_nx = move_dx / move_dist
        move_ny = move_dy / move_dist
        
        # Optimization: Only check nearby agents to reduce lag
        max_check_distance = safe_distance * 3  # Increased search range
        nearby_agents = []
        
        # First pass: collect only nearby agents
        for other in self.all_agents:
            if other is self or getattr(other, 'done', False):
                continue
                
            other_x, other_y = other.pos
            # Quick distance check using squared distance (faster than hypot)
            dx_sq = (other_x - current_x) ** 2
            dy_sq = (other_y - current_y) ** 2
            
            if dx_sq + dy_sq <= max_check_distance ** 2:
                nearby_agents.append(other)
        
        # Second pass: detailed check only for nearby agents
        for other in nearby_agents:
            other_x, other_y = other.pos
            
            # Check distance to other vehicle at current position
            current_dist = math.hypot(other_x - current_x, other_y - current_y)
            
            # Check distance to other vehicle at target position
            target_dist = math.hypot(other_x - target_x, other_y - target_y)
            
            # If either distance is too close, prevent movement
            if current_dist < safe_distance or target_dist < safe_distance:
                # Additional check: are we moving towards each other?
                to_other_x = other_x - current_x
                to_other_y = other_y - current_y
                
                # Dot product to see if other vehicle is in our movement direction
                dot_product = (to_other_x * move_nx + to_other_y * move_ny)
                
                # If we're moving towards the other vehicle or very close, block movement
                if dot_product > 0 or current_dist < safe_distance * 0.8:
                    return True
                
        return False

    def _check_any_collision(self, position, collision_radius=None):
        """
        Strict collision check - prevents any overlap with other vehicles.
        Returns True if there would be a collision at the given position.
        """
        if not hasattr(self, 'all_agents') or not self.all_agents:
            return False
        
        if collision_radius is None:
            # Get vehicle size for collision radius
            if hasattr(self, 'width') and hasattr(self, 'length'):
                collision_radius = max(getattr(self, 'width', 50), getattr(self, 'length', 80)) * 0.7
            else:
                collision_radius = 25  # Default for pedestrians/cyclists
        
        pos_x, pos_y = position
        
        for other in self.all_agents:
            if other is self or getattr(other, 'done', False):
                continue
            
            other_x, other_y = other.pos
            distance = math.hypot(other_x - pos_x, other_y - pos_y)
            
            # Get other vehicle's collision radius
            if hasattr(other, 'width') and hasattr(other, 'length'):
                other_radius = max(getattr(other, 'width', 50), getattr(other, 'length', 80)) * 0.7
            else:
                other_radius = 25
            
            # Check if collision would occur
            min_safe_distance = collision_radius + other_radius + 10  # Extra 10px safety margin
            
            if distance < min_safe_distance:
                return True
        
        return False

    def _calculate_following_speed_adjustment(self) -> float:
        """
        Calculate speed adjustment based on vehicle ahead to maintain proper spacing.
        Returns a speed factor between 0.0 and 1.0
        """
        if not hasattr(self, 'all_agents') or not self.all_agents:
            return 1.0
        
        # Import here to avoid circular imports
        try:
            from ...services.physics import find_vehicle_ahead, calculate_safe_following_speed
        except ImportError:
            from traffic_sim.services.physics import find_vehicle_ahead, calculate_safe_following_speed
        
        # Import config
        try:
            from ...configuration import Config
        except ImportError:
            from traffic_sim.configuration import Config
        
        config = Config()
        
        # Find vehicle ahead on same path
        result = find_vehicle_ahead(self, self.all_agents)
        
        if result is None:
            return 1.0  # No vehicle ahead, go full speed
        
        vehicle_ahead, distance_to_ahead = result
        
        # Calculate different following distances based on vehicle type
        if hasattr(self, 'width') and hasattr(self, 'length'):
            # For cars and trucks, base following distance on vehicle size
            vehicle_size = max(getattr(self, 'width', 50), getattr(self, 'length', 80))
            desired_distance = vehicle_size * config.VEHICLE_SPACING["FOLLOWING_DISTANCE_MULTIPLIER"]
        else:
            # For pedestrians and cyclists, use minimum following distance
            desired_distance = config.VEHICLE_SPACING["MIN_FOLLOWING_DISTANCE"]
        
        # Ensure minimum following distance
        desired_distance = max(desired_distance, config.VEHICLE_SPACING["MIN_FOLLOWING_DISTANCE"])
        
        return calculate_safe_following_speed(
            self, vehicle_ahead, distance_to_ahead, desired_distance
        )

    def update(self, dt: float):
        if self.done:
            return
        
        # Track total simulation time for this vehicle
        self.total_time += dt
        
        # Store initial position to check if vehicle moved
        initial_pos = self.pos.copy()

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
            # Calculate speed adjustment based on vehicle ahead
            speed_factor = self._calculate_following_speed_adjustment()
            
            # Calculate new position with adjusted speed
            adjusted_speed = self.speed * speed_factor
            vx = (dx / dist) * adjusted_speed
            vy = (dy / dist) * adjusted_speed
            new_pos = [self.pos[0] + vx * dt, self.pos[1] + vy * dt]
            
            # Get config for safety distances
            try:
                from ...configuration import Config
            except ImportError:
                from traffic_sim.configuration import Config
            
            config = Config()
            emergency_distance = config.VEHICLE_SPACING["EMERGENCY_STOP_DISTANCE"]
            
            # Multi-layer collision prevention:
            # 1. Check strict collision (vehicle overlap)
            # 2. Check emergency stopping distance
            # 3. Check directional collision ahead
            
            can_move = True
            
            # Layer 1: Strict collision check - absolutely no overlap
            if self._check_any_collision(new_pos):
                can_move = False
            
            # Layer 2: Emergency stopping distance check
            elif self._check_collision_ahead(new_pos, safe_distance=emergency_distance):
                can_move = False
            
            # Layer 3: Additional safety check with larger distance for high-speed vehicles
            elif adjusted_speed > 100:  # For fast-moving vehicles, use larger safety margin
                if self._check_collision_ahead(new_pos, safe_distance=emergency_distance * 1.5):
                    can_move = False
            
            # Only move if all collision checks pass
            if can_move:
                self.pos[0] = new_pos[0]
                self.pos[1] = new_pos[1]
                self.stopped_time = 0.0  # Reset stopped time when moving
            else:
                # Vehicle is stopped due to collision prevention
                self.stopped_time += dt
        
        # Check if vehicle actually moved this frame
        moved_distance = math.hypot(self.pos[0] - initial_pos[0], self.pos[1] - initial_pos[1])
        if moved_distance < 1.0:  # Less than 1 pixel movement counts as stopped
            self.stopped_time += dt
        else:
            self.stopped_time = 0.0
