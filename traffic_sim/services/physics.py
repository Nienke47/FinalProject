# src/traffic_sim/services/physics.py
import math
import pygame
from typing import List, Optional, Tuple
from ..domain.actors.road_users import RoadUser

# Safe imports for configuration
try:
    from ..configuration import Config
except ImportError:
    from traffic_sim.configuration import Config

config = Config()

def get_collision_rect(vehicle: RoadUser):
    """
    Get the collision rectangle for a vehicle.
    For rotated rectangles, this returns the axis-aligned bounding box.
    Use get_rotated_collision_points() for precise rotated collision detection.
    """
    # Get collision radius for this vehicle type
    vehicle_type = type(vehicle).__name__.upper()
    collision_radius = config.COLLISION_RADIUS.get(vehicle_type, 25)
    
    # Convert radius to rectangle dimensions (narrower width, longer height)
    rect_width = collision_radius * 1.4   # Narrower: 1.4x instead of 2x
    rect_height = collision_radius * 4.0  # Longer: 2.6x instead of 2x
    
    # Create rectangle centered at vehicle position
    rect_x = vehicle.pos[0] - rect_width / 2
    rect_y = vehicle.pos[1] - rect_height / 2
    
    return pygame.Rect(rect_x, rect_y, rect_width, rect_height)

def get_rotated_collision_points(vehicle: RoadUser):
    """
    Get the four corner points of the rotated collision rectangle.
    Returns list of (x, y) tuples representing the corners.
    """
    # Get collision radius for this vehicle type
    vehicle_type = type(vehicle).__name__.upper()
    collision_radius = config.COLLISION_RADIUS.get(vehicle_type, 25)
    
    # Convert radius to rectangle dimensions (narrower width, longer height)
    half_width = (collision_radius * 1.4) / 2   # Half width
    half_height = (collision_radius * 4.0) / 2  # Half height
    
    # Get vehicle rotation angle
    if hasattr(vehicle, 'get_rotation'):
        angle_deg = vehicle.get_rotation()
        angle_rad = math.radians(-angle_deg)  # Negative because pygame uses clockwise rotation
    else:
        angle_rad = 0
    
    # Calculate rotated corner points relative to vehicle center
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Original rectangle corners (relative to center)
    corners = [
        (-half_width, -half_height),  # Top-left
        (half_width, -half_height),   # Top-right
        (half_width, half_height),    # Bottom-right
        (-half_width, half_height)    # Bottom-left
    ]
    
    # Rotate and translate to world coordinates
    rotated_corners = []
    for x, y in corners:
        # Rotate the point
        rotated_x = x * cos_a - y * sin_a
        rotated_y = x * sin_a + y * cos_a
        # Translate to vehicle position
        world_x = vehicle.pos[0] + rotated_x
        world_y = vehicle.pos[1] + rotated_y
        rotated_corners.append((world_x, world_y))
    
    return rotated_corners

def rotated_rectangles_collide(vehicle_a: RoadUser, vehicle_b: RoadUser) -> bool:
    """
    Check if two vehicles' rotated collision rectangles overlap using Separating Axis Theorem (SAT).
    Returns True if they collide.
    """
    # Get the corner points of both rectangles
    points_a = get_rotated_collision_points(vehicle_a)
    points_b = get_rotated_collision_points(vehicle_b)
    
    # Get the axes to test (perpendicular to each edge)
    def get_axes(points):
        axes = []
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            # Edge vector
            edge_x = p2[0] - p1[0]
            edge_y = p2[1] - p1[1]
            # Perpendicular (normal) vector
            normal_x = -edge_y
            normal_y = edge_x
            # Normalize
            length = math.hypot(normal_x, normal_y)
            if length > 0:
                axes.append((normal_x / length, normal_y / length))
        return axes
    
    axes = get_axes(points_a) + get_axes(points_b)
    
    # Test separation on each axis
    for axis_x, axis_y in axes:
        # Project both rectangles onto the axis
        def project_points(points, axis_x, axis_y):
            projections = []
            for px, py in points:
                projection = px * axis_x + py * axis_y
                projections.append(projection)
            return min(projections), max(projections)
        
        min_a, max_a = project_points(points_a, axis_x, axis_y)
        min_b, max_b = project_points(points_b, axis_x, axis_y)
        
        # Check if projections overlap
        if max_a < min_b or max_b < min_a:
            return False  # Separating axis found, no collision
    
    return True  # No separating axis found, collision detected

def rectangles_collide(vehicle_a: RoadUser, vehicle_b: RoadUser) -> bool:
    """
    Check if two vehicles' collision rectangles overlap.
    Uses rotated rectangle collision detection.
    Returns True if they collide.
    """
    return rotated_rectangles_collide(vehicle_a, vehicle_b)

def distance(a: RoadUser, b: RoadUser) -> float:
    """
    Calculate center-to-center distance between two vehicles.
    Still used for some calculations even with rectangular collision.
    """
    dx = a.pos[0] - b.pos[0]
    dy = a.pos[1] - b.pos[1]
    return math.hypot(dx, dy)

def check_collisions(agents: List[RoadUser], min_dist: float = 15.0):
    """
    Check if any two agents have colliding rectangles.
    Uses rectangular collision detection instead of circular distance.
    """
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            if rectangles_collide(agents[i], agents[j]):
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
            
            # Cars should be more selective about cyclists - only stop if very close paths
            current_vehicle_type = type(current_vehicle).__name__
            other_vehicle_type = type(other_vehicle).__name__
            
            if current_vehicle_type == "Car" and other_vehicle_type == "Cyclist":
                # Cars only stop for cyclists if they're on nearly identical paths (very strict)
                if start_distance > 20:  # Much stricter tolerance for car-cyclist interactions
                    continue
            else:
                # Normal tolerance for other vehicle combinations
                if start_distance > 50:  # 50 pixel tolerance for same path
                    continue
        
        # Check if other vehicle is ahead in our direction of travel
        to_other_x = other_pos[0] - current_pos[0]
        to_other_y = other_pos[1] - current_pos[1]
        
        # Dot product with our direction to see if it's ahead
        dot_product = to_other_x * dir_nx + to_other_y * dir_ny
        
        # Special handling for trucks - directional collision detection
        if current_vehicle_type == "Truck":
            # Calculate cross product to determine if other vehicle is to the side
            cross_product = to_other_x * dir_ny - to_other_y * dir_nx
            side_distance = abs(cross_product)  # Perpendicular distance from truck's path
            
            # For trucks: be more lenient with side vehicles (especially cyclists)
            if other_vehicle_type == "Cyclist" and side_distance > 15:  # If cyclist is >15px to the side, ignore
                continue
            elif side_distance > 25:  # For other vehicles, ignore if >25px to the side
                continue
            
            # For forward detection, trucks should be more sensitive to avoid rear-ending
            if dot_product > 0:
                # Increase effective search distance for vehicles directly ahead
                if side_distance < 15:  # Vehicle is directly in front (increased from 10px to 15px)
                    effective_search_distance = search_distance * 2.0  # 100% longer forward detection (increased from 1.5x to 2.0x)
                    if quick_distance > effective_search_distance:
                        continue
                
                if quick_distance < closest_distance:
                    closest_vehicle = other_vehicle
                    closest_distance = quick_distance
        else:
            # Normal collision detection for non-trucks
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
