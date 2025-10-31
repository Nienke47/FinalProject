
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
        "CAR": 5,
        "TRUCK": 5,
        "CYCLIST": 5,
        "PEDESTRIAN": 5,
        "BOAT": 5
    }

    # Path settings
    INTERSECTION_POINT = (WIDTH // 2, HEIGHT // 2)
    ROAD_WIDTH = 60

    # Debug settings
    DEBUG_MODE = False
    SHOW_PATHS = False
    SHOW_COLLISION_CIRCLES = False

    # Asset paths (relative to src folder)
    ASSETS_DIR = "assets"
    BACKGROUND_IMAGE = "background.png"