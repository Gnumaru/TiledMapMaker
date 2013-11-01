#! /usr/bin/env python2.7
# coding: utf-8
# Filename  : Image2Map.py
# Authors   : Georg Muntingh and Bjorn Lindeijer
# Version   : 1.2
# Date      : June 16, 2010
# Copyright : Public Domain

import Image;
import os;
import sys;

class TileMap:
    """ This class represents a tiledMap of tiles.
    """
    
    FullTileMap = None;
    G = None;
    mapHeightInTiles = None;
    MapImage = None;
    mapHeightInPixels = None;
    mapWidthInPixels = None;
    MapList = None;
    TileDict = None;
    TileImage = None;
    TileList = None;
    tileWidth = None;
    tileHeight = None;
    mapWidthInTiles = None;
    graphFromList = None;

    def __init__(self, imageFileName, tileWidth, tileHeight):
        # For initialization, tiledMap image with filename imageFileName should be specified, together with the
        # tile size (tile X, tileHeight). First we set the tile sizes.
        self.tileWidth, self.tileHeight = tileWidth, tileHeight

        # Open the tiledMap and find its attributes.
        print("Opening the tiledMap image imageFileName: " + imageFileName)
        self.MapImage = Image.open(imageFileName)
        # self.MapImage.size is a tuple, hence the double atribution below
        self.mapWidthInPixels, self.mapHeightInPixels = self.MapImage.size
        self.mapWidthInTiles, self.mapHeightInTiles = int(self.mapWidthInPixels / self.tileWidth), int(self.mapHeightInPixels / self.tileHeight)

        # Store the unique tiles in a list and a hash, and the tiledMap in a list.
        self.MapList, self.TileList, self.TileDict = self.parseMap()

    def parseMap(self):
        """ This function takes the tiledMap image, and obtains
            * a list TList of unique tiles.
            * a hash TDict of unique tiles.
            * a double list self.MapList of where an entry equals i if
                self.TileList[i] is the corresponding picture on the tiledMap image.
        """

        MList = [[-1 for i in range(self.mapWidthInTiles)] for j in range(self.mapHeightInTiles)]  # TODO: Make this a single list
        TList = []
        TDict = {}
        progress = -1
        print("Parsing the Map: ")

        # Jump through the tiledMap image in 8 currentColumn 8-tile steps. In each step:
        #  * If the string of the tile is in the dictionary, place its value in tiledMap list MList[currentRow][currentColumn].
        #  * Otherwise, add this tile to the list, and add its string to the dictionary with value "the
        #    number of elements in the list". Also place this value in MList[currentRow][currentColumn].
        for currentRow in range(self.mapHeightInTiles):
            for currentColumn in range(self.mapWidthInTiles):
                box = self.tileWidth * currentColumn, self.tileHeight * currentRow, self.tileWidth * (currentColumn + 1), self.tileHeight * (currentRow + 1)
                tile = self.MapImage.crop(box)
                s = tile.tostring()

                if TDict.has_key(s):
                    MList[currentRow][currentColumn] = TDict[s]
                else:
                    TList.append(tile)
                    TDict[s] = len(TList)
                    MList[currentRow][currentColumn] = len(TList)

                # Calculate the progress, and print(it to the screen.
                p = ((currentColumn + currentRow * self.mapWidthInTiles) * 100) / (self.mapWidthInTiles * self.mapHeightInTiles)
                if progress != p:
                    progress = p
                    self.printProgress(progress)

        self.printProgress(100)
        print("Done!")
        
        
        
        
        
#         self.TileImage = Image.new("RGB", (len(TList) * self.tileWidth, self.tileHeight))
#         for i in range(len(TList)):
#             lowerLeft = (i * self.tileWidth, 0)  # formato da coordenada: (x, y).  
#             upperRight = ((i + 1) * self.tileWidth, self.tileHeight)  # formato da coordenada: (x, y)
# #             Valor inicial eé inclusivo, valor final e exclusivo. Ex.: Certo: (0, 0, 16, 16). Errado:(0, 0, 15, 15) 
#             self.TileImage.paste(TList[i].convert("RGB"), lowerLeft + upperRight)
        
        
        
        
        
        widthInPixels, heightInPixels = self.getImageGeometry(len(TList));
        self.TileImage = Image.new("RGB", self.getImageGeometry(len(TList)));
         
        widthInTiles = widthInPixels / self.tileWidth;
        heightInTiles = heightInPixels / self.tileHeight;
         
        listIndex = 0;
        listLength = len(TList);
        for row in range(heightInTiles):
            if listIndex < listLength:
                for column in range(widthInTiles):
                    if listIndex < listLength:
