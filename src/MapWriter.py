#! /usr/bin/env python2.7
# coding: utf-8
# Filename  : MapWriter.py
# Authors   : Bjorn Lindeijer and Georg Muntingh
# Version   : 1.1
# Date      : April 29, 2008
# Copyright : Public Domain

import Image
import base64
import os
import struct
import sys
from xml.dom.minidom import Document


class Tileset:
    """ This class represents a set of tiles.
    """

    def __init__(self, tileImageFile, tileWidth, tileHeight):
        self.TileWidth = tileWidth
        self.TileHeight = tileHeight
        self.Filename = tileImageFile
        self.Name = os.path.splitext(tileImageFile)[0]
        self.List = []
        self.TileDict = {}
        self.readTiles()

    def readTiles(self):
        """ This method reads the tiles from the tileset and also fills up the tile dictionary.
        """
        TileImage = Image.open(self.Filename).convert("RGB")
        TileIW, TileIH = TileImage.size
        TilesetW, TilesetH = TileIW / self.TileWidth, TileIH / self.TileHeight

        for y in range(TilesetH):
            for x in range(TilesetW):
                box = self.TileWidth * x, self.TileHeight * y, self.TileWidth * (x + 1), self.TileHeight * (y + 1)
                tile = TileImage.crop(box)
                self.List.append(tile)

                tileString = tile.tostring()
                if not self.TileDict.has_key(tileString):
                    self.TileDict[tileString] = len(self.List) - 1

    def findTile(self, tileImage):
        """ This method returns the tile index for the given tile image if it is part of this tileset,
            and returns 0 if the tile could not be found. Constant complexity due to dictionary lookup.
        """
        tileString = tileImage.tostring()
        if self.TileDict.has_key(tileString):
            return self.TileDict[tileString] + 1
        else:
            return 0

class TileMap:
    """ This class represents a tile tiledMap.
    """

    def __init__(self, mapImageFile, tileSet, tileWidth, tileHeight):
        self.mapImageFile = mapImageFile
        self.TileWidth = tileWidth
        self.TileHeight = tileHeight
        self.TileSet = tileSet
        self.List = []
        self.readMap()

    def readMap(self):
        """ This function takes the tiledMap image, and obtains a list self.List, where
            an entry equals i if self.TileSet.List[i-1] is the corresponding picture on the tiledMap
            image. If a matching tile is not found, i is set to 0.
        """
        MapImage = Image.open(self.mapImageFile).convert("RGB")
        MapImageWidth, MapImageHeight = MapImage.size
        self.Width, self.mapHeightInTiles = MapImageWidth / self.TileWidth, MapImageHeight / self.TileHeight
        progress = -1

        for y in range(self.mapHeightInTiles):
            for x in range(self.Width):
                box = self.TileWidth * x, self.TileHeight * y, self.TileWidth * (x + 1), self.TileHeight * (y + 1)
                tile = MapImage.crop(box)
                self.List.append(self.TileSet.findTile(tile))

                # Calculate the progress, and print(it to the screen.
                p = ((x + y * self.Width) * 100) / (self.Width * self.mapHeightInTiles)
                if progress != p:
                    progress = p
                    self.printProgress(progress)

        self.printProgress(100)

    def printProgress(self, percentage):
        """ This function prints the percentage on the current row after erasing what is already there.
        """
        print('%s\r' % ' ' * 20,)  # clean up row
        print('%3d%% ' % percentage,)  # ending with comma prevents newline from being appended
        sys.stdout.flush()

    def write(self, fileName):
        doc = Document()
        tiledMap = doc.createElement("map")
        tiledMap.setAttribute("version", "0.99b")
        tiledMap.setAttribute("orientation", "orthogonal")
        tiledMap.setAttribute("width", str(self.Width))
        tiledMap.setAttribute("height", str(self.mapHeightInTiles))
        tiledMap.setAttribute("tilewidth", str(self.TileWidth))
        tiledMap.setAttribute("tileheight", str(self.TileHeight))
        tileset = doc.createElement("tileset")
        tileset.setAttribute("name", self.TileSet.Name)
        tileset.setAttribute("firstgid", str(1))
        tileset.setAttribute("tilewidth", str(self.TileSet.TileWidth))
        tileset.setAttribute("tileheight", str(self.TileSet.TileHeight))
        image = doc.createElement("image")
        image.setAttribute("source", self.TileSet.Filename)
        tileset.appendChild(image)
        tiledMap.appendChild(tileset)
        layer = doc.createElement("layer")
        layer.setAttribute("name", "Ground")
        layer.setAttribute("width", str(self.Width))
        layer.setAttribute("height", str(self.mapHeightInTiles))
        data = doc.createElement("data")

        data.setAttribute("encoding", "base64")
        TileData = ""
        for tileId in self.List:
            TileData = TileData + struct.pack("<l", tileId)  # pack the tileId into a long
        b64data = doc.createTextNode(base64.b64encode(TileData))
        data.appendChild(b64data)

        layer.appendChild(data)
        tiledMap.appendChild(layer)
        doc.appendChild(tiledMap)
        fileToBeWritten = open(fileName, "w")
        fileToBeWritten.write(doc.toprettyxml(indent=" "))
        fileToBeWritten.close()

def printHelp():
    print("Usage  : python Image2Map.py [tileX] [tileY] <tiledMap image file> <tileset file>");
    print("Example: python MapWriter.py 8 8 JansHouse.png JansHouse-Tileset.png");

def main(sys):
    if len(sys.argv) != 1:
        if len(sys.argv) == 4:
            sys.argv.append(sys.argv[3][:-4] + "-Tileset.png");
        if sys.argv[1] in ("-h", "--help"):
            printHelp();
        elif len(sys.argv) < 5:
            printHelp();
        else:
            tileX, tileY = int(sys.argv[1]), int(sys.argv[2]);
            mapImageFile, tileImageFile = sys.argv[3], sys.argv[4];
            tiledMap = TileMap(mapImageFile, Tileset(tileImageFile, tileX, tileY), tileX, tileY);
            tiledMap.write(os.path.splitext(mapImageFile)[0] + ".tmx");
    else:
        printHelp();

if __name__ == '__main__':
    main(sys);
