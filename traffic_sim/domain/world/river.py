import pygame
import math
import sys

# --- S Line class ---
class RiverSLine:
    def __init__(self, x, y, amplitude=10, wavelength=40, length=150, speed=1):
        self.x = x
        self.y = y
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.length = length
        self.speed = speed
        self.points = self.generate_points()

    def generate_points(self):
        """Generate a vertical S-shaped line (wave in X direction)."""
        points = []
        for i in range(self.length):
            dy = i
            dx = math.sin(i / self.wavelength * 2 * math.pi) * self.amplitude
            points.append((self.x + dx, self.y + dy))
        return points

    def draw(self, surface, color=(0, 200, 255)):
        """Draw the S-line."""
        if len(self.points) > 1:
            pygame.draw.lines(surface, color, False, self.points, 3)


# --- Create centered S-line ---
def create_center_s_line(screen_width, screen_height):
    x = screen_width // 2
    y = screen_height // 2 - 75  # vertical offset to center the smaller line
    return RiverSLine(x, y, amplitude=10, wavelength=40, length=150, speed=1)


# --- Main section (window + draw) ---
def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Centered Vertical S-Line")

    clock = pygame.time.Clock()
    s_line = create_center_s_line(screen_width, screen_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((10, 10, 20))  # background
        s_line.draw(screen)        # draw the smaller S-line
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()