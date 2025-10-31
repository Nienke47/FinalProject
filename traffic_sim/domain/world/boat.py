import pygame
import sys
from typing import Tuple, List
from pathlib import Path

# Add src to Python path when running directly
if __name__ == "__main__":
    src_path = Path(__file__).resolve().parents[3]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

# Try relative import first, fall back to absolute if running as script
try:
    from ...configuration import Config
except ImportError:
    from traffic_sim.configuration import Config

config = Config()
Vec2 = Tuple[float, float]

class Boat:
    """Boat that moves upwards along a vertical path."""

    def __init__(
        self,
        scale: float = 1.0,
        path_px: List[Vec2] = None,
        speed_px_s: float = None
    ):
        if path_px is None:
            path_px = []
        if speed_px_s is None:
            speed_px_s = config.SPEEDS["BOAT"]

        self.scale = float(scale)
        self.path = path_px
        self.speed = float(speed_px_s)

        self.i = 0
        self.pos = list(self.path[0]) if self.path else [0.0, 0.0]
        self.done = False

    def update(self, dt: float) -> None:
        """Move the boat along its path, only vertically (y-axis)."""
        if self.done or self.i + 1 >= len(self.path):
            self.done = True
            return

        target_y = self.path[self.i + 1][1]
        dy = target_y - self.pos[1]

        step = self.speed * dt
        if abs(dy) <= step:
            self.pos[1] = target_y
            self.i += 1
        else:
            self.pos[1] += step if dy > 0 else -step

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the boat at its current position."""
        x, y = int(self.pos[0]), int(self.pos[1])
        scale = self.scale
        hull_w, hull_h = int(20 * scale), int(60 * scale)
        surf = pygame.Surface((hull_w, hull_h), pygame.SRCALPHA)

        # Hull
        hull_color = (139, 69, 19)
        pygame.draw.ellipse(surf, hull_color, pygame.Rect(0, 0, hull_w, hull_h))

        # Mast
        mast_color = (0, 0, 0)
        mast_x = hull_w * 0.5
        mast_y1 = hull_h * 0.2
        mast_y2 = hull_h * 0.8
        pygame.draw.line(surf, mast_color, (mast_x, mast_y1), (mast_x, mast_y2), max(1, int(2 * scale)))

        # Sail
        sail_color = (255, 255, 255)
        pygame.draw.polygon(surf, sail_color, [
            (mast_x, mast_y1),
            (mast_x - 8 * scale, mast_y1 + 15 * scale),
            (mast_x + 8 * scale, mast_y1 + 15 * scale)
        ])

        rect = surf.get_rect(center=(x, y))
        surface.blit(surf, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Path: only moves vertically, x stays constant
    path = [(400, 500), (400, 400), (400, 300), (400, 200), (400, 100)]
    boat = Boat(scale=1.2, path_px=path, speed_px_s=100.0)

    running = True
    while running:
        dt = clock.get_time() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        boat.update(dt)

        screen.fill((135, 206, 250))
        boat.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
