import pygame
import sys
import math
from typing import List, Tuple, Callable
from pathlib import Path

if __name__ == "__main__":
    src_path = Path(__file__).resolve().parents[3]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

# Try relative import first, fall back to absolute if running as script
try:
    from ...configuration import Config
    from .road_users import RoadUser
except ImportError:
    from traffic_sim.configuration import Config
    from traffic_sim.domain.actors.road_users import RoadUser

config = Config()

# Colors can come from config now
RED = config.RED
GRAY = config.GRAY
BLUE = config.BLUE
WIDTH = config.WIDTH
HEIGHT = config.HEIGHT

Vec2 = Tuple[float, float]

class Car(RoadUser):
    """
    Car is a RoadUser that follows a path (RoadUser.update) and draws itself.
    Drawing is identical to the original procedural car: a rectangular body,
    roof/window and four wheels drawn onto a transparent surface and blitted
    centered at the actor position (self.pos).
    """

    def __init__(
        self,
        path_px: List[Vec2],
        speed_px_s: float = config.SPEEDS["CAR"],  # use config speed
        width: int = 50,
        length: int = 80,
        color=RED,
        roof_color=BLUE,
        can_cross_ok: Callable[[], bool] = lambda: True,
    ):
        super().__init__(path_px, speed_px_s, can_cross_ok)
        # keep same naming as previous file for visuals
        self.width = float(width)
        self.length = float(length)
        self.color = color
        self.roof_color = roof_color
        self._car_surf = self._create_surface()

    def _create_surface(self) -> pygame.Surface:
        CAR_W, CAR_H = int(self.width), int(self.length)
        surf = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)

        # Car body
        pygame.draw.rect(surf, self.color, (0, 0, CAR_W, CAR_H), border_radius=8)
        # Roof / window
        pygame.draw.rect(
            surf,
            self.roof_color,
            (CAR_W * 0.15, CAR_H * 0.2, CAR_W * 0.7, CAR_H * 0.4),
            border_radius=6,
        )
        # Wheels (same placement as original)
        wheel_w, wheel_h = 14, 24
        pygame.draw.ellipse(surf, GRAY, (-wheel_w // 2, CAR_H * 0.1, wheel_w, wheel_h))
        pygame.draw.ellipse(surf, GRAY, (-wheel_w // 2, CAR_H * 0.65, wheel_w, wheel_h))
        pygame.draw.ellipse(surf, GRAY, (CAR_W - wheel_w // 2, CAR_H * 0.1, wheel_w, wheel_h))
        pygame.draw.ellipse(surf, GRAY, (CAR_W - wheel_w // 2, CAR_H * 0.65, wheel_w, wheel_h))

        return surf

    def draw(self, surface: pygame.Surface) -> None:
        """Draw car centered at its current position with rotation."""
        x, y = int(round(self.pos[0])), int(round(self.pos[1]))
        
        # Get rotation from parent RoadUser class
        angle = super().get_rotation()
        
        # Rotate the car surface
        rotated = pygame.transform.rotate(self._car_surf, angle)
        
        # Get the new rect centered at our position
        rect = rotated.get_rect(center=(x, y))
        
        # Draw the rotated surface
        surface.blit(rotated, rect)

    def clone(self) -> "Car":
        """Return a shallow copy of this Car (same type)."""
        new = Car(
            list(self.path),
            speed_px_s=self.speed,
            width=int(self.width),
            length=int(self.length),
            color=self.color,
            roof_color=self.roof_color,
            can_cross_ok=self._can_cross,
        )
        new.pos = list(self.pos)
        new.i = self.i
        new.done = self.done
        return new

# Simple demo loop when run as a script
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simpel bovenaanzicht autootje")
    clock = pygame.time.Clock()

    # simple two-point path: start center, move to the right
    path = [(50, 100), (50, 500), (800, 500), (800, 100)]
    car = Car(path, speed_px_s=120.0, width=50, length=80)

    # Create a car instance
    car = Car(path, speed_px_s=120.0)  # Add speed to see movement

    running = True
    while running:
        dt = clock.get_time() / 1000.0  # seconds since last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update and draw the car instance
        car.update(dt)

        screen.fill((220, 220, 220))
        car.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()