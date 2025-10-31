import pygame as pg
import sys
from pathlib import Path

if __name__ == "__main__":
    src_path = Path(__file__).resolve().parents[2]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
try:
    from ..configuration import Config
except ImportError:
    from traffic_sim.configuration import Config

config = Config()
WIDTH = config.WIDTH
HEIGHT = config.HEIGHT

class WorldRenderer:
    """Handles rendering of the entire traffic simulation world"""
    def __init__(self):
        # Colors
        self.ROAD_COLOR = (80, 80, 80)  # Dark gray for roads
        self.GRASS_COLOR = (100, 180, 100)  # Light green for surroundings
        self.SIDEWALK_COLOR = (200, 200, 200)  # Light gray for sidewalks
        self.LINE_COLOR = (255, 255, 255)  # White for road lines
        self.RIVER_COLOR = (0, 162, 230)  # Blue for river
        
        # Create base surface
        self.background = pg.Surface((WIDTH, HEIGHT))
        self._create_background()
        
    def _create_background(self):
        """Create the static background with roads, river, and markings"""
        # Fill with grass
        self.background.fill(self.GRASS_COLOR)
        
        # Draw river on the right side
        river_width = WIDTH * 0.3
        river_x = WIDTH * 0.7
        pg.draw.rect(self.background, self.RIVER_COLOR, (river_x, 0, river_width, HEIGHT))

        # Draw main roads
        road_width = WIDTH * 0.15
        # Vertical road
        pg.draw.rect(self.background, self.ROAD_COLOR,
                     (WIDTH/2 - road_width/2, 0, road_width, HEIGHT))
        # Horizontal road
        pg.draw.rect(self.background, self.ROAD_COLOR,
                     (0, HEIGHT/2 - road_width/2, WIDTH, road_width))

        # Draw sidewalks
        sidewalk_width = WIDTH * 0.03
        # Vertical sidewalks
        for x in [WIDTH/2 - road_width/2 - sidewalk_width, WIDTH/2 + road_width/2]:
            pg.draw.rect(self.background, self.SIDEWALK_COLOR,
                         (x, 0, sidewalk_width, HEIGHT))
        # Horizontal sidewalks
        for y in [HEIGHT/2 - road_width/2 - sidewalk_width, HEIGHT/2 + road_width/2]:
            pg.draw.rect(self.background, self.SIDEWALK_COLOR,
                         (0, y, WIDTH, sidewalk_width))

        # Draw road markings
        line_width = 3
        dash_length = 20
        gap_length = 20

        # Center lines
        # Vertical
        y = 0
        while y < HEIGHT:
            pg.draw.line(self.background, self.LINE_COLOR,
                         (WIDTH/2, y), (WIDTH/2, y + dash_length), line_width)
            y += dash_length + gap_length

        # Horizontal
        x = 0
        while x < WIDTH:
            pg.draw.line(self.background, self.LINE_COLOR,
                         (x, HEIGHT/2), (x + dash_length, HEIGHT/2), line_width)
            x += dash_length + gap_length

        # Draw bridge crossing the river (on the right side)
        bridge_thickness = road_width * 1.2
        bridge_y = HEIGHT / 2 - bridge_thickness / 2
        pg.draw.rect(self.background, self.ROAD_COLOR,
                     (river_x, bridge_y, river_width, bridge_thickness))

        # Bridge railings (top and bottom along the river segment)
        railing_color = (60, 60, 60)
        railing_height = int(max(2, bridge_thickness * 0.08))
        # top railing
        pg.draw.rect(self.background, railing_color,
                     (river_x, bridge_y - railing_height, river_width, railing_height))
        # bottom railing
        pg.draw.rect(self.background, railing_color,
                     (river_x, bridge_y + bridge_thickness, river_width, railing_height))

def draw(screen, background, views=()):
    """Draw entire scene"""
    if background:
        screen.blit(background, (0,0))
    else:
        screen.fill((40,44,52))

    # Draw order: background, then agents, then HUD
    for v in views:
        v.draw(screen)
    
    # Update display
    pg.display.flip()

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption('Traffic Simulation World Renderer')
    clock = pg.time.Clock()
    renderer = WorldRenderer()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        draw(screen, renderer.background)
        clock.tick(60)
    pg.quit()

if __name__ == "__main__":
    main()