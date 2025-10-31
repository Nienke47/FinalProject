# src/traffic_sim/domain/world/traffic_light.py
from enum import Enum, auto

class Light(Enum):
    RED = auto()
    AMBER = auto()
    GREEN = auto()

class Stoplicht:
    """Los van pygame. Houdt tijd + huidige kleur bij."""
    def __init__(self, green_s=8.0, amber_s=2.0, red_s=10.0, auto_cycle=False):
        self.green_s = green_s
        self.amber_s = amber_s
        self.red_s = red_s
        self.state = Light.RED
        self.t = 0.0
        self.auto_cycle = auto_cycle

    def set_state(self, state: Light, reset=True):
        self.state = state
        if reset:
            self.t = 0.0

    def get_state(self) -> Light:
        return self.state
    
    def is_green(self) -> bool:
        return self.state == Light.GREEN

    def update(self, dt: float):
        self.t += dt
        if not self.auto_cycle:
            return

        # simpele cyclische volgorde: RED -> GREEN -> AMBER -> RED ...
        if self.state is Light.RED and self.t >= self.red_s:
            self.set_state(Light.GREEN)
        elif self.state is Light.GREEN and self.t >= self.green_s:
            self.set_state(Light.AMBER)
        elif self.state is Light.AMBER and self.t >= self.amber_s:
            self.set_state(Light.RED)
