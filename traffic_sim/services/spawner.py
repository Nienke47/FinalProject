from typing import List, Tuple, Optional, Dict, Any

Vec2 = Tuple[float, float]

# Safe imports: relative when packaged, fallback to absolute when run directly
try:
    from ..domain.actors.road_users import RoadUser
    from ..domain.actors.car import Car
    from ..domain.actors.truck import Truck
    from ..domain.actors.cyclist import Cyclist
    from ..domain.actors.pedestrian import Pedestrian
except ImportError:
    from traffic_sim.domain.actors.road_users import RoadUser
    from traffic_sim.domain.actors.car import Car
    from traffic_sim.domain.actors.truck import Truck
    from traffic_sim.domain.actors.cyclist import Cyclist
    from traffic_sim.domain.actors.pedestrian import Pedestrian


class Spawner:
    """Spawner helper and timed spawner in one.

    Two usages are supported:
    - As a simple factory: `s = Spawner(); car = s.spawn_car(path, ...)`
    - As a timed spawner used by the App: `s = Spawner(factory=..., interval_s=3.0, ...)`

    When used as a timed spawner, call `s.update(dt)` each frame — it will
    return a newly spawned RoadUser when it's time, or None otherwise.
    """

    def __init__(
        self,
        factory: Optional[callable] = None,
        interval_s: float = 1.0,
        random_offset: float = 0.0,
        max_count: Optional[int] = None,
    ):
        # Timed-spawner state
        self.factory = factory
        self.interval = float(interval_s)
        self.random_offset = float(random_offset)
        self.max_count = max_count
        self._acc = 0.0
        self._spawned = 0

    # --- Timed spawner API (used by App) ---
    def update(self, dt: float, allow_spawn: bool = True, **kwargs) -> Optional[RoadUser]:
        """Advance the spawner timer by dt seconds; spawn when interval elapsed.

        Returns the spawned RoadUser or None.
        """
        if self.factory is None:
            return None
        if self.max_count is not None and self._spawned >= self.max_count:
            return None

        # If caller temporarily disallows spawning, only advance internal time
        # but do not produce a new agent.
        if not allow_spawn:
            self._acc += dt
            return None

        self._acc += dt
        if self._acc + self.random_offset >= self.interval:
            # reset accumulator but keep overflow
            self._acc = max(0.0, self._acc - self.interval)
            self._spawned += 1
            try:
                return self.factory()
            except Exception:
                return None
        return None

    # --- Direct factory helpers (used by testapp.py and quick scripts) ---
    def spawn_car(self, path: List[Vec2], **kwargs) -> Car:
        return Car(path_px=path, **kwargs)

    def spawn_truck(self, path: List[Vec2], **kwargs) -> Truck:
        return Truck(path_px=path, **kwargs)

    def spawn_cyclist(self, path: List[Vec2], **kwargs) -> Cyclist:
        return Cyclist(path_px=path, **kwargs)

    def spawn_pedestrian(self, path: List[Vec2], **kwargs) -> Pedestrian:
        return Pedestrian(path_px=path, **kwargs)

    def spawn_by_type(self, kind: str, path: List[Vec2], **kwargs) -> Optional[RoadUser]:
        k = (kind or "").lower()
        if k == "car":
            return self.spawn_car(path, **kwargs)
        if k == "truck":
            return self.spawn_truck(path, **kwargs)
        if k in ("cyclist", "bike", "bicycle"):
            return self.spawn_cyclist(path, **kwargs)
        if k in ("pedestrian", "ped"):
            return self.spawn_pedestrian(path, **kwargs)
        return None

    def spawn_batch(self, specs: List[Dict[str, Any]]) -> List[RoadUser]:
        results: List[RoadUser] = []
        for s in specs:
            kind = s.get("kind", "")
            path = s.get("path", [])
            ctor_kwargs = {k: v for k, v in s.items() if k not in ("kind", "path")}
            obj = self.spawn_by_type(kind, path, **ctor_kwargs)
            if obj is not None:
                results.append(obj)
        return results

__all__ = ["Spawner"]