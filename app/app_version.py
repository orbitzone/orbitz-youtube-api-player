"""Version shared by source checkouts and installed bundles."""
from pathlib import Path

VERSION = (Path(__file__).resolve().parents[1] / 'VERSION').read_text().strip()
