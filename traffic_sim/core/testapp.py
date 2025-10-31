# src/traffic_sim/core/app.py
import pygame as pg
import time
from pathlib import Path
import time
import sys
import random
import math

if __name__ == "__main__":
    src_path = Path(__file__).resolve().parents[2]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

try:
    from ..configuration import Config
    from ..render.draw_world import draw
    from ..domain.world.intersection import Controller
    from ..domain.actors.car import Car
    from ..domain.actors.cyclist import Cyclist
    from ..domain.actors.pedestrian import Pedestrian
    from ..domain.actors.truck import Truck
    from ..domain.world.boat import Boat
    from ..services.pathing import (
        to_pixels,
        CARS_NS_UP, CARS_NS_LEFT, CARS_NS_RIGHT,
        CARS_EW_RIGHT, CARS_EW_LEFT, CARS_EW_TURN_RIGHT,
        BIKES_NS_UP,
        PEDS_EW_RIGHT,
    )
    from ..services.spawner import Spawner
    from ..services.physics import check_collisions
    from ..services.statistics import SimulationStats
    from ..domain.world.traffic_light import Light            # status enum
    from ..render.draw_traffic_light import DrawableStoplicht # visuele stoplichten
    from ..render.draw_world import WorldRenderer
except ImportError:
    from traffic_sim.configuration import Config
    from traffic_sim.render.draw_world import draw
    from traffic_sim.domain.world.intersection import Controller
    from traffic_sim.domain.actors.car import Car
    from traffic_sim.domain.actors.cyclist import Cyclist
    from traffic_sim.domain.actors.pedestrian import Pedestrian
    from traffic_sim.domain.actors.truck import Truck
    from traffic_sim.domain.world.boat import Boat
    from traffic_sim.services.pathing import (
        to_pixels,
        CARS_NS_UP, CARS_NS_LEFT, CARS_NS_RIGHT,
        CARS_EW_RIGHT, CARS_EW_LEFT, CARS_EW_TURN_RIGHT,
        BIKES_NS_UP,
        PEDS_EW_RIGHT,
    )
    from traffic_sim.services.spawner import Spawner
    from traffic_sim.services.physics import check_collisions
    from traffic_sim.services.statistics import SimulationStats
    from traffic_sim.domain.world.traffic_light import Light            # status enum
    from traffic_sim.render.draw_traffic_light import DrawableStoplicht # visuele stoplichten
    from traffic_sim.render.draw_world import WorldRenderer

config = Config()
def load_background(path: Path):
    try:
        if path.exists():
            return pg.image.load(str(path)).convert()
    except Exception:
        pass
    return None


