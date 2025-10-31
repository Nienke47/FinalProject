
class Config:

    # Window settings
    WIDTH = 1024
    HEIGHT = 768
    TITLE = "Traffic Simulation"
    FPS = 60

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    BACKGROUND = (220, 220, 220)

    # Traffic light timings (seconds)
    TRAFFIC_LIGHT_TIMINGS = {
        "GREEN": 10.0,
        "YELLOW": 3.0,
        "RED": 10.0
    }

    # Actor speeds (pixels per second)
    SPEEDS = {
        "CAR": 120.0,
        "TRUCK": 80.0,
        "CYCLIST": 60.0,
        "PEDESTRIAN": 40.0,
        "BOAT": 50.0
    }

    # Collision detection
    COLLISION_RADIUS = {
        "CAR": 20,
        "TRUCK": 10,
        "CYCLIST":5,
        "PEDESTRIAN": 2,
        "BOAT": 5
    }

    # Path settings
    INTERSECTION_POINT = (WIDTH // 2, HEIGHT // 2)
    ROAD_WIDTH = 60

    # Vehicle-specific spacing settings - each vehicle type has its own collision behavior
    VEHICLE_SPACING = {
        "CAR": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 1.5,  # Cars maintain moderate following distance
            "MIN_FOLLOWING_DISTANCE": 50.0,        # Minimum distance for cars
            "SEARCH_DISTANCE": 150.0,              # How far ahead cars look
            "EMERGENCY_STOP_DISTANCE": 30.0,       # Emergency braking distance for cars
        },
        "TRUCK": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 2.0,  # Trucks need more space due to size
            "MIN_FOLLOWING_DISTANCE": 80.0,        # Larger minimum distance for trucks
            "SEARCH_DISTANCE": 200.0,              # Trucks look further ahead
            "EMERGENCY_STOP_DISTANCE": 50.0,       # Longer braking distance for trucks
        },
        "CYCLIST": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 1.0,  # Cyclists can follow closer
            "MIN_FOLLOWING_DISTANCE": 30.0,        # Smaller minimum distance
            "SEARCH_DISTANCE": 100.0,              # Shorter look-ahead distance
            "EMERGENCY_STOP_DISTANCE": 20.0,       # Quick stopping for cyclists
        },
        "PEDESTRIAN": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 0.8,  # Pedestrians can get very close
            "MIN_FOLLOWING_DISTANCE": 20.0,        # Very small minimum distance
            "SEARCH_DISTANCE": 80.0,               # Short look-ahead
            "EMERGENCY_STOP_DISTANCE": 15.0,       # Immediate stopping capability
        },
        # Global fallback settings for unknown vehicle types
        "DEFAULT": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 1.5,
            "MIN_FOLLOWING_DISTANCE": 60.0,
            "SEARCH_DISTANCE": 150.0,
            "EMERGENCY_STOP_DISTANCE": 25.0,
        }
    }

    # Frame boundary settings for vehicle despawning
    FRAME_BOUNDARY = {
        "DESPAWN_BUFFER": 50,                   # Extra pixels outside frame before despawning
        "ENABLE_FRAME_DESPAWN": True,           # Enable automatic despawning when leaving frame
    }

    # Debug settings
    DEBUG_MODE = False
    SHOW_PATHS = False
    SHOW_COLLISION_CIRCLES = False
    SHOW_FOLLOWING_DISTANCE = False  # Show following distance indicators

    # Asset paths (relative to src folder)
    ASSETS_DIR = "assets"
    BACKGROUND_IMAGE = "background.png"