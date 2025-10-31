import pygame
import sys
from typing import Tuple, List, Callable
from pathlib import Path

# Add src to Python path when running directly
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

Vec2 = Tuple[float, float]
config = Config()

def draw_pedestrian(screen, x, y, scale=1):

    # Shoulders (very flat, wide ellipse, just below head)
    shoulder_color = (0, 102, 204)  # Blue
    shoulder_rect = pygame.Rect(x - 4 * scale, y + 12 * scale, 28 * scale, 7 * scale)
    pygame.draw.ellipse(screen, shoulder_color, shoulder_rect)

    # Head (circle) drawn after shoulders, placed even lower
    head_color = (255, 224, 189)  # Skin tone
    head_center = (int(x + 10 * scale), int(y + 15 * scale))
    pygame.draw.circle(screen, head_color, head_center, int(6 * scale))

    # Hair (arc on top of the head)
    hair_color = (80, 50, 20)  # Donkerbruin
    hair_rect = pygame.Rect(head_center[0] - 6 * scale, head_center[1] - 6 * scale, 12 * scale, 8 * scale)
    pygame.draw.ellipse(screen, hair_color, hair_rect)

# attempt relative import when packaged, fallback to module import when run as script
try:
    from .road_users import RoadUser
except Exception:
    from trafficsimulation.domain.actors.road_users import RoadUser

Vec2 = Tuple[float, float]

class Pedestrian(RoadUser):
    """
    Pedestrian is a RoadUser that can follow a path (inherited) and be drawn.
    It uses self.pos (list of floats) updated by RoadUser.update().
    """

    def __init__(
        self,
        path_px: List[Tuple[float, float]],
        speed_px_s: float = config.SPEEDS["PEDESTRIAN"],
        can_cross_ok: Callable[[], bool] = lambda: True,
        color: Tuple[int, int, int] = config.BLUE,
        skin: Tuple[int, int, int] = (255, 224, 189),
        hair: Tuple[int, int, int] = (80, 50, 20),
        scale: float = 1.0,
    ):
        super().__init__(path_px, speed_px_s, can_cross_ok)
        self.color = color
        self.skin = skin
        self.hair = hair
        self.scale = float(scale)
        self.radius = max(4, int(config.COLLISION_RADIUS["PEDESTRIAN"] * self.scale))
        self._ped_surf = self._create_surface()

    def _S(self, v: float) -> int:
        return max(1, int(round(v * self.scale)))

    def _create_surface(self) -> pygame.Surface:
        """Create a surface with the pedestrian drawing for rotation."""
        # Make surface large enough for rotation
        w, h = self._S(50), self._S(50)  # Square surface for clean rotation
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Center point of surface
        cx, cy = w // 2, h // 2
        
        # Shoulders (very flat, wide ellipse, just below head)
        shoulder_rect = pygame.Rect(
            cx - self._S(4),  # x offset from center
            cy + self._S(12), # y offset from center
            self._S(28),      # width
            self._S(7)        # height
        )
        pygame.draw.ellipse(surf, self.color, shoulder_rect)

        # Head (circle) drawn after shoulders, placed even lower
        head_center = (
            int(cx + self._S(10)),  # x offset from center
            int(cy + self._S(15))   # y offset from center
        )
        pygame.draw.circle(surf, self.skin, head_center, self._S(6))

        # Hair (arc on top of the head)
        hair_rect = pygame.Rect(
            head_center[0] - self._S(6),  # x offset from head center
            head_center[1] - self._S(6),  # y offset from head center
            self._S(12),                  # width
            self._S(8)                    # height
        )
        pygame.draw.ellipse(surf, self.hair, hair_rect)
        
        return surf

    def draw(self, surface: pygame.Surface) -> None:
        """Draw pedestrian at current position with rotation."""
        x, y = int(round(self.pos[0])), int(round(self.pos[1]))
        
        # Get rotation from parent RoadUser class
        angle = -super().get_rotation()
        
        # Rotate the surface
        rotated = pygame.transform.rotate(self._ped_surf, angle)
        
        # Get centered rect
        rect = rotated.get_rect(center=(x, y))
        
        # Draw
        surface.blit(rotated, rect)

# Demo runner
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    # Create test path
    path = [(50, config.HEIGHT//2), (config.WIDTH-50, config.HEIGHT//2)]
    ped = Pedestrian(path, speed_px_s=config.SPEEDS["PEDESTRIAN"], scale=1.0)

    running = True
    while running:
        dt = clock.get_time() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ped.update(dt)
        
        screen.fill(config.BACKGROUND)
        ped.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()