# src/traffic_sim/services/physics.py
import math
from typing import List, Optional, Tuple
from ..domain.actors.road_users import RoadUser

# Safe imports for configuration
try:
    from ..configuration import Config
except ImportError:
    from traffic_sim.configuration import Config

config = Config()

def distance(a: RoadUser, b: RoadUser) -> float:
    dx = a.pos[0] - b.pos[0]
    dy = a.pos[1] - b.pos[1]
    return math.hypot(dx, dy)

def check_collisions(agents: List[RoadUser], min_dist: float = 15.0):
    """
    Simpele check die True teruggeeft als twee agents te dicht bij elkaar komen.
    """
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            if distance(agents[i], agents[j]) < min_dist:
                return True
    return False

def find_vehicle_ahead(current_vehicle: RoadUser, all_vehicles: List[RoadUser], 
                      search_distance: float = None) -> Optional[Tuple[RoadUser, float]]:
    """
    Find the nearest vehicle ahead of the current vehicle on the same path.
    
    Returns:
        Tuple of (vehicle_ahead, distance_to_vehicle) or None if no vehicle found
    """
    if search_distance is None:
        # Get vehicle-specific search distance
        if hasattr(current_vehicle, 'get_collision_settings'):
            vehicle_settings = current_vehicle.get_collision_settings()
            search_distance = vehicle_settings["SEARCH_DISTANCE"]
        else:
            # Fallback to default settings
            search_distance = config.VEHICLE_SPACING["DEFAULT"]["SEARCH_DISTANCE"]
    
    if not hasattr(current_vehicle, 'path') or len(current_vehicle.path) < 2:
        return None
    
    # Get current position and direction
    current_pos = current_vehicle.pos
    current_path_idx = getattr(current_vehicle, 'i', 0)
    
    # Calculate direction vector from current movement
    if current_path_idx < len(current_vehicle.path) - 1:
        next_waypoint = current_vehicle.path[current_path_idx + 1]
        direction_x = next_waypoint[0] - current_pos[0]
        direction_y = next_waypoint[1] - current_pos[1]
        direction_length = math.hypot(direction_x, direction_y)
        
        if direction_length == 0:
            return None
        
        # Normalize direction vector
        dir_nx = direction_x / direction_length
        dir_ny = direction_y / direction_length
    else:
        return None
    
    closest_vehicle = None
    closest_distance = float('inf')
    
    for other_vehicle in all_vehicles:
        if (other_vehicle is current_vehicle or 
            getattr(other_vehicle, 'done', False) or
            not hasattr(other_vehicle, 'path')):
            continue
        
        # Quick distance filter
        other_pos = other_vehicle.pos
        quick_distance = math.hypot(other_pos[0] - current_pos[0], 
                                  other_pos[1] - current_pos[1])
        
        if quick_distance > search_distance:
            continue
        
        # Check if the other vehicle is on a similar path (same starting point within tolerance)
        if (len(other_vehicle.path) > 0 and len(current_vehicle.path) > 0):
            start_distance = math.hypot(
                other_vehicle.path[0][0] - current_vehicle.path[0][0],
                other_vehicle.path[0][1] - current_vehicle.path[0][1]
            )
            # Only consider vehicles on the same or very similar path
            if start_distance > 50:  # 50 pixel tolerance for same path
                continue
        
        # Check if other vehicle is ahead in our direction of travel
        to_other_x = other_pos[0] - current_pos[0]
        to_other_y = other_pos[1] - current_pos[1]
        
        # Dot product with our direction to see if it's ahead
        dot_product = to_other_x * dir_nx + to_other_y * dir_ny
        
        if dot_product > 0 and quick_distance < closest_distance:
            closest_vehicle = other_vehicle
            closest_distance = quick_distance
    
    return (closest_vehicle, closest_distance) if closest_vehicle else None

def calculate_safe_following_speed(current_vehicle: RoadUser, vehicle_ahead: RoadUser, 
                                 distance_to_ahead: float, desired_following_distance: float = None) -> float:
    """
    Calculate a safe speed - BINARY APPROACH: Full speed or complete stop.
    No gradual slowing down, vehicles either drive normally or stop at reasonable distance.
    
    Args:
        current_vehicle: The vehicle that needs to adjust speed
        vehicle_ahead: The vehicle being followed
        distance_to_ahead: Current distance to the vehicle ahead
        desired_following_distance: Target following distance in pixels
    
    Returns:
        Adjusted speed factor: 1.0 (full speed) or 0.0 (complete stop)
    """
    if desired_following_distance is None:
        # Get vehicle-specific minimum following distance
        if hasattr(current_vehicle, 'get_collision_settings'):
            vehicle_settings = current_vehicle.get_collision_settings()
            desired_following_distance = vehicle_settings["MIN_FOLLOWING_DISTANCE"]
        else:
            # Fallback to default settings
            desired_following_distance = config.VEHICLE_SPACING["DEFAULT"]["MIN_FOLLOWING_DISTANCE"]
    
    # BINARY DECISION: Either full speed or complete stop
    # Stop if we're at or below the desired following distance
    if distance_to_ahead <= desired_following_distance:
        return 0.0  # COMPLETE STOP - maintain reasonable distance
    
    # Go full speed if we have sufficient distance
    return 1.0  # FULL SPEED - no gradual slowing
