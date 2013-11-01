#! /usr/bin/env python2.7
# coding: utf-8
# Filename  : Image2Map.py
# Authors   : Georg Muntingh and Bjorn Lindeijer
# Version   : 1.2
# Date      : June 16, 2010
# Copyright : Public Domain

import Image;
import networkx;
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

        # Create a graph that contains the information that is relevant for the article.
        self.graphFromList()

        # We create a dictionary self.FullTileMap whose keys will be the coordinates
        # for the image of unique tiles, and the values are the unique tile numbers.
        self.FullTileMap = {}

        # Extract maximal components from G into the dictionary TileMap, and combine them
        # into self.FullTileMap using a method that places them as close to each other as
        # possible.
        while self.G.nodes() != []:
            v = self.G.nodes()[0]
            TileMap, K = self.growTileMap({(0, 0): v}, self.G, 0, 0, v)
            self.FullTileMap = self.composeDictionaries(self.FullTileMap, TileMap)
            self.G.remove_nodes_from(TileMap.values())

        # Create an image imageFileName from our tiledMap of unique tiles.
        self.TileImage = self.getTileImage()

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
        
        return MList, TList, TDict

    def printProgress(self, percentage):
        """ This function prints the percentage on the current row after erasing what is already there.
        """
        print('%s\r' % ' ' * 20,)  # clean up row
        print('%3d%% ' % percentage,)  # ending with comma prevents newline from being appended
        sys.stdout.flush()

    def getTileImage(self):
        """ This function takes the hash of unique tiles self.FullTileMap and
            creates a tileset image from it.
        """

        H = self.FullTileMap

        Xmin = min([ h[1] for h in H.keys() ])
        Xmax = max([ h[1] for h in H.keys() ])
        Ymin = min([ h[0] for h in H.keys() ])
        Ymax = max([ h[0] for h in H.keys() ])
        
        xSize = self.tileWidth * (Xmax - Xmin + 1)
        ySize = self.tileHeight * (Ymax - Ymin + 1)
        
        xSizeInPowerOfTwo = 2
        ySizeInPowerOfTwo = 2
        
        while xSizeInPowerOfTwo < xSize:
            xSizeInPowerOfTwo *= 2
        xSizeInPowerOfTwo /= 2
        
        while ySizeInPowerOfTwo < ySize:
            ySizeInPowerOfTwo *= 2
            
#         print("xSize: " + str(xSize) + ", ySize: " + str(ySize))
#         print("xSizeInPowerOfTwo: " + str(xSizeInPowerOfTwo) + ", ySizeInPowerOfTwo: " + str(ySizeInPowerOfTwo))

#         TileImage = Image.new("RGB", (self.tileWidth * (Xmax - Xmin + 1), self.tileHeight * (Ymax - Ymin + 1)))
        TileImage = Image.new("RGB", (xSize, ySize))
