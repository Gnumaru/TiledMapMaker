TiledMapMaker
=============

Fork from the original Image2Map.py and MapWriter.py scripts, explained here:

https://github.com/bjorn/tiled/wiki/Import-from-Image

The original Image2Map.py generates a square image. It may be fine for some uses, but OpenGL may require an image whose dimensions are power of two. This modified version of Image2Map.py generates a TileSet whose dimensions are strictly a power of two.

I made this because I'm developing a game using LibGDX and it complains when loading an image that does not have dimensions as powers of two.
