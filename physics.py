# src/traffic_sim/services/physics.py
import math
from typing import List
from ..domain.actors.road_users import RoadUser

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