class App:
    """Main simulation application with self-rendering agents"""

    def __init__(self):
        pg.init()
        self.size = (config.WIDTH, config.HEIGHT)
        self.screen = pg.display.set_mode(self.size)
        pg.display.set_caption(getattr(config, "TITLE", "Traffic Sim"))
        self.clock = pg.time.Clock()

        # Create world renderer and background
        world_renderer = WorldRenderer()
        self.background = world_renderer.background

        # Traffic controller
        self.ctrl = Controller()

        # Helper function: 0..1 → pixels
        def px(nx: float, ny: float):
            return int(nx * self.size[0]), int(ny * self.size[1])

        # Initialize statistics
        self.stats = SimulationStats()
        self.stats_font = pg.font.Font(None, 24)

        # ====== ROUTES → PIXELS ======
        self.cars_ns_up_px = to_pixels(CARS_NS_UP, *self.size)
        self.cars_ns_left_px = to_pixels(CARS_NS_LEFT, *self.size)
        self.cars_ns_right_px = to_pixels(CARS_NS_RIGHT, *self.size)
        self.cars_ew_right_px = to_pixels(CARS_EW_RIGHT, *self.size)
        self.cars_ew_left_px = to_pixels(CARS_EW_LEFT, *self.size)
        self.cars_ew_turn_right_px = to_pixels(CARS_EW_TURN_RIGHT, *self.size)
        self.bikes_ns_up_px = to_pixels(BIKES_NS_UP, *self.size)
        self.peds_ew_right_px = to_pixels(PEDS_EW_RIGHT, *self.size)

        # ====== SPAWNERS ======
        self.car_ns_spawner = Spawner(
            factory=lambda: Car(
                random.choice([
                    self.cars_ns_up_px,
                    self.cars_ns_left_px,
                    self.cars_ns_right_px
                ]),
                can_cross_ok=self.ctrl.can_cars_cross_ns,
            ),
            interval_s=3.0, random_offset=1.0, max_count=50
        )

        self.car_ew_spawner = Spawner(
            factory=lambda: Car(
                random.choice([
                    self.cars_ew_right_px,
                    self.cars_ew_left_px,
                    self.cars_ew_turn_right_px
                ]),
                speed_px_s=130,
                can_cross_ok=self.ctrl.can_cars_cross_ew,
            ),
            interval_s=4.0, random_offset=1.5, max_count=50
        )

        self.bike_ns_spawner = Spawner(
            factory=lambda: Cyclist(self.bikes_ns_up_px, speed_px_s=90, can_cross_ok=self.ctrl.can_ped_cross_ns),
            interval_s=5.0, random_offset=1.0, max_count=30
        )

        self.truck_ew_spawner = Spawner(
            factory=lambda: Truck(
                random.choice([
                    to_pixels([(p[0] - 0.1, p[1]) for p in CARS_EW_RIGHT], *self.size),
                    to_pixels([(p[0] - 0.1, p[1]) for p in CARS_EW_LEFT], *self.size),
                    to_pixels([(p[0] - 0.1, p[1]) for p in CARS_EW_TURN_RIGHT], *self.size)
                ]),
                speed_px_s=100,
                can_cross_ok=self.ctrl.can_cars_cross_ew
            ),
            interval_s=8.0, random_offset=2.0, max_count=20
        )

        self.ped_ew_spawner = Spawner(
            factory=lambda: Pedestrian(self.peds_ew_right_px, speed_px_s=70, can_cross_ok=self.ctrl.can_ped_cross_ew),
            interval_s=4.0, random_offset=1.0, max_count=40
        )

        # ====== TRAFFIC LIGHTS ======
        # Create visual traffic lights at intersection positions
        self.traffic_lights = []
        
        # North-South car traffic light (for cars going north)
        self.tl_car_ns = DrawableStoplicht(
            traffic_light=self.ctrl.cars_ns,
            pos=px(0.52, 0.36),
            scale=0.18,
            as_pedestrian=False,
            rotation=180  # Rotate 180 degrees to face south-to-north traffic
        )
        
        # East-West car traffic light (for cars going east)
        # Positioned on the far side (right/east side) of the intersection
        self.tl_car_ew = DrawableStoplicht(
            traffic_light=self.ctrl.cars_ew,
            pos=px(0.64, 0.52),  # Moved to the right side of intersection
            scale=0.18,
            as_pedestrian=False,
            rotation=90  # Rotate for east-west orientation
        )
        
        # North-South pedestrian/cyclist traffic light
        self.tl_ped_ns = DrawableStoplicht(
            traffic_light=self.ctrl.ped_ns,
            pos=px(0.48, 0.36),
            scale=0.16,
            as_pedestrian=True,
            rotation=180  # Rotate 180 degrees to face south-to-north traffic
        )
        
        # East-West pedestrian/cyclist traffic light
        # Positioned next to the car light on the right side
        self.tl_ped_ew = DrawableStoplicht(
            traffic_light=self.ctrl.ped_ew,
            pos=px(0.64, 0.58),  # Next to car light (slightly lower)
            scale=0.16,
            as_pedestrian=True,
            rotation=90
        )
        
        self.traffic_lights = [self.tl_car_ns, self.tl_car_ew, self.tl_ped_ns, self.tl_ped_ew]

        # ====== BOAT ======
        # Create boat path in river area (right side) that goes under the bridge
        river_start_x = self.size[0] * 0.72  # River starts at 72% of screen width
        river_width = self.size[0] * 0.28
        river_center = river_start_x + river_width * 0.5
        
        # Simple path from bottom to top, passing under bridge
        boat_path = [
            (river_center, self.size[1] + 50),  # Start below screen
            (river_center, self.size[1] * 0.75),  # Quarter way up
            (river_center, self.size[1] * 0.5),   # Under bridge area
            (river_center, self.size[1] * 0.25),  # Three quarters up
            (river_center, -50)                   # End above screen
        ]
        
        self.boat = Boat(scale=1.0, path_px=boat_path, speed_px_s=80.0)
        self.boat_active = False  # Boat starts inactive
        
        # ====== BOAT BUTTON ======
        self.button_width = 120
        self.button_height = 40
        self.button_x = 20
        self.button_y = self.size[1] - self.button_height - 20
        self.button_rect = pg.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_font = pg.font.Font(None, 24)

        # Domain agents (all self-rendering)
        self.agents = []

        # Add initial agents for immediate visual
        for _ in range(2):
            self._add_agent(self.car_ns_spawner.factory())
            self._add_agent(self.car_ew_spawner.factory())

    def _add_agent(self, agent):
        # Check if spawn position is safe (no collision with existing vehicles)
        if self._is_safe_spawn_position(agent):
            agent.all_agents = self.agents
            self.agents.append(agent)
            return True
        return False
    
    def _is_safe_spawn_position(self, new_agent, min_spawn_distance=60):
        """
        Check if it's safe to spawn a new agent at its starting position.
        Returns True if safe, False if too close to existing vehicles.
        """
        if not self.agents:
            return True  # No existing agents, always safe
        
        new_pos = new_agent.pos
        
        # Get the size of the new agent for collision calculation
        if hasattr(new_agent, 'width') and hasattr(new_agent, 'length'):
            new_agent_size = max(getattr(new_agent, 'width', 50), getattr(new_agent, 'length', 80))
        else:
            new_agent_size = 25  # Default for pedestrians/cyclists
        
        for existing_agent in self.agents:
            if getattr(existing_agent, 'done', False):
                continue
            
            # Calculate distance to existing agent
            existing_pos = existing_agent.pos
            distance = math.hypot(existing_pos[0] - new_pos[0], existing_pos[1] - new_pos[1])
            
            # Get size of existing agent
            if hasattr(existing_agent, 'width') and hasattr(existing_agent, 'length'):
                existing_size = max(getattr(existing_agent, 'width', 50), getattr(existing_agent, 'length', 80))
            else:
                existing_size = 25
            
            # Calculate required safe distance based on both vehicle sizes (reduced multiplier)
            required_distance = max(min_spawn_distance, (new_agent_size + existing_size) * 1.0)  # Reduced from 1.5 to 1.0
            
            if distance < required_distance:
                return False  # Too close to spawn safely
        
        return True
    
    def _separate_colliding_vehicles(self):
        """
        Emergency function to separate vehicles that are too close to each other.
        This should rarely be needed if collision prevention is working correctly.
        """
        min_separation = 30.0  # Minimum distance between vehicle centers (reduced for closer spacing)
        
        for i in range(len(self.agents)):
            for j in range(i + 1, len(self.agents)):
                agent1 = self.agents[i]
                agent2 = self.agents[j]
                
                if (getattr(agent1, 'done', False) or getattr(agent2, 'done', False)):
                    continue
                
                # Calculate distance between agents
                dx = agent2.pos[0] - agent1.pos[0]
                dy = agent2.pos[1] - agent1.pos[1]
                distance = math.hypot(dx, dy)
                
                if distance < min_separation and distance > 0:
                    # Calculate separation vector
                    separation_needed = min_separation - distance
                    
                    # Normalize direction vector
                    nx = dx / distance
                    ny = dy / distance
                    
                    # Move agents apart (each moves half the required distance)
                    move_distance = separation_needed * 0.5
                    
                    agent1.pos[0] -= nx * move_distance
                    agent1.pos[1] -= ny * move_distance
                    agent2.pos[0] += nx * move_distance
                    agent2.pos[1] += ny * move_distance
                    
                    print(f"Separated vehicles: moved {move_distance:.1f}px each")

    def _draw_boat_button(self):
        """Draw the boat control button"""
        # Button colors
        if not self.boat_active:
            button_color = (0, 150, 0)  # Green when ready to start
            text_color = (255, 255, 255)
            button_text = "Start Boot"
        else:
            button_color = (150, 150, 150)  # Gray when boat is active
            text_color = (200, 200, 200)
            button_text = "Boot Actief"
        
        # Draw button background
        pg.draw.rect(self.screen, button_color, self.button_rect)
        pg.draw.rect(self.screen, (255, 255, 255), self.button_rect, 2)  # White border
        
        # Draw button text
        text_surface = self.button_font.render(button_text, True, text_color)
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def _draw_bridge_overlay(self):
        """Draw the bridge over the river (on top of boats)"""
        # Bridge parameters (same as in WorldRenderer)
        river_start_x = self.size[0] * 0.7
        river_width = self.size[0] * 0.3
        road_width = self.size[0] * 0.15
        bridge_thickness = road_width * 1.2
        bridge_y = self.size[1] / 2 - bridge_thickness / 2

        # Draw bridge crossing the river
        bridge_color = (80, 80, 80)  # Same as road color
        pg.draw.rect(self.screen, bridge_color,
                     (river_start_x, bridge_y, river_width, bridge_thickness))

        # Bridge railings (top and bottom)
        railing_color = (60, 60, 60)
        railing_height = int(max(2, bridge_thickness * 0.08))
        # top railing
        pg.draw.rect(self.screen, railing_color,
                     (river_start_x, bridge_y - railing_height, river_width, railing_height))
        # bottom railing
        pg.draw.rect(self.screen, railing_color,
                     (river_start_x, bridge_y + bridge_thickness, river_width, railing_height))

    def print_stats(self):
        """Print current simulation statistics."""
        stats = self.stats.get_summary()
        print("\n=== Simulation Statistics ===")
        print(f"Total vehicles spawned: {sum(stats['spawns'].values())}")
        print("Spawn counts by type:")
        for agent_type, count in stats['spawns'].items():
            print(f"  {agent_type}: {count}")
        print("Path completions by type:")
        for agent_type, count in stats['completions'].items():
            print(f"  {agent_type}: {count}")
        print("Frame exits by type:")
        for agent_type, count in stats['frame_exits'].items():
            print(f"  {agent_type}: {count}")
        print(f"Total collisions: {stats['collisions']}")
        print(f"Vehicles per minute: {stats['vehicles_per_minute']:.1f}")
        print("============================\n")

    def run(self):
        running = True
        last_stats_time = time.time()
        stats_interval = 30

        while running:
            dt = self.clock.tick(getattr(config, "FPS", 60)) / 1000.0

            # Periodic stats
            current_time = time.time()
            if current_time - last_stats_time >= stats_interval:
                self.print_stats()
                last_stats_time = current_time

            # Events
            for e in pg.event.get():
                if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                    running = False
                elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:  # Left mouse click
                    if self.button_rect.collidepoint(e.pos):
                        # Clicked on boat button
                        if not self.boat_active:
                            self.boat_active = True
                            self.boat.i = 0  # Reset to start of path
                            self.boat.pos = list(self.boat.path[0])  # Reset position
                            self.boat.done = False
                            if self.boat not in self.agents:
                                self.agents.append(self.boat)
                            print("Boot gestart via knop!")

            # Update traffic controller
            self.ctrl.update(dt)
            
            # Update traffic light visual states
            self.tl_car_ns.set_active(self.ctrl.cars_ns.state)
            self.tl_car_ew.set_active(self.ctrl.cars_ew.state)
            self.tl_ped_ns.set_active(self.ctrl.ped_ns.state)
            self.tl_ped_ew.set_active(self.ctrl.ped_ew.state)

            # Spawn new agents
            spawn_items = [
                (self.car_ns_spawner, self.cars_ns_up_px),
                (self.car_ew_spawner, self.cars_ew_right_px),  # Uncommented East-West cars
                (self.truck_ew_spawner, self.cars_ew_right_px),
                (self.bike_ns_spawner, self.bikes_ns_up_px),
                (self.ped_ew_spawner, self.peds_ew_right_px),
            ]

            # Limit total number of agents to prevent lag
            max_total_agents = 30
            
            for sp, path_px in spawn_items:
                # Only spawn if we haven't reached the limit
                if len(self.agents) < max_total_agents:
                    allow_spawn = lambda p=path_px: sum(
                        1 for a in self.agents
                        if getattr(a, "path", None) and a.path[0] == p[0] and not getattr(a, "done", False)
                        and ((a.pos[0]-p[0])**2 + (a.pos[1]-p[1])**2)**0.5 < 180
                    ) < 3  # Reduced from 4 to 3 per spawn point
                    new_agent = sp.update(dt, allow_spawn=allow_spawn)
                    if new_agent:
                        # Only add agent if spawn position is safe
                        if self._add_agent(new_agent):
                            self.stats.record_spawn(type(new_agent).__name__)
                        # If spawn position is not safe, the agent is discarded

            # Update agents
            for a in list(self.agents):
                a.update(dt)
                if getattr(a, "done", False):
                    # Remove agent from list first
                    self.agents.remove(a)
                    
                    # Special handling for boat
                    if isinstance(a, Boat):
                        self.boat_active = False
                        print("Boot heeft zijn reis voltooid! Klik op de groene knop om opnieuw te starten.")
                    else:
                        # Record completion based on the reason for non-boat agents
                        completion_reason = getattr(a, "completion_reason", "unknown")
                        if completion_reason == "frame_exit":
                            self.stats.record_frame_exit(type(a).__name__, getattr(a, "total_time", 0.0))
                        else:
                            self.stats.record_completion(type(a).__name__, getattr(a, "total_time", 0.0))

            # Check collisions with strict no-touch policy
            collisions = check_collisions(self.agents, min_dist=35.0)  # Increased to prevent any touching
            if collisions:
                self.stats.record_collision()
                # Log collision details for debugging
                print(f"WARNING: Vehicles too close! Total agents: {len(self.agents)}")
                # Attempt to separate colliding vehicles
                self._separate_colliding_vehicles()

            # === RENDER ===
            screen_fill_color = (40, 44, 52)
            
            # First draw basic background (without bridge)
            if self.background:
                # Draw everything except the bridge part
                temp_surface = self.background.copy()
                self.screen.blit(temp_surface, (0, 0))
            else:
                self.screen.fill(screen_fill_color)

            # Draw boat first (so it appears under the bridge)
            boat_agents = [agent for agent in self.agents if isinstance(agent, Boat)]
            for boat in boat_agents:
                boat.draw(self.screen)

            # Now draw the bridge on top of the boat
            self._draw_bridge_overlay()

            # Draw traffic lights 
            for traffic_light in self.traffic_lights:
                traffic_light.draw(self.screen)

            # Draw all other agents (cars, trucks, etc.)
            for agent in self.agents:
                if not isinstance(agent, Boat):
                    agent.draw(self.screen)

            # Draw boat control button
            self._draw_boat_button()
            
            # Draw status text if boat is active
            if self.boat_active and self.boat in self.agents and not self.boat.done:
                status_text = self.stats_font.render("Boot vaart onder de brug door!", True, (0, 255, 0))
                self.screen.blit(status_text, (10, 10))

            pg.display.flip()

        pg.quit()