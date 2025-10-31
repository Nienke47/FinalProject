from typing import List, Tuple

Point = Tuple[float, float]  # genormaliseerd 0..1

# Route definitions for all possible directions
# North-South routes (going up)
CARS_NS_UP: List[Point] = [
    # Straight up - extend further beyond screen edges
    (0.55, 1.10), (0.55, 0.80), (0.55, -0.10)
]
CARS_NS_RIGHT: List[Point] = [
    # Turn left from south to east - extend exit point
    (0.55, 1.10), (0.55, 0.80), (0.55, 0.55), (1.10, 0.55)
]
CARS_NS_LEFT: List[Point] = [
    # Turn right from south to west - extend exit point
    (0.55, 1.10), (0.55, 0.80), (0.55, 0.45), (-0.10, 0.45)
]

# East-West routes
CARS_EW_RIGHT: List[Point] = [
    # Straight through - extend beyond screen edges
    (-0.10, 0.55), (0.20, 0.55), (1.10, 0.55)
]
CARS_EW_LEFT: List[Point] = [
    # Turn left from west to south - extend exit point
    (-0.10, 0.55), (0.20, 0.55), (0.55, 0.55), (0.55, 1.10)
]
CARS_EW_TURN_RIGHT: List[Point] = [
    # Turn right from west to north - extend exit point
    (-0.10, 0.55), (0.20, 0.55), (0.45, 0.55), (0.55, -0.10)
]

# Fietsers (rood) en voetgangers (bruin) iets opzij van het midden:
BIKES_NS_UP: List[Point] = [
    # cyclists stay closer to the cars but still on the right side - extend beyond edges
    (0.60, 1.10), (0.60, 0.80), (0.60, -0.10)
]
PEDS_EW_RIGHT: List[Point] = [
    # pedestrians on the grass further from the road (north of sidewalk) - extend beyond edges
    (-0.10, 0.30), (0.20, 0.30), (1.10, 0.30)
]

def to_pixels(path: List[Point], w: int, h: int):
    return [(int(x*w), int(y*h)) for x, y in path]