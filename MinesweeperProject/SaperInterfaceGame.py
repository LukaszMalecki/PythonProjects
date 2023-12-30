import random
from re import A
import numpy as np
import SaperConstants as cons
import Saper as saper
from collections import deque
import datetime

import configparser
import tkinter as tk
import tkinter.messagebox
from tkinter.constants import NSEW
from turtle import width
from xml import dom
import os
import tkinter.filedialog
import time
from tkinter import *
from tkinter.ttk import *
import platform

dane_konfig="data/tcBoard.txt"

CLICK = "<Button-1>"
if platform.system() == 'Darwin':
    RCLICK = "<Button-2>"
else: 
    RCLICK = "<Button-3>"

#Make it work

class GameBoard(tk.Frame):
    tileImages = {}

    def __init__(self, master=None, game=saper.Game("E"), styleFile=cons.INTERFACE_DEFAULT_STYLE, parentSignal:saper.WindowController=saper.WindowController()):
        
        #signal from SaperInterface
        self.parentSignal = parentSignal
        self.parentSignal.setSigMultiple()

        self.config= configparser.ConfigParser()
        self.config.read(dane_konfig, "UTF8")        
        tk.Frame.__init__(self, master)

        self.parent=master
        self.parent.protocol("WM_DELETE_WINDOW", self.appQuit)
        self.parent.title("Saper")
        self.game:saper.Game = game
        self.loadScore()

        self.boardStartRow = 1
        self.boardStartColumn = 0

        defaultCon=self.config["DEFAULT"]
        self.geometria_baza=defaultCon.get('bazowa_geometria',"+150+400")

        self.currentStyle=styleFile



        self.interfaceParts = None
        self.loadInterface()
        self.parent.geometry(self.geometria_baza)


        self.make_board()
        self.make_timer()

        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=10)
        self.parent.rowconfigure(1, weight=1)
        self.parent.rowconfigure(2, weight=1)

        self.parent.resizable(False, False)
        self.timerId = None


        pass


        '''
    def initialBoardSettings(self):
        defaultBoard=self.config["BOARD"]

        #MAKE SETTINGS SAVE IN A FILE
        self.gameMode=defaultBoard.get("gameMode", "M")
        gSettingAnswer = defaultBoard.get("gameSettings", None)
        if gSettingAnswer != None and gSettingAnswer != str(None):
            self.gameSettingsTuple=tuple(map( lambda x: int(x),gSettingAnswer.split(";")))
        else:
            self.gameSettingsTuple=None
    '''
        

    def createMenu(self):
        self.menubar = tk.Menu(self.parent)
        self.parent["menu"] = self.menubar
        fileMenu = tk.Menu(self.menubar, tearoff=False)
        for label, command, shortcut_text, shortcut in (
                #("Start", self.file_new, "Ctrl+N", "<Control-n>"),
                #("Choose Covid Data...", self.file_open, "Ctrl+O", "<Control-o>"),
                #("Choose Log...", self.file_save, "Ctrl+S", "<Control-s>"),
                (None, None, None, None),
                ("Quit", self.appQuit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menubar.add_cascade(label="File", menu=fileMenu, underline=0) 
        pass
    
    def boardCorX( self, gridX):
        return gridX - self.boardStartRow

    def boardCorY( self, gridY):
        return gridY - self.boardStartColumn
        
    def gridCorX( self, boardX):
        return boardX + self.boardStartRow

    def gridCorY( self, boardY):
        return boardY + self.boardStartColumn

    def make_timer(self):
        self.timer = Label(self.boardFrame, text="Czas: 0000")

        self.timer.grid(row=0,column=0,columnspan=self.sizeY())
    
    def timeUpdate(self):

        if not self.game.isGameOngoing():
            return
        endTime = datetime.datetime.now()
        playTime = endTime - self.game.gameStartTime
        self.game.gameTime = int(playTime.total_seconds())

        playTime = str(self.game.gameTime).zfill(4)

        self.timer.config(text=("%s%s" % ("Czas: ",playTime)))
        self.timerId = self.boardFrame.after(100, self.timeUpdate)

    
    def make_board(self):
        #self.toolbar_images = []   #muszą być pamiętane stale
        self.boardFrame = tk.Frame(self.parent)

        self.boardFrame.configure(background=self.backgroundColor)

        self.boardButtons = []
        

        for rowX in range(0, self.sizeX()):
            self.boardButtons.append([])
            for tileY in range(0, self.sizeY()):
                tile = self.getTile(rowX, tileY)
                button = tkinter.Button(self.boardFrame, image = GameBoard.tileImages[tile.getName()+"_"+self.gameStatus()]) #relief="flat"

                if self.tileColorChange:
                    #self.tileColorChange = False
                    button['bg'] = self.tileColor
                if self.tileClickColorChange:
                    button.configure(activebackground=self.tileClickColor) #DD0000


                button.bind(CLICK, self.lambdaOnClick(rowX, tileY))
                button.bind(RCLICK, self.lambdaOnRClick(rowX, tileY))
                button.grid( row=self.gridCorX(rowX), column=self.gridCorY(tileY))


                self.boardButtons[rowX].append(button)
        
        self.boardFrame.grid(row=0, column=1)
        #self.boardFrame.rowconfigure(0, weight=1)
        
    def lambdaOnClick(self, corX, corY):
        return lambda Button: self.onClick(corX, corY)
    
    def lambdaOnRClick(self, corX, corY):
        return lambda Button: self.onRClick(corX, corY)

    def updateTiles(self):

        t = self.game.dequeueTileToChange()
        while t != None:
            self.updateTile(t)
            t = self.game.dequeueTileToChange()
    
    def updateTile(self, tile:saper.Tile):
        button = self.boardButtons[tile.corX][tile.corY]
        button.config(image = GameBoard.tileImages[tile.getName()+"_"+self.gameStatus()])
    
    def updateTileCor(self, corX, corY):
        return self.updateTile(self.getTile(corX,corY))
    
    def updateAllTiles(self):
        for rowX in range(0, self.sizeX()):
            for tileY in range(0, self.sizeY()):
                self.updateTileCor(rowX, tileY)

    def onClick(self, corX, corY):
        if self.game.hasGameStarted():
            self.game.onClick(corX, corY)
        else:
            self.game.gameStart(corX, corY, True)
            self.updateAllTiles()#self.make_board()
            self.game.startTimer()
            self.timeUpdate()
        if self.game.isGameComplete():
            self.gameComplete()
            #self.restartQuestion()
        else:
            self.updateTiles()


    def gameComplete(self):
        endTime = datetime.datetime.now()
        playTime = endTime - self.game.gameStartTime
        self.game.gameTime = int(playTime.total_seconds())

        self.updateTiles()
        if self.gameStatus() == cons.GAME_STATUS_WIN:
            if self.game.gameMode in cons.SCORE_MENU_VALID_KEYS:
                self.scores[self.game.gameMode].append(self.game.gameTime)
        self.restartQuestion()

    def restart(self):
        self.game.restart()
        self.updateAllTiles()
    
    def restartQuestion(self):
        if self.gameStatus() == cons.GAME_STATUS_WIN:
            reply = tkinter.messagebox.askyesno(
                            "Wygrana!",
                            "Gratulacje!\nTwój czas to: %d sekund\nChcesz spróbować jeszcze raz?" % self.game.gameTime, parent=self.parent)
        else:
            reply = tkinter.messagebox.askyesno(
                            "Przegrana",
                            "Nie udało się tym razem :c\nChcesz spróbować jeszcze raz?", parent=self.parent)
        if reply:
            self.restart()
        else:
            self.appQuit(forced=True)


    def onRClick(self, corX, corY):
        if self.game.gameStartTime != None:
            self.game.onRClick(corX, corY)
        else:
            self.game.gameStart(corX, corY, False)
            self.updateAllTiles()#self.make_board()
            self.gameStartTime = datetime.datetime.now()
        self.updateTiles()

    def getTile(self, corX, corY) -> saper.Tile:
        return self.game.getTile(corX, corY)
    def gameStatus(self):
        return self.game.gameStatus()

    def loadInterface(self):
        
        GameBoard.tileImages = {}
        tileImages = GameBoard.tileImages

        with open(file=cons.INTERFACE_FILE_PATH + self.currentStyle + "/"+cons.INTERFACE_BACKGROUND_COLOR_FILE, mode='r') as file:
            content = file.readlines()
            self.backgroundColor = content[0].replace("\n", "")
            self.tileColor = content[3].replace("\n", "")
            self.tileClickColor = content[4].replace("\n", "")
        
        self.tileColorChange = True
        if self.tileColor == "default":
            self.tileColorChange = False
        
        self.tileClickColorChange = True
        if self.tileClickColor == "default":
            self.tileClickColorChange = False

        self.parent.configure(background=self.backgroundColor)
        #self.toolbar.configure(background=self.backgroundColor)
        


        self.loadTiles()

    imagesYes = [] #list of images
    def loadTiles(self):
        interfacePath = cons.INTERFACE_FILE_PATH + self.currentStyle + "/"
        fileExtension = cons.INTERFACE_FILE_EXTENSION

        def getFile(name):
            return "%s%s%s" % (interfacePath,name,fileExtension)

        #Semantics: M - mine, A - all tiles, 9 - all numtiles, 0-8 - tiles with nearby mine number equal to the number
        #D - in default state, F - in flagged state, C - in clicked state
        #O - when the game is on-going, L - when the game is lost, W - when the game is won

        #generate default tile when game is on-going
        tempImage = tkinter.PhotoImage(file=getFile("A_D_O"), master=self.parent)
        GameBoard.tileImages["M_D_O"] = tempImage
        for i in range(0, 9):
             GameBoard.tileImages["%d_D_O" % (i)] = tempImage


        #generate default tile when game is lost
        tempImage = tkinter.PhotoImage(file=getFile("M_D_L"), master=self.parent)
        GameBoard.tileImages["M_D_L"] = tempImage

        tempImage = tkinter.PhotoImage(file=getFile("A_D_O"), master=self.parent)
        for i in range(0, 9):
             GameBoard.tileImages["%d_D_L" % (i)] = tempImage
        

        #generate default tile when game is won
        tempImage = tkinter.PhotoImage(file=getFile("M_F_W"), master=self.parent)
        GameBoard.tileImages["M_D_W"] = tempImage
        #there is no default tiles when game is won

        
        #generate flag tile when game is on-going
        tempImage = tkinter.PhotoImage(file=getFile("A_F_O"), master=self.parent)
        GameBoard.tileImages["M_F_O"] = tempImage
        for i in range(0, 9):
             GameBoard.tileImages["%d_F_O" % (i)] = tempImage


        #generate flag tile when game is lost
        tempImage = tkinter.PhotoImage(file=getFile("M_F_L"), master=self.parent)
        GameBoard.tileImages["M_F_L"] = tempImage
        tempImage = tkinter.PhotoImage(file=getFile("9_F_L"), master=self.parent)
        for i in range(0, 9):
             GameBoard.tileImages["%d_F_L" % (i)] = tempImage


        #generate flag tile when game is won
        tempImage = tkinter.PhotoImage(file=getFile("M_F_W"), master=self.parent)
        GameBoard.tileImages["M_F_W"] = tempImage


        #generate clicked tile when game is on-going
        for i in range(0, 9):
            tempImage = tkinter.PhotoImage(file=getFile("%d_C_O" %i), master=self.parent)
            GameBoard.tileImages["%d_C_O" % (i)] = tempImage


        #generate clicked tile when game is lost
        tempImage = tkinter.PhotoImage(file=getFile("M_C_L"), master=self.parent)
        GameBoard.tileImages["M_C_L"] = tempImage
        for i in range(0, 9):
            tempImage = tkinter.PhotoImage(file=getFile("%d_C_O" %i), master=self.parent)
            GameBoard.tileImages["%d_C_L" % (i)] = tempImage


        #generate clicked tile when game is won
        for i in range(0, 9):
            tempImage = tkinter.PhotoImage(file=getFile("%d_C_O" %i), master=self.parent)
            GameBoard.tileImages["%d_C_W" % (i)] = tempImage
        
        for im in GameBoard.tileImages.values():
            GameBoard.imagesYes.append(im)
        
        



    def sizeX(self):
        return self.game.sizeX()
    
    def sizeY(self):
        return self.game.sizeY()

    def backGroundColorChange(self, color="#b9c7d0"):
        self.parent.configure(background=color)
        self.toolbar.configure(background=color)

    def appQuit(self, event= None, forced=False):
        if not forced:
            reply = tkinter.messagebox.askyesno(
                            "Wyłączenie okna",
                            cons.INTERFACE_GOODBYE_MESSAGE, parent=self.parent)
        else:
            reply = True
        event=event
        if reply:
            geometria= ('+%d+%d' % (self.parent.winfo_x(), self.parent.winfo_y()))
            
            self.config["DEFAULT"]["bazowa_geometria"]=geometria
            self.config["DEFAULT"]["currentStyle"]=self.currentStyle

            with open(dane_konfig, 'w') as konfig_plik:
                self.config.write(konfig_plik)
            
            #Score writing

            for gameType in cons.SCORE_MENU_VALID_KEYS:
                tempScores = self.scores[gameType]
                retString = ""
                if tempScores:
                    tempScores = list(sorted(tempScores))[0:cons.SCORE_MENU_MAX_SCORE_SIZE] #we sort and get first 10
                    isFirst = True
                    for score in tempScores:
                        if isFirst:
                            retString += str(score)
                            isFirst = False
                        else:
                            retString += ";%d" % score

                self.scoreReader[gameType][cons.SCORE_MENU_KEY_NAME]=retString
            
            with open(cons.SCORE_MENU_FILE_PATH, 'w') as konfig_plik:
                self.scoreReader.write(konfig_plik)


            
            if self.timerId != None:
                self.boardFrame.after_cancel(self.timerId)
            self.parentSignal.setSigSingular()
            self.parent.destroy()
        pass

    def loadScore(self):
        self.scoreReader= configparser.ConfigParser()
        self.scoreReader.read(cons.SCORE_MENU_FILE_PATH, "UTF8") 
        self.scores = dict()
        for gameType in cons.SCORE_MENU_VALID_KEYS:
            self.scores[gameType]=[]
            tempScores = self.scoreReader[gameType].get(cons.SCORE_MENU_KEY_NAME, "")
            if tempScores != "":
                self.scores[gameType]=list(map(lambda x: int(x),tempScores.split(";")))
    
    def printScores(self):
        for mode in self.scores.keys():
            print("Mode %s times:\n" % mode)
            print(self.scores[mode])




def main(game=saper.Game("E"), styleFile=cons.INTERFACE_DEFAULT_STYLE,parentSignal=saper.WindowController()):
    root = tk.Tk()
    game = GameBoard(master=root, game=game, styleFile=styleFile,parentSignal=parentSignal)
    game.mainloop()

if __name__ == "__main__":
    main()
