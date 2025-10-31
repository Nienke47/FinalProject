# src/traffic_sim/core/app.py
import pygame as pg
from pathlib import Path
import sys

if __name__ == "__main__":
    src_path = Path(__file__).resolve().parents[2]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from ..configuration import config
from ..render.draw_world import draw
from ..render.entities import make_view
from ..domain.world.intersection import Controller
from ..domain.actors.car import Car
from ..domain.actors.cyclist import Cyclist
from ..domain.actors.pedestrian import Pedestrian
from ..services.pathing import (
    to_pixels,
    CARS_NS_UP, CARS_EW_RIGHT,
    BIKES_NS_UP,
    PEDS_EW_RIGHT,
)
from ..services.spawner import Spawner
from ..services.physics import check_collisions
from ..domain.world.traffic_light import Light            # status enum
from ..render.draw_traffic_light import DrawableStoplicht # visuele stoplichten


def load_background(path: Path):
    try:
        if path.exists():
            return pg.image.load(str(path)).convert()
    except Exception:
        pass
    return None


class App:
    def __init__(self):
        pg.init()
        self.size = (config.WIDTH, config.HEIGHT)
        self.screen = pg.display.set_mode(self.size)
        pg.display.set_caption(getattr(config, "TITLE", "Traffic Sim"))
        self.clock = pg.time.Clock()

        # Achtergrond (kruispunt-afbeelding)
        self.background = load_background(config.ASSETS / "backgrounds" / "background.png")

        # Verkeerscontroller (stoplichten/fasen)
        self.ctrl = Controller()
                # --- STOPLICHTEN POSITIES (genormaliseerd) ---
        def px(nx: float, ny: float):  # helper: 0..1 -> pixels
            return int(nx * self.size[0]), int(ny * self.size[1])

        self.tl_views = []

        # Auto-lichten (NS en EW) – zet ze dicht bij de rijbaan
        self.tl_car_ns = DrawableStoplicht(center=px(0.52, 0.36), scale=0.18)  # noord/zuid
        self.tl_car_ew = DrawableStoplicht(center=px(0.36, 0.52), scale=0.18)  # oost/west

        # Voetganger/fiets-lichten (NS en EW) – zet ze bij voetpad/fietspad
        self.tl_ped_ns = DrawableStoplicht(center=px(0.48, 0.36), scale=0.16, as_pedestrian=True)
        self.tl_ped_ew = DrawableStoplicht(center=px(0.36, 0.48), scale=0.16, as_pedestrian=True)

        self.tl_views.extend([self.tl_car_ns, self.tl_car_ew, self.tl_ped_ns, self.tl_ped_ew])


        # ====== ROUTES → PIXELS ======
        cars_ns_up_px     = to_pixels(CARS_NS_UP,     *self.size)  # auto: Zuid -> Noord
        cars_ew_right_px  = to_pixels(CARS_EW_RIGHT,  *self.size)  # auto: West -> Oost
        bikes_ns_up_px    = to_pixels(BIKES_NS_UP,    *self.size)  # fiets: Zuid -> Noord
        peds_ew_right_px  = to_pixels(PEDS_EW_RIGHT,  *self.size)  # voetganger: West -> Oost

        # ====== SPAWNERS ======
        self.car_ns_spawner = Spawner(
            factory=lambda: Car(cars_ns_up_px, speed_px_s=130, can_cross_ok=self.ctrl.can_cars_cross_ns),
            interval_s=3.0, random_offset=1.0, max_count=50
        )
        self.car_ew_spawner = Spawner(
            factory=lambda: Car(cars_ew_right_px, speed_px_s=130, can_cross_ok=self.ctrl.can_cars_cross_ew),
            interval_s=4.0, random_offset=1.5, max_count=50
        )
        self.bike_ns_spawner = Spawner(
            factory=lambda: Cyclist(bikes_ns_up_px, speed_px_s=90, can_cross_ok=self.ctrl.can_ped_cross_ns),
            interval_s=5.0, random_offset=1.0, max_count=30
        )
        self.ped_ew_spawner = Spawner(
            factory=lambda: Pedestrian(peds_ew_right_px, speed_px_s=70, can_cross_ok=self.ctrl.can_ped_cross_ew),
            interval_s=4.0, random_offset=1.0, max_count=40
        )

        # Domain-agents + hun Views (tekenlaag)
        self.agents = []
        self.views  = []

        # Optioneel: paar startagents zodat je meteen iets ziet
        for _ in range(2):
            self._add_agent(self.car_ns_spawner.factory())
            self._add_agent(self.car_ew_spawner.factory())
        # Uncomment als je direct een fietser/voetganger wilt zien:
        # self._add_agent(self.bike_ns_spawner.factory())
        # self._add_agent(self.ped_ew_spawner.factory())

    def _add_agent(self, agent):
        self.agents.append(agent)
        self.views.append(make_view(agent))  # koppelt renderlaag aan domain-agent

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(getattr(config, "FPS", 60)) / 1000.0

            # === EVENTS ===
            for e in pg.event.get():
                if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                    running = False

            # === UPDATE LOGICA ===
            # 1) Stoplichten/fasen
            self.ctrl.update(dt)
            # --- STOPLICHTEN STATUS DOORZETTEN NAAR VIEW ---
            # Je kunt direct de Light-state gebruiken van de controller:
            self.tl_car_ns.set_active(self.ctrl.cars_ns.state)
            self.tl_car_ew.set_active(self.ctrl.cars_ew.state)
            self.tl_ped_ns.set_active(self.ctrl.ped_ns.state)
            self.tl_ped_ew.set_active(self.ctrl.ped_ew.state)


            # 2) Nieuwe agents spawnen
            for sp in (self.car_ns_spawner, self.car_ew_spawner, self.bike_ns_spawner, self.ped_ew_spawner):
                new_agent = sp.update(dt)
                if new_agent:
                    self._add_agent(new_agent)

            # 3) Agents updaten & afronden
            for a in list(self.agents):
                a.update(dt)
                if getattr(a, "done", False):
                    idx = self.agents.index(a)
                    self.agents.pop(idx)
                    self.views.pop(idx)

            # 4) (Optioneel) eenvoudige collision proximity check
            _collision = check_collisions(self.agents, min_dist=15.0)
            # if _collision: print("Collision proximity!")  # debug

            # === RENDER ===
            draw(self.screen, self.background, self.views)
            pg.display.flip()
                        # === RENDER ===
            all_views = [*self.tl_views, *self.views]  # eerst stoplichten, dan verkeer
            draw(self.screen, self.background, all_views)
            pg.display.flip()


        pg.quit()

