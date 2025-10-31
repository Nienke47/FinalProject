# src/traffic_sim/render/draw_traffic_light.py
import pygame as pg
from typing import Tuple
from ..domain.world.traffic_light import Light, Stoplicht

class DrawableStoplicht:
    """Visual representation of a traffic light"""
    def __init__(self, traffic_light: Stoplicht, pos: Tuple[int, int], scale: float = 0.2, as_pedestrian: bool = False, rotation: int = 0):
        self.traffic_light = traffic_light
        self.pos = pos
        self.scale = scale
        self.surface = None
        self.as_pedestrian = as_pedestrian
        self.rotation = rotation  # 0, 90, 180, or 270 degrees
        self._create_surface()
    
    def set_active(self, light: Light):
        """Update the active state of the traffic light"""
        # Don't mutate the domain traffic light from the view (that resets timers).
        # Store a local display state used for rendering only.
        self._display_state = light
    
    def S(self, value: float) -> int:
        """Scale a value according to the traffic light's scale factor"""
        return int(value * self.scale)
    
    def _create_surface(self):
        """Create the traffic light's visual representation"""
        # Base dimensions (smaller for pedestrian lights)
        base_width = 200 if not self.as_pedestrian else 150
        base_height = 500 if not self.as_pedestrian else 400
        width = self.S(base_width)
        height = self.S(base_height)
        self.surface = pg.Surface((width, height), pg.SRCALPHA)
        
        # Colors
        BLACK = (0, 0, 0)
        DARK_GRAY = (50, 50, 50)
        HOUSING_GRAY = (100, 100, 100)
        
        # Draw main housing
        housing_rect = (0, 0, width, height)
        pg.draw.rect(self.surface, HOUSING_GRAY, housing_rect, border_radius=self.S(40))
        pg.draw.rect(self.surface, BLACK, housing_rect, width=self.S(10), border_radius=self.S(40))
        
        # Draw lights
        light_size = self.S(120 if not self.as_pedestrian else 100)
        light_margin = self.S(20)
        light_x = (width - light_size) // 2

        # Determine display state (use local if set, otherwise domain state)
        display_state = getattr(self, '_display_state', self.traffic_light.state)

        # Define colors
        RED_COLOR = (255, 0, 0)
        AMBER_COLOR = (255, 191, 0)
        GREEN_COLOR = (0, 255, 0)
        OFF_COLOR = (60, 60, 60)

        # Green light at top (flipped order)
        green_y = light_margin
        pg.draw.circle(self.surface, GREEN_COLOR if display_state == Light.GREEN else OFF_COLOR,
                      (width//2, green_y + light_size//2), light_size//2)

        # Amber light in middle
        amber_y = green_y + light_size + light_margin
        pg.draw.circle(self.surface, AMBER_COLOR if display_state == Light.AMBER else OFF_COLOR,
                      (width//2, amber_y + light_size//2), light_size//2)

        # Red light at bottom (flipped order)
        red_y = amber_y + light_size + light_margin
        pg.draw.circle(self.surface, RED_COLOR if display_state == Light.RED else OFF_COLOR,
                      (width//2, red_y + light_size//2), light_size//2)
    
    def draw(self, screen: pg.Surface):
        """Draw the traffic light on the screen"""
        if not self.surface:
            self._create_surface()

        # Update surface to reflect current state
        self._create_surface()

        # Optionally rotate the surface before drawing
        surf = self.surface
        if getattr(self, 'rotation', 0):
            # rotate around center
            surf = pg.transform.rotate(self.surface, self.rotation)

        # Draw at position (centered)
        x, y = self.pos
        screen.blit(surf, (x - surf.get_width()//2, y - surf.get_height()//2))