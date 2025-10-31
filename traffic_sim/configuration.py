
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
        "CAR": 100.0,
        "TRUCK": 80.0,
        "CYCLIST": 60.0,
        "PEDESTRIAN": 40.0,
        "BOAT": 50.0
    }

    # Collision detection - Physical boundaries to prevent touching
    COLLISION_RADIUS = {
        "CAR": 22,        # Increased by 10% (20 * 1.1 = 22)
        "TRUCK": 35,      # Reduced from 41 to make truck hitbox smaller
        "CYCLIST": 12,    # Reduced collision width for cyclists (was 17)
        "PEDESTRIAN": 11, # Increased by 10% (10 * 1.1 = 11)
        "BOAT": 22        # Increased by 10% (20 * 1.1 = 22)
    }

    # Path settings
    INTERSECTION_POINT = (WIDTH // 2, HEIGHT // 2)
    ROAD_WIDTH = 60

    # Vehicle-specific spacing settings - STRICT NO-TOUCH POLICY
    # All vehicles maintain safe distances to prevent any contact/overlap
    VEHICLE_SPACING = {
        "CAR": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 4.4,  # Increased by 10% (4 * 1.1 = 4.4)
            "MIN_FOLLOWING_DISTANCE": 44.0,        # Increased by 10% (40 * 1.1 = 44)
            "SEARCH_DISTANCE": 88.0,              # Increased by 10% (80 * 1.1 = 88)
            "EMERGENCY_STOP_DISTANCE": 33.0,       # Increased by 10% (30 * 1.1 = 33)
        },
        "TRUCK": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 5.5,  # Increased by 10% (5.0 * 1.1 = 5.5)
            "MIN_FOLLOWING_DISTANCE": 88.0,        # Increased by 10% (80 * 1.1 = 88)
            "SEARCH_DISTANCE": 220.0,              # Increased by 10% (200 * 1.1 = 220)
            "EMERGENCY_STOP_DISTANCE": 72.0,       # Increased by 10% (65 * 1.1 = 71.5 ≈ 72)
        },
        "CYCLIST": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 1.7,  # Increased by 10% (1.5 * 1.1 = 1.65 ≈ 1.7)
            "MIN_FOLLOWING_DISTANCE": 55.0,        # Increased by 10% (50 * 1.1 = 55)
            "SEARCH_DISTANCE": 110.0,              # Increased by 10% (100 * 1.1 = 110)
            "EMERGENCY_STOP_DISTANCE": 39.0,       # Increased by 10% (35 * 1.1 = 38.5 ≈ 39)
        },
        "PEDESTRIAN": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 0.9,  # Increased by 10% (0.8 * 1.1 = 0.88 ≈ 0.9)
            "MIN_FOLLOWING_DISTANCE": 28.0,        # Increased by 10% (25 * 1.1 = 27.5 ≈ 28)
            "SEARCH_DISTANCE": 88.0,               # Increased by 10% (80 * 1.1 = 88)
            "EMERGENCY_STOP_DISTANCE": 22.0,       # Increased by 10% (20 * 1.1 = 22)
        },
        # Global fallback settings for unknown vehicle types
        "DEFAULT": {
            "FOLLOWING_DISTANCE_MULTIPLIER": 1.7,  # Increased by 10% (1.5 * 1.1 = 1.65 ≈ 1.7)
            "MIN_FOLLOWING_DISTANCE": 66.0,        # Increased by 10% (60 * 1.1 = 66)
            "SEARCH_DISTANCE": 165.0,              # Increased by 10% (150 * 1.1 = 165)
            "EMERGENCY_STOP_DISTANCE": 28.0,       # Increased by 10% (25 * 1.1 = 27.5 ≈ 28)
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