# src/traffic_sim/main.py
import sys
from pathlib import Path

if __name__ == "__main__":
    src_path = Path(__file__).resolve().parents[1]
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
try:
    from .core.testapp import App
except ImportError:
    from traffic_sim.core.testapp import App

if __name__ == "__main__":
    App().run()
