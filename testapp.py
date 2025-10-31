# src/traffic_sim/core/app.py
import pygame as pg
import time
from pathlib import Path
import time
import sys
import random

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

        # Domain agents (all self-rendering)
        self.agents = []

        # Add initial agents for immediate visual
        for _ in range(2):
            self._add_agent(self.car_ns_spawner.factory())
            self._add_agent(self.car_ew_spawner.factory())

    def _add_agent(self, agent):
        agent.all_agents = self.agents
        self.agents.append(agent)

    def print_stats(self):
        """Print current simulation statistics."""
        stats = self.stats.get_summary()
        print("\n=== Simulation Statistics ===")
        print(f"Total vehicles spawned: {sum(stats['spawns'].values())}")
        print("Spawn counts by type:")
        for agent_type, count in stats['spawns'].items():
            print(f"  {agent_type}: {count}")
        print("Average completion times:")
        for agent_type, avg_time in stats['average_completion_times'].items():
            print(f"  {agent_type}: {avg_time:.1f}s")
        print("Traffic light wait times:")
        print(f"  North-South: {stats['average_wait_times']['NS']:.1f}s")
        print(f"  East-West: {stats['average_wait_times']['EW']:.1f}s")
        print(f"Total collisions: {stats['collisions']}")
        print("Throughput (completions per minute):")
        for agent_type, rate in stats['throughput'].items():
            print(f"  {agent_type}: {rate:.1f}/min")
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
                # (self.car_ew_spawner, self.cars_ew_right_px),
                (self.truck_ew_spawner, self.cars_ew_right_px),
                (self.bike_ns_spawner, self.bikes_ns_up_px),
                (self.ped_ew_spawner, self.peds_ew_right_px),
            ]

            for sp, path_px in spawn_items:
                allow_spawn = lambda p=path_px: sum(
                    1 for a in self.agents
                    if getattr(a, "path", None) and a.path[0] == p[0] and not getattr(a, "done", False)
                    and ((a.pos[0]-p[0])**2 + (a.pos[1]-p[1])**2)**0.5 < 180
                ) < 4
                new_agent = sp.update(dt, allow_spawn=allow_spawn)
                if new_agent:
                    self._add_agent(new_agent)
                    self.stats.record_spawn(type(new_agent).__name__)

            # Update agents
            for a in list(self.agents):
                a.update(dt)
                if getattr(a, "done", False):
                    self.agents.remove(a)
                    self.stats.record_completion(type(a).__name__, getattr(a, "total_time", 0.0))

            # Check collisions
            collisions = check_collisions(self.agents, min_dist=15.0)
            if collisions:
                self.stats.record_collision()

            # === RENDER ===
            screen_fill_color = (40, 44, 52)
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(screen_fill_color)

            # Draw traffic lights first (so they appear behind vehicles if needed)
            for traffic_light in self.traffic_lights:
                traffic_light.draw(self.screen)

            # Draw all agents (self-rendering)
            for agent in self.agents:
                agent.draw(self.screen)

            pg.display.flip()

        pg.quit()