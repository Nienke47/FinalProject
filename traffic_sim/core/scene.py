# src/traffic_sim/core/scene.py
from __future__ import annotations
from typing import List, Optional
import pygame as pg

class Scene:
    """
    Basis voor een 'scherm' in je applicatie (menu, simulatie, pauze, ...).
    Subclasses implementeren: handle_event, update, render.
    """
    def __init__(self, manager: "SceneManager"):
        self.manager = manager
        self.is_paused = False   # handig voor overlays

    # Lifecycle hooks
    def on_enter(self, prev: Optional["Scene"]):  # aangeroepen als scene actief wordt
        pass

    def on_exit(self, nxt: Optional["Scene"]):    # aangeroepen als scene verlaat
        pass

    def on_pause(self):    # aangeroepen als er een overlay bovenop komt (push)
        self.is_paused = True

    def on_resume(self):   # aangeroepen als overlay verdwijnt (pop)
        self.is_paused = False

    # Main API
    def handle_event(self, event: pg.event.Event):
        """Verwerk input (toetsen/muis)."""
        pass

    def update(self, dt: float):
        """Werk logica bij. Houd rekening met self.is_paused indien nodig."""
        pass

    def render(self, screen: pg.Surface):
        """Teken de scene."""
        pass


class SceneManager:
    """
    Stapel van scenes. Bovenste scene is actief.
    Je kunt overlays (bv. pauzemenu) pushen bovenop de simulatie.
    """
    def __init__(self):
        self._stack: List[Scene] = []

    def current(self) -> Optional[Scene]:
        return self._stack[-1] if self._stack else None

    def push(self, scene: Scene):
        # Pauseer huidige (overlay komt erbovenop)
        if self._stack:
            self._stack[-1].on_pause()
        self._stack.append(scene)
        scene.on_enter(prev=self._stack[-2] if len(self._stack) > 1 else None)

    def pop(self) -> Optional[Scene]:
        if not self._stack:
            return None
        top = self._stack.pop()
        nxt = self._stack[-1] if self._stack else None
        top.on_exit(nxt=nxt)
        if nxt:
            nxt.on_resume()
        return top

    def switch(self, scene: Scene):
        """Vervang huidige scene door een nieuwe (geen overlay)."""
        prev = self._stack.pop() if self._stack else None
        if prev:
            prev.on_exit(nxt=scene)
        self._stack.append(scene)
        scene.on_enter(prev=prev)

    # Doorsturen naar actieve scene
    def handle_event(self, event: pg.event.Event):
        cur = self.current()
        if cur:
            cur.handle_event(event)

    def update(self, dt: float):
        cur = self.current()
        if cur:
            cur.update(dt)

    def render(self, screen: pg.Surface):
        """
        Render *alle* scenes zodat overlays transparant kunnen tekenen.
        Als je alleen de top-scene wilt tekenen, teken dan alleen self.current().
        """
        for scn in self._stack:
            scn.render(screen)