#                         Pode parecer que não está certo, mas os tiles são colados da esquerda pra direita, de cima pra baixo...
                        lowerLeft = (column * self.tileWidth, row * self.tileHeight);  # formato da coordenada: (x, y)
                        upperRight = ((column + 1) * self.tileWidth, (row + 1) * self.tileHeight);  # formato da coordenada: (x, y)
                        self.TileImage.paste(TList[listIndex].convert("RGB"), lowerLeft + upperRight)
                        listIndex += 1;
                    else:
                        break;
            else:
                break;

        return MList, TList, TDict
    
    def getImageGeometry(self, tileNumber):
        """ Calculate the optimal geometry for the tile set, and return it as a tuple
        """
        width = tileNumber * self.tileWidth;
        optimalHeight = self.tileHeight;
        # Since (tileNumber * self.tileWidth) may not be a power of 2, we start
        # with an optimal width of 2 and keep growing until it surpasses the
        # original width
        optimalWidth = 2;
        while optimalWidth < width:
            optimalWidth *= 2;

        while optimalWidth > optimalHeight:
            optimalWidth /= 2;
            optimalHeight *= 2;
        
        return (optimalWidth, optimalHeight);
    
    def printProgress(self, percentage):
        """ This function prints the percentage on the current row after erasing what is already there.
        """
        print('%s\r' % ' ' * 20,)  # clean up row
        print('%3d%% ' % percentage,)  # ending with comma prevents newline from being appended
        sys.stdout.flush()

    def printHash(self, H):
        """ This function nicely aligns dictionaries with elements of the form
            "(y, x): n" in a table, in which row y, column x has entry n.

            In this specific case (x, y) will be the tile coordinates at which
            tile n will be placed in the tile image.
        """

        Xmin = min([ h[1] for h in H.keys() ])
        Xmax = max([ h[1] for h in H.keys() ])
        Ymin = min([ h[0] for h in H.keys() ])
        Ymax = max([ h[0] for h in H.keys() ])

        # Find the number of symbols we need to write down the tile numbers.
        D = len(str(max(H.values())))

        st = ""
        for i in range(Ymin, Ymax + 1):
            for j in range(Xmin, Xmax + 1):

                if not (i, j) in H:
                    st = st + "|"
                    for k in range(D):
                        st = st + "."
                else:
                    h = H[(i, j)]
                    d = len(str(h))

                    st = st + "|"
                    for k in range(D - d):
                        st = st + "."

                    st = st + str(h)

            st = st + "|\n"

        print(st)

    def addEdge(self, s, t, dirr):
        """ This function increases abs(value) of an edge st in a graph G, taking the
            'direction' of st into account.

                s: a start vertex
                t: an end  vertex
              dir: a value depicting the st-direction,
                        +1 for left -> right
                        -1 for up   -> down
        """

        if self.G.has_edge(s, t):
            values = [ value for value in self.G.edge[s][t] if (dirr * value) > 0 ]
        else:
            values = []

        if values:
            self.G.remove_edge(s, t, values[0])  # increase the value by 1
            self.G.add_edge(s, t, values[0] + dirr)
        else:
            self.G.add_edge(s, t, dirr)  # create a dir-valued edge

    def centerOfDictionary(self, H):
        """ Returns the center of the dictionary, that is, the average of all keys.
        """

        L = H.keys()
        return [ int(round(sum([l[1] for l in L]) / (len(L) + 0.0))), \
                 int(round(sum([l[0] for l in L]) / (len(L) + 0.0))) ]

def main(sys):
    if sys.argv[1] in ("-h", "--help"):
        print("Usage  : python Image2Map.py [tileWidth] [tileHeight] files...")
        print("Example: python Image2Map.py 8 8 Sewers.png Caves.png")
    elif len(sys.argv) < 4:
        print("Error  : You specified too few arguments!\n")
        print("Usage  : python Image2Map.py [tileWidth] [tileHeight] files...")
        print("Example: python Image2Map.py 8 8 Sewers.png Caves.png")
    else:
        sys.argv[3] = os.path.dirname(os.path.abspath(__file__)) + "/" + sys.argv[3];
        tileWidth, tileHeight = int(sys.argv[1]), int(sys.argv[2])

        for imageFile in sys.argv[3:]:
            tiledMap = TileMap(imageFile, tileWidth, tileHeight)
    
            tilefile = os.path.splitext(imageFile)[0] + "-Tileset" + ".png"
            print("Saving the tileset image into the imageFile: " + tilefile)
            tiledMap.TileImage.save(tilefile, "PNG")
    
#             print("Pretty-printing the tileset:" + "\n")
#             tiledMap.printHash(tiledMap.FullTileMap)

if __name__ == '__main__':
    main(sys);
