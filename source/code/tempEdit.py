from importlib import reload
import tempEditLib
reload(tempEditLib)

from tempEditLib import TempEditGlyphs
from mojo.roboFont import OpenWindow

OpenWindow(TempEditGlyphs)
