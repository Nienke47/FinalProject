from enum import Enum, auto
from .traffic_light import Stoplicht, Light

class Phase(Enum):
    NS_CARS_GREEN = auto()   # Noord/Zuid auto's groen
    EW_CARS_GREEN = auto()   # Oost/West auto's groen
    NS_PED_BIKE = auto()     # N/Z voetganger+fietser groen
    EW_PED_BIKE = auto()     # O/W voetganger+fietser groen

class Controller:
    """Eenvoudige 4-fasen controller. Later makkelijk uit te breiden."""
    def __init__(self):
        # 1 set voor auto's per richting-as
        self.cars_ns = Stoplicht(green_s=8,  amber_s=2, red_s=10)
        self.cars_ew = Stoplicht(green_s=8,  amber_s=2, red_s=10)
        # 1 set voor ped/bike per as
        self.ped_ns  = Stoplicht(green_s=6,  amber_s=0.5, red_s=13.5)
        self.ped_ew  = Stoplicht(green_s=6,  amber_s=0.5, red_s=13.5)

        self.phase = Phase.NS_CARS_GREEN
        self._enter_phase(self.phase)

    def _enter_phase(self, phase: Phase):
        self.phase = phase
        for l in (self.cars_ns, self.cars_ew, self.ped_ns, self.ped_ew):
            l.set_state(Light.RED)
        if phase is Phase.NS_CARS_GREEN:
            self.cars_ns.set_state(Light.GREEN)
        elif phase is Phase.EW_CARS_GREEN:
            self.cars_ew.set_state(Light.GREEN)
        elif phase is Phase.NS_PED_BIKE:
            self.ped_ns.set_state(Light.GREEN)
        elif phase is Phase.EW_PED_BIKE:
            self.ped_ew.set_state(Light.GREEN)

    def update(self, dt: float):
        # Update all traffic light timers
        for l in (self.cars_ns, self.cars_ew, self.ped_ns, self.ped_ew):
            l.update(dt)

        # Handle phase transitions based on current phase
        if self.phase is Phase.NS_CARS_GREEN:
            # Check if we need to transition to amber
            if self.cars_ns.state == Light.GREEN and self.cars_ns.t >= self.cars_ns.green_s:
                self.cars_ns.set_state(Light.AMBER, reset=False)  # Don't reset timer
            # Check if amber period is over
            elif self.cars_ns.state == Light.AMBER and self.cars_ns.t >= self.cars_ns.green_s + self.cars_ns.amber_s:
                self._enter_phase(Phase.EW_CARS_GREEN)

        elif self.phase is Phase.EW_CARS_GREEN:
            # Check if we need to transition to amber
            if self.cars_ew.state == Light.GREEN and self.cars_ew.t >= self.cars_ew.green_s:
                self.cars_ew.set_state(Light.AMBER, reset=False)  # Don't reset timer
            # Check if amber period is over
            elif self.cars_ew.state == Light.AMBER and self.cars_ew.t >= self.cars_ew.green_s + self.cars_ew.amber_s:
                self._enter_phase(Phase.NS_PED_BIKE)

        elif self.phase is Phase.NS_PED_BIKE:
            # Pedestrian lights don't have amber, go straight to red
            if self.ped_ns.t >= self.ped_ns.green_s:
                self._enter_phase(Phase.EW_PED_BIKE)

        elif self.phase is Phase.EW_PED_BIKE:
            # Pedestrian lights don't have amber, go straight to red
            if self.ped_ew.t >= self.ped_ew.green_s:
                self._enter_phase(Phase.NS_CARS_GREEN)

    # Query’s waar agents op kunnen beslissen:
    def can_cars_cross_ns(self) -> bool: return self.cars_ns.state is Light.GREEN
    def can_cars_cross_ew(self) -> bool: return self.cars_ew.state is Light.GREEN
    def can_ped_cross_ns(self)  -> bool: return self.ped_ns.state  is Light.GREEN
    def can_ped_cross_ew(self)  -> bool: return self.ped_ew.state  is Light.GREEN
