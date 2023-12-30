
import random
from re import A
import numpy as np
import SaperConstants as cons
from collections import deque
import datetime


#This class 
class Board:

    def __init__(self, sizeX: int=cons.BOARD_DEFAULT_X, sizeY:int =cons.BOARD_DEFAULT_Y, mineCount=cons.BOARD_DEFAULT_MINECOUNT):
        self.initialize(sizeX, sizeY, mineCount)
    
    def initialize(self, sizeX: int, sizeY: int, mineCount: int):
        self.sizeX=sizeX
        self.sizeY=sizeY
        self.mineCount=mineCount
        self.checkedTiles=0
        self.flagCount=0
        self.gameStatus=cons.GAME_STATUS_ONGOING
        self.tilesToChange = deque()
    
    #tuple(sizeX, sizeY, mineCount)
    def initializeWithTuple(self, tuple):
        self.initialize(tuple[0], tuple[1], tuple[2])
    @property
    def sizeX(self):
        return self._sizeX
    
    @sizeX.setter
    def sizeX(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: sizeX has to be of int type")
        elif arg < cons.BOARD_MINIMUM_X:
            raise ValueError("ERROR: sizeX has to be greater than or equal to %d" % cons.BOARD_MINIMUM_X)
        elif arg > cons.BOARD_MAXIMUM_X:
            raise ValueError("ERROR: sizeX has to be less than or equal to %d" % cons.BOARD_MAXIMUM_X)
        else:
            self._sizeX = arg
    
    @sizeX.deleter
    def sizeX(self):
        del self._sizeX
    

    @property
    def sizeY(self):
        return self._sizeY
    
    @sizeY.setter
    def sizeY(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: sizeY has to be of int type")
        elif arg < cons.BOARD_MINIMUM_Y:
            raise ValueError("ERROR: sizeY has to be greater than or equal to %d" % cons.BOARD_MINIMUM_Y)
        elif arg > cons.BOARD_MAXIMUM_Y:
            raise ValueError("ERROR: sizeY has to be less than or equal to %d" % cons.BOARD_MAXIMUM_Y)
        else:
            self._sizeY = arg
    
    @sizeY.deleter
    def sizeY(self):
        del self._sizeY
    
    @property
    def mineCount(self):
        return self._mineCount
    
    @mineCount.setter
    def mineCount(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: mineCount has to be of int type")
        elif arg <= 0:
            raise ValueError("ERROR: mineCount has to be greater than 0")
        elif arg > int(0.5*self.sizeX * self.sizeY):
            raise ValueError("ERROR: mineCount has to be less than or equal to half the number of tiles")
        else:
            self._mineCount = arg
    
    @mineCount.deleter
    def mineCount(self):
        del self._mineCount
    
    @property
    def checkedTiles(self):
        return self._checkedTiles

    @checkedTiles.setter
    def checkedTiles(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: checkedTiles has to be of int type")
        elif arg < 0:
            raise ValueError("ERROR: checkedTiles has to be greater than or equal to 0")
        else:
            self._checkedTiles = arg
    
    @checkedTiles.deleter
    def checkedTiles(self):
        del self._checkedTiles
    
    @property
    def flagCount(self):
        return self._flagCount
    
    @flagCount.setter
    def flagCount(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: flagCount has to be of int type")
        elif arg < 0:
            raise ValueError("ERROR: flagCount has to be greater than or equal to 0")
        else:
            self._flagCount = arg
    
    @flagCount.deleter
    def flagCount(self):
        del self._flagCount
    
    @property
    def gameStatus(self):
        return self._gameStatus
    
    @gameStatus.setter
    def gameStatus(self, arg):
        if not isinstance(arg, str):
            raise TypeError("ERROR: gameStatus has to be of str type")
        else:
            self._gameStatus = arg

    @gameStatus.deleter
    def gameStatus(self):
        del self._gameStatus
    
    #these represent tiles which might need to change their appearence in GUI
    @property
    def tilesToChange(self):
        return self._tilesToChange
    
    @tilesToChange.setter
    def tilesToChange(self, arg):
        if not isinstance(arg, deque):
            raise TypeError("ERROR: tilesToChange has to be of deque type")
        else:
            self._tilesToChange = arg
    
    @tilesToChange.deleter
    def tilesToChange(self):
        del self._tilesToChange
    
    def getSettingsTuple(self):
        return (self.sizeX, self.sizeY, self.mineCount)
    
    def restart(self):
        self.initizalizeBoard()

    #initializeBoard works like a reset of the board, initializes it with numtiles and mines
    def initizalizeBoard(self, initialTile=(-1,-1)):
        #initizalizing board
        self.__initializeTiles(initialTile)

        attemptCount = 1
        while( not self.__initializeNeighbours() and attemptCount < cons.BOARD_MAX_ATTEMPT_COUNT):
            self.__initializeTiles(initialTile)
            attemptCount += 1
        
        self.checkedTiles=0
        self.flagCount=0
        self.gameStatus=cons.GAME_STATUS_ONGOING
        self.tilesToChange = deque()

        if attemptCount >= cons.BOARD_MAX_ATTEMPT_COUNT:
            return (self.__checkNeighbors(), attemptCount)
        return (True, attemptCount)
    
    #produces set of numbers ranging from 0 to sizeX*sizeY-1 which represents their positions on the board
    def __initializeMineSet(self, initialTile: tuple[int,int] = (-1,-1)):

        mineNumbers = set()
        leftToAdd = self.mineCount #number of mines that still has to be added

        freeTiles = set()


        if Tile.isInBoundTuple(self, initialTile):
            initialX, initialY = initialTile
            for tempX in range(initialX-1, initialX+2):
                for tempY in range(initialY-1, initialY+2):
                    if Tile.isInBound(self, tempX, tempY):
                        freeTiles.add(tempX*self.sizeY + tempY)
                        #there cannot be bombs on the initial tile and neighbouring tiles
        
        freeTilesNumber = len(freeTiles)
        mineNumbers.update(freeTiles)

        toBeAdded = self.mineCount + freeTilesNumber #full number of needed mine tiles and free tiles
        leftToAdd = self.mineCount #number of mines that still has to be added


        while leftToAdd != 0:
            mineNumbers.update(list(np.random.randint(low=0, high=self.sizeX*self.sizeY, size=leftToAdd )))
            leftToAdd = toBeAdded - len(mineNumbers)
            while leftToAdd == 1:
                tempNum = random.randrange(0, self.sizeX*self.sizeY)
                if tempNum not in mineNumbers:
                    mineNumbers.add(tempNum)
                    leftToAdd -= 1
        
        mineNumbers.difference_update(freeTiles) #we remove tiles which need to be free

        return mineNumbers
    
    #initialization of all the tiles
    def __initializeTiles(self, initialTile: tuple[int,int] = (-1,-1)):
        self.board = []
        minesPositions = self.__initializeMineSet(initialTile)
        tempPosition = 0
        for iRow in range(0, self.sizeX):
            self.board.append([])

            for jColumn in range(0, self.sizeY):
                if tempPosition in minesPositions:
                    self.board[iRow].append(Mine(self, iRow, jColumn))
                else:
                    self.board[iRow].append(NumTile(self, iRow, jColumn))
                tempPosition += 1
    

    def __initializeNeighbours(self) -> bool: #if there are neighbourless numTiles returns False, else True
        for iRow in self.board:
            for tile in iRow:
                tile.initializeNeighbors()

        return self.__checkNeighbors()
    
    def __checkNeighbors(self) -> bool:
        for iRow in self.board:
            for tile in iRow:
                if not tile.isNeighborsGood():
                    return False
        return True

    #what happens when a tile is clicked with a left click
    def onClick(self, corX, corY):
        self.board[corX][corY].onClick()

    #what happens when a tile is clicked with a right click
    def onRClick(self, corX, corY):
        self.board[corX][corY].onRClick()

    #information that a tile has been checked, potentially winning the game
    def checkTile(self, tile):
        self.checkedTiles += 1
        if self.isWin():
            for rowX in self.board:
                for tileM in rowX:
                    if tileM.isMine:
                        self.addTileChange(tileM)
    
    def addFlag(self):
        self.flagCount +=1

    def removeFlag(self):
        self.flagCount -=1

    def addTileChange(self, tile):
        self.tilesToChange.append(tile)
    
    #return a tile which might have changed appearance (could require gui change)
    def dequeueTileToChange(self):
        if self.tilesToChange:
            return self.tilesToChange.popleft()
        else:
            return None

    #act of clicking a bomb with left button ends with a loss
    def bombClicked(self, tile):
        self.addTileChange(tile)
        for rowX in self.board:
            for tileM in rowX:
                if tileM.isMine or tileM.status == cons.STATUS_FLAG:
                    self.addTileChange(tileM) #repetition of the initial tile is not dangerous
        self.gameStatus = cons.GAME_STATUS_LOSS
    
    def isWin(self):
        if self.checkedTiles < self.sizeX*self.sizeY - self.mineCount:
            return False
        self.gameStatus = cons.GAME_STATUS_WIN
        return True

    def isGameComplete(self):
        return self.gameStatus == cons.GAME_STATUS_WIN or self.gameStatus == cons.GAME_STATUS_LOSS
    
    def isClickSafe(self, corX, corY):
        return not self.board[corX][corY].isMine

    def getTile(self, corX, corY):
        return self.board[corX][corY]

    def printBoard(self):

        for rowX in self.board:
            for tile in rowX:
                print(tile.getName(), end=" ")
            print()





class Tile:

    def __init__(self, board, corX, corY, isMine):
        
        self.initialize(board, corX, corY, isMine)

    def initialize(self, board, corX, corY, isMine):
        self.board = board
        self.corX = corX
        self.corY = corY
        self.isMine = isMine
        self.status = cons.STATUS_DEFAULT
    

    @property
    def board(self):
        return self._board
    
    @board.setter
    def board(self, arg):
        if not isinstance(arg, Board):
            raise TypeError("ERROR: board has to be of Board type")
        else:
            self._board = arg
    
    @board.deleter
    def board(self):
        del self._board
    
    @property
    def corX(self):
        return self._corX
    
    @corX.setter
    def corX(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: corX has to be of int type")
        elif arg < 0:
            raise ValueError("ERROR: corX has to be greater than or equal to 0")
        else:
            self._corX = arg
    
    @corX.deleter
    def corX(self):
        del self._corX
    
    @property
    def corY(self):
        return self._corY
    
    @corY.setter
    def corY(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: corY has to be of int type")
        elif arg < 0:
            raise ValueError("ERROR: corY has to be greater than or equal to 0")
        else:
            self._corY = arg
    
    @corY.deleter
    def corY(self):
        del self._corY

    @property
    def isMine(self):
        return self._isMine
    
    @isMine.setter
    def isMine(self, arg):
        if not isinstance(arg, bool):
            raise TypeError("ERROR: isMine has to be of bool type")
        else:
            self._isMine = arg
    
    @isMine.deleter
    def isMine(self, arg):
        del self._isMine

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, arg):
        if not isinstance(arg, str):
            raise TypeError("ERROR: status has to be of str type")
        else:
            self._status = arg
    
    @status.deleter
    def status(self):
        del self._status

    

    
    def initializeNeighbors(self):
        pass

    
    def isNeighborsGood(self):
        pass
    
    def onClick(self):
        pass
    
    #Behavior when flag button was used on the tile
    def onRClick(self):
        if self.status == cons.STATUS_FLAG:
            self.status = cons.STATUS_DEFAULT
        elif self.status != cons.STATUS_CLICKED:
            self.status = cons.STATUS_FLAG
        self.board.addTileChange(self)

    def getName(self):
        pass
    
    #InBound - are coordinates given acceptable according to limits
    @staticmethod
    def isInBound(board, corX, corY):
        return Tile.isXinBound(board, corX) and Tile.isYinBound(board, corY)
    
    @staticmethod
    def isInBoundTuple(board, corXY:tuple[int,int]):
        corX, corY = corXY
        return Tile.isXinBound(board, corX) and Tile.isYinBound(board, corY)
    
    @staticmethod
    def isXinBound(board, corX):
        return corX >= 0 and corX < board.sizeX
    
    @staticmethod
    def isYinBound(board, corY):
        return corY >= 0 and corY < board.sizeY



class Mine(Tile):

    def __init__(self, board, corX, corY):
        super().__init__(board, corX, corY, True)
    
    #calculate how many nearby mines there are
    def initializeNeighbors(self):
        self.neighborCount = 0
        self.neighbors = []

        for tempX in range(self.corX-1, self.corX+2):
            for tempY in range(self.corY-1, self.corY+2):
                if Tile.isInBound(self.board, tempX, tempY) and (tempX != self.corX or tempY != self.corY):
                    if self.board.board[tempX][tempY].isMine:
                        self.neighborCount += 1
                        self.neighbors.append(self.board.board[tempX][tempY])

    
    def onClick(self):
        if self.status == cons.STATUS_FLAG:
            return
        self.status = cons.STATUS_CLICKED
        self.board.bombClicked(self)


    def getName(self):
        return cons.NAME_MINE + "_" + self.status
    
    def isNeighborsGood(self):
        #Mines have no restrictions on their neighbors
        return True


class NumTile(Tile):

    def __init__(self, board, corX, corY):
        super().__init__(board, corX, corY, False)
    
    #neighbors - nearby numtiles
    def initializeNeighbors(self):
        self.neighborCount = 0
        self.neighbors = []
        self.mineCount = 0

        for tempX in range(self.corX-1, self.corX+2):
            for tempY in range(self.corY-1, self.corY+2):
                if Tile.isInBound(self.board, tempX, tempY) and (tempX != self.corX or tempY != self.corY):
                    if self.board.board[tempX][tempY].isMine:
                        self.mineCount += 1
                    else:
                        self.neighborCount += 1
                        self.neighbors.append(self.board.board[tempX][tempY])
    
    
    def onClick(self):
        #no effect if already clicked
        if self.status == cons.STATUS_CLICKED or self.status == cons.STATUS_FLAG:
            return
        spread = self.isSpreadable()
        self.status = cons.STATUS_CLICKED
        self.board.checkTile(self)
        self.board.addTileChange(self)
        if spread:
            for neighbor in self.neighbors:
                neighbor.onClick()

        pass
    
    def getName(self):
        return str(self.mineCount) + "_" + self.status
        #make it more elaborate
    
    #Checking if the the tile aftering being clicked should also "click" all its neighbors
    def isSpreadable(self):
        return self.mineCount==0 and self.status==cons.STATUS_DEFAULT
    
    def isNeighborsGood(self):
        #Need to have at least one neighbor
        return self.neighborCount > 0



class Game:
    def __init__(self, mode="M", settingTuple:tuple[int,int,int]=None):
        self.board = Board()
        self.setMode(mode)
        self.prepareBoard(settingTuple)
        self.board.initizalizeBoard()
        self.gameStartTime = None
        pass

    def setMode(self, mode):
        self.gameMode = mode
    
    def prepareBoard(self, tuple:tuple[int,int,int]=None):
        if tuple != None:
            self.gameMode = "C"
        if self.gameMode != "C":
            self.board.initializeWithTuple(cons.GAME_MODES_DICT[self.gameMode])
        else:
            self.board.initializeWithTuple(tuple)

    @property
    def gameTime(self):
        return self._gameTime
    
    @gameTime.setter
    def gameTime(self, arg):
        if not isinstance(arg, int):
            raise TypeError("ERROR: gameTime should be of int type")
        elif arg < 0:
            raise ValueError("ERROR: gameTime should be greater than or equal to 0")
        elif arg > cons.TIME_MAX:
            self._gameTime = cons.TIME_MAX
        else:
            self._gameTime = arg
    
    @gameTime.deleter
    def gameTime(self):
        del self._gameTime

    @property
    def gameMode(self):
        return self._gameMode
    
    @gameMode.setter
    def gameMode(self, arg):
        if arg not in cons.GAME_MODES_DICT.keys():
            errorMessage = "ERROR: gamemode needs to be one of the following: "
            for k in cons.GAME_MODES_DICT.keys():
                errorMessage += k
                errorMessage += ", "
            raise TypeError(errorMessage)
        else:
            self._gameMode = arg

    
    @gameMode.deleter
    def gameMode(self):
        del self._gameMode

    @property
    def board(self):
        return self._board
    
    @board.setter
    def board(self, arg):
        if not isinstance(arg, Board):
            raise TypeError("ERROR: board has to be of Board type")
        else:
            self._board = arg
    
    @board.deleter
    def board(self):
        del self._board
    
    def onClick(self, corX, corY):
        if not self.isGameComplete():
            self.board.onClick(corX, corY)

    def onRClick(self, corX, corY):
        if not self.isGameComplete():
            self.board.onRClick(corX, corY)
    
    def dequeueTileToChange(self) -> Tile | None:
        return self.board.dequeueTileToChange()
    
    def isWin(self):
        return self.board.isWin()

    def isGameComplete(self):
        return self.board.isGameComplete()
    
    def gameStart(self, corX, corY, isLeftClick=True):
        if isLeftClick:
            #if not self.board.isClickSafe(corX, corY):
            self.board.initizalizeBoard((corX, corY))
            self.board.onClick(corX, corY)
        else:
            self.board.onRClick(corX, corY)
        self.gameStartTime = datetime.datetime.now()

    def sizeX(self):
        return self.board.sizeX
    
    def sizeY(self):
        return self.board.sizeY
    
    def gameStatus(self):
        return self.board.gameStatus
    
    def getTile(self, corX, corY):
        return self.board.getTile(corX, corY)
    
    def restart(self):
        self.board.restart()
        self.gameStartTime = None
    
    #when game is not yet started the gameStartTime == None
    def hasGameStarted(self):
        return self.gameStartTime != None
    
    def isGameOngoing(self):
        return self.hasGameStarted() and not self.board.isGameComplete()
    
    def startTimer(self):
        self.gameStartTime = datetime.datetime.now()
    

class WindowController:
    #Used for preventing interaction in many open windows at the same time (only one should be interactable)
    def __init__(self):
        self.setSigSingular()
    def setSigSingular(self):
        self.sigStatus = True
    def setSigMultiple(self):
        self.sigStatus = False
    def isSignalSingular(self):
        return self.sigStatus
    



def main():
    pass

if __name__ == "__main__":
    main()
