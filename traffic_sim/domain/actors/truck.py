import pygame
import sys
import math
from typing import Tuple, List, Callable
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

Vec2 = Tuple[float, float]

# Colors (use config where available)
RED = getattr(config, "RED", (200, 30, 30))
BLUE = getattr(config, "BLUE", (60, 150, 255))
GRAY = getattr(config, "GRAY", (100, 100, 100))
DARK_GRAY = getattr(config, "DARK_GRAY", (40, 40, 40))
BLACK = (0, 0, 0)
WHITE = getattr(config, "WHITE", (230, 230, 230))
BACKGROUND = getattr(config, "BACKGROUND", (220, 220, 220))


class Truck(RoadUser):
    """
    Truck actor that inherits RoadUser for movement & rotation.
    Drawing matches the original truck visuals; rotation is taken from RoadUser.get_rotation().
    """

    def __init__(
        self,
        path_px: List[Vec2],
        speed_px_s: float = None,
        can_cross_ok: Callable[[], bool] = lambda: True,
        cab_color: Tuple[int, int, int] = BLUE,
        trailer_color: Tuple[int, int, int] = WHITE,
        scale: float = 0.3,
    ):
        speed = speed_px_s if speed_px_s is not None else config.SPEEDS.get("TRUCK", 80.0)
        super().__init__(path_px, speed, can_cross_ok)
        self.cab_color = cab_color
        self.trailer_color = trailer_color
        self.scale = float(scale)
        self.radius = int(config.COLLISION_RADIUS.get("TRUCK", 35) * self.scale)
        self._truck_surf = self._create_surface()

    def _S(self, v: float) -> int:
        return max(1, int(round(v * self.scale)))

    def _create_surface(self) -> pygame.Surface:
        S = self._S
        surf_w, surf_h = S(120), S(280)
        surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        cx, cy = surf_w // 2, surf_h // 2

        # Trailer (rear)
        trailer_w, trailer_h = S(80), S(200)
        trailer_rect = pygame.Rect(cx - trailer_w // 2, cy - trailer_h // 2 + S(40), trailer_w, trailer_h)
        pygame.draw.rect(surf, self.trailer_color, trailer_rect, border_radius=S(6))
        pygame.draw.rect(surf, GRAY, trailer_rect, width=S(3), border_radius=S(6))

        # Cab (front)
        cab_w, cab_h = S(90), S(80)
        cab_rect = pygame.Rect(cx - cab_w // 2, trailer_rect.top - cab_h + S(5), cab_w, cab_h)
        pygame.draw.rect(surf, self.cab_color, cab_rect, border_radius=S(8))

        # Windshield
        pygame.draw.rect(
            surf,
            (120, 200, 255),
            (cab_rect.left + S(10), cab_rect.top + S(10), cab_w - S(20), S(25)),
            border_radius=S(4),
        )

        # Wheels
        wheel_w, wheel_h = S(14), S(28)
        pygame.draw.ellipse(surf, DARK_GRAY, (cab_rect.left - wheel_w // 2, cab_rect.top + S(15), wheel_w, wheel_h))
        pygame.draw.ellipse(surf, DARK_GRAY, (cab_rect.right - wheel_w // 2, cab_rect.top + S(15), wheel_w, wheel_h))
        for offset in [S(10), S(130), S(150)]:
            pygame.draw.ellipse(surf, BLACK, (trailer_rect.left - wheel_w // 2, trailer_rect.top + offset, wheel_w, wheel_h))
            pygame.draw.ellipse(surf, BLACK, (trailer_rect.right - wheel_w // 2, trailer_rect.top + offset, wheel_w, wheel_h))

        # Divider line between cab and trailer
        pygame.draw.line(surf, DARK_GRAY, (cx - S(45), trailer_rect.top), (cx + S(45), trailer_rect.top), S(3))

        # Lights
        pygame.draw.circle(surf, (255, 255, 150), (cab_rect.left + S(15), cab_rect.top + S(5)), S(5))
        pygame.draw.circle(surf, (255, 255, 150), (cab_rect.right - S(15), cab_rect.top + S(5)), S(5))
        pygame.draw.circle(surf, RED, (trailer_rect.left + S(15), trailer_rect.bottom - S(8)), S(6))
        pygame.draw.circle(surf, RED, (trailer_rect.right - S(15), trailer_rect.bottom - S(8)), S(6))

        return surf

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the truck centered at self.pos, rotated according to RoadUser.get_rotation().
        """
        x = int(round(self.pos[0]))
        y = int(round(self.pos[1]))
        angle = self.get_rotation()
        rotated = pygame.transform.rotate(self._truck_surf, angle)
        rect = rotated.get_rect(center=(x, y))
        surface.blit(rotated, rect)

    def clone(self) -> "Truck":
        new = Truck(list(self.path), speed_px_s=self.speed, can_cross_ok=self._can_cross, cab_color=self.cab_color, trailer_color=self.trailer_color, scale=self.scale)
        new.pos = list(self.pos)
        new.i = self.i
        new.done = self.done
        return new


# Demo runner when executed directly
if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Truck demo")
    clock = pygame.time.Clock()

    path = [(50, HEIGHT // 2), (WIDTH - 50, HEIGHT // 2)]
    truck = Truck(path, speed_px_s=config.SPEEDS.get("TRUCK", 80.0), scale=0.4)

    running = True
    while running:
        dt = clock.get_time() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        truck.update(dt)

        screen.fill(BACKGROUND)
        truck.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()
