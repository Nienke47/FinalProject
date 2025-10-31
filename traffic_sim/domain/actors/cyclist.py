# src/traffic_sim/domain/actors/cyclist.py
import pygame
import sys
from typing import List, Tuple, Callable
import math
from pathlib import Path

# Add src to Python path when running directly
if __name__ == "__main__":
    # Find src directory (3 levels up from cyclist.py)
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

Vec2 = Tuple[float, float]
config = Config()

class Cyclist(RoadUser):
    """
    Fietser (logica): volgt waypoints, houdt evt. bij het kruispunt stil op rood.
    Geen tekenwerk/pygame hier.
    """
    def __init__(
        self,
        path_px: List[Vec2],
        speed_px_s: float = config.SPEEDS["CYCLIST"],  # Use config speed
        can_cross_ok: Callable[[], bool] = lambda: True,
        color: Tuple[int, int, int] = config.BLUE,  # Use config colors
        skin: Tuple[int, int, int] = (230, 190, 160),
        hair: Tuple[int, int, int] = (100, 60, 30),
        scale: float = 0.2,
    ):
        super().__init__(path_px, speed_px_s, can_cross_ok)
        self.color = color
        self.skin = skin
        self.hair = hair
        self.scale = float(scale)
        self.radius = max(4, int(config.COLLISION_RADIUS["CYCLIST"] * self.scale))  # Use config radius
        # Create surface for rotation
        self._cyclist_surf = self._create_surface()

    def _S(self, value: float) -> int:
        return max(1, int(round(value * self.scale)))

    def _create_surface(self) -> pygame.Surface:
        """Create a surface with the cyclist drawing for rotation."""
        S = self._S
        # Create surface large enough for rotation
        w, h = S(120), S(200)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Draw cyclist centered on surface
        cx, cy = w // 2, h // 2
        
        # Frame (vertical main frame)
        pygame.draw.rect(surf, (40, 40, 40),
                        (cx - S(5), cy - S(100), S(10), S(200)))
        
        # Front/rear rectangles
        pygame.draw.rect(surf, (0, 0, 0),
                        (cx - S(3), cy - S(120), S(6), S(20)))
        pygame.draw.rect(surf, (0, 0, 0),
                        (cx - S(3), cy + S(100), S(6), S(20)))

        # Handlebars
        pygame.draw.rect(surf, (100, 100, 100),
                        (cx - S(60), cy - S(115), S(120), S(8)),
                        border_radius=S(3))

        # Arms
        pygame.draw.line(surf, self.skin,
                        (cx - S(30), cy - S(30)),
                        (cx - S(45), cy - S(110)), S(12))
        pygame.draw.line(surf, self.skin,
                        (cx + S(30), cy - S(30)),
                        (cx + S(45), cy - S(110)), S(12))

        # Body / shirt
        pygame.draw.ellipse(surf, self.color,
                          (cx - S(40), cy - S(50), S(80), S(80)))

        # Head
        pygame.draw.circle(surf, self.hair,
                         (cx, cy - S(70)), S(22))

        # Handlebar grips
        pygame.draw.circle(surf, (0, 0, 0),
                         (cx - S(55), cy - S(111)), S(6))
        pygame.draw.circle(surf, (0, 0, 0),
                         (cx + S(55), cy - S(111)), S(6))

        return surf

    def draw(self, surface: pygame.Surface) -> None:
        """Draw cyclist at current position with rotation."""
        x, y = int(round(self.pos[0])), int(round(self.pos[1]))
        
        # Get rotation from RoadUser parent class
        angle = self.get_rotation()
        
        # Rotate the surface
        rotated = pygame.transform.rotate(self._cyclist_surf, angle)
        
        # Get the new rect centered at our position
        rect = rotated.get_rect(center=(x, y))
        
        # Draw the rotated surface
        surface.blit(rotated, rect)

    # Als je fietsspecifieke logica hebt, voeg die hier toe (bijv. prefer bike lanes)
    # def update(self, dt: float):
    #     super().update(dt)

# Demo runner
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    # Create path with turns to test rotation
    path = [(0, 200), (500, 200), (500, 800), (500, 100), (0, 100)]
    cyclist = Cyclist(path, speed_px_s=config.SPEEDS["CYCLIST"], scale=0.2)

    running = True
    while running:
        dt = clock.get_time() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        cyclist.update(dt)
        
        screen.fill(config.BACKGROUND)
        cyclist.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()