#         TileImage = Image.new("RGB", (xSizeInPowerOfTwo, ySizeInPowerOfTwo))
        
        for currentRow in range(Ymin, Ymax + 1):
            for currentColumn in range(Xmin, Xmax + 1):
                if (currentRow, currentColumn) in H:
                    box = (self.tileWidth * (currentColumn - Xmin)    , self.tileHeight * (currentRow - Ymin), \
                            self.tileWidth * (currentColumn - Xmin + 1), self.tileHeight * (currentRow - Ymin + 1)) 
                    TileImage.paste(self.TileList[H[(currentRow, currentColumn)] - 1].convert("RGB"), box)
            
        return TileImage

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

    def graphFromList(self):
        """ This function constructs a weighted directed graph from the 
            list that depicts the tiledMap using the following scheme:
                Left A, Right B -> add (A, B, 1)
                Left B, Right A -> add (B, A, 1)
                Up   A, Down  B -> add (A, B,-1)
                Up   B, Down  A -> add (B, A,-1)
            We then add all similar edges together, so for instance
                (A, B, 1) and (A, B,  1) -> (A, B, 2)
            but *NOT*
                (A, B, 1) and (A, B, -1) -> (A, B, 0)
        """

        self.G = networkx.MultiDiGraph(selfloops=False, multiedges=True)
        L = self.MapList
        progress = -1
        print("Generating the graph: ")

        # Now add for every Cartesian crossing an edge (or a value) in G
        for i in range(len(L) - 1):
            for j in range(len(L[0]) - 1):
                self.addEdge(L[i][j], L[i][j + 1], 1)  # L-R, +1
                self.addEdge(L[i][j], L[i + 1][j], -1)  # U-D, -1

                # Calculate the progress, and print(it to the screen.
                p = ((j + i * len(L)) * 100) / (len(L) * len(L[0]))
                if progress != p:
                    progress = p
                    self.printProgress(progress)

        # What remains is the bottom and right line of edges:
        for j in range(len(L[0]) - 1):
            self.addEdge(L[len(L) - 1][j], L[len(L) - 1][j + 1], 1)

        for i in range(len(L) - 1):
            self.addEdge(L[i][len(L[0]) - 1], L[i + 1][len(L[0]) - 1], -1)

        # Now show 100% progress and say we're done.
        self.printProgress(100)
        print("Done!")


    def growTileMap(self, TileMap, G, posX, posY, curV):
        """ This is a recursive function that arranges a tiledMap of unique tiles.
        """

        # For each of the directions, make a possible edge-list to choose from,
        # and combine them into one list Edges such that Edges[i] stands
        # for the edges with direction code i, where
        #       0 <-> up
        #       1 <-> right
        #       2 <-> down
        #       3 <-> left
        LL = [e for e in G.in_edges(curV)  if e[1] > 0]
        LU = [e for e in G.in_edges(curV)  if e[1] < 0]
        LR = [e for e in G.out_edges(curV) if e[1] > 0]
        LD = [e for e in G.out_edges(curV) if e[1] < 0]
        Edges = [LU, LR, LD, LL]

        # We want to visit all directions such that we visit the direction with
        # the smallest amount of possible tiles first. This is because these tiles
        # will have the smallest probability to fit in at a later stage. It will
        # also embed blocks of tiles that appear only in one configuration
        # (pictures chopped up in tiles).
        directory = [ [ Edges[i], i ] for i in range(4)]
        directory.sort(cmp=lambda L1, L2: len(L1[0]) - len(L2[0]))
        directory = [ x[1] for x in directory]

        while directory != []:
            direction = directory[0]

            if Edges[direction] != []:
                E = Edges[direction]

                # Now order E with respect to the values of its edges. This will
                # make the algorithm start with a combination that appears most
                # often in the graph, which is a measure for how much two tiles
                # "belong together".
                E.sort(cmp=lambda e, f: abs(e[1]) - abs(f[1]), reverse=True)

                # Now walk through E until you find an edge that fits with
                # the previously placed tiles in TileMap
                isPlaced = False
                while E != [] and isPlaced == False:
                    e = E[0]

                    # We need to know the end vertex and the new position.
                    if direction == 0:
                        endV = e[0]
                        NX, NY = posX, posY - 1
                    elif direction == 1:
                        endV = e[1]
                        NX, NY = posX + 1, posY
                    elif direction == 2:
                        endV = e[1]
                        NX, NY = posX, posY + 1
                    elif direction == 3:
                        endV = e[0]
                        NX, NY = posX - 1, posY

                    # Now in case position NX, NY is not already taken and endV is
                    # compatible with "surrounding edges" in our graph, then we can
                    # add endV to our TileMap.
                    if  (not (NY, NX) in TileMap) and (TileMap.values().count(endV) == 0) and \
                        ((not (NY - 1, NX) in TileMap) or G.has_edge(TileMap[(NY - 1, NX)], endV)) and \
                        ((not (NY, NX + 1) in TileMap) or G.has_edge(endV, TileMap[(NY, NX + 1)])) and \
                        ((not (NY + 1, NX) in TileMap) or G.has_edge(endV, TileMap[(NY + 1), NX])) and \
                        ((not (NY, NX - 1) in TileMap) or G.has_edge(TileMap[(NY, NX - 1)], endV)):

                        # Add this node to our TileMap and delete the edge we just processed.
                        TileMap[(NY, NX)] = endV
                        isPlaced = True
                        G.remove_edge(*e)

                        # Call the procedure recursively with this new node.
                        TileMap, G = self.growTileMap(TileMap, G, NX, NY, endV)

                    E = E[1:len(E)]  # Chop of the first edge

            directory = directory[1:len(directory)]  # Chop of the first direction

        return TileMap, G

    def centerOfDictionary(self, H):
        """ Returns the center of the dictionary, that is, the average of all keys.
        """

        L = H.keys()
        return [ int(round(sum([l[1] for l in L]) / (len(L) + 0.0))), \
                 int(round(sum([l[0] for l in L]) / (len(L) + 0.0))) ]

    def composeDictionaries(self, H1, H2):
        """ This method takes two dictionaries H1, H2 that represent pieces of the
            maps of unique tiles, and pastes the second into the first, as close to
            their centers -- as close together -- as possible.
        """

        # In the first step H1 will be empty, and we return just H2.
        if H1 == {}:
            return H2

        CX1, CY1 = self.centerOfDictionary(H1)
        CX2, CY2 = self.centerOfDictionary(H2)

        # To make sure we fit H2 in as central as possible in H1, we walk in a spiral
        # around the center of H1, the offset being X, Y.
        #   |.4|.5|.6|
        #   |.3|.0|.7|
        #   |.2|.1|.8|
        #      ...|.9|
        X, Y = 0, 0
        foundFit = False
        while foundFit == False:
            # We check if H2 can be placed at location (CX1 + X, CY1 + Y)
            isFit = True
            keys = H2.keys()

            # As long as there are keys in H2 left and we found no counter example:
            while keys != [] and isFit:
                (y, x) = keys.pop()
                x1, y1 = x - CX2 + CX1 + X, y - CY2 + CY1 + Y

                if H1.has_key((y1, x1)) or H1.has_key((y1 - 1, x1)) or H1.has_key((y1, x1 + 1)) or \
                   H1.has_key((y1 + 1, x1)) or H1.has_key((y1, x1 - 1)):
                    isFit = False

            # If we found a fit, embed H2 into H1 accordingly.
            if isFit:
                for (y, x) in H2.keys():
                    x1, y1 = x - CX2 + CX1 + X, y - CY2 + CY1 + Y
                    H1[(y1, x1)] = H2[(y, x)]

                foundFit = True

            # Update the offset (X, Y) from the center of H1, by spiraling away.
            if X == 0 and Y == 0:
                Y += 1  # The first direction away from (0,0)
            elif Y < 0 and X < -Y and X >= Y: 
                X += 1
            elif X > 0 and Y <= X and Y >= -X:
                Y += 1
            elif Y > 0 and X > -Y and X < Y:
                X -= 1
            elif X < 0 and Y > X and Y <= -X: 
                Y -= 1

        return H1

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
    
            print("Pretty-printing the tileset:" + "\n")
            tiledMap.printHash(tiledMap.FullTileMap)

if __name__ == '__main__':
    main(sys);
