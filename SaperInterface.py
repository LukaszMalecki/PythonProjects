import random
from re import A
from tkinter.font import BOLD
import numpy as np
import SaperConstants as cons
import Saper as saper
from collections import deque

import configparser
import tkinter as tk
import tkinter.messagebox
from tkinter.constants import NSEW
from turtle import bgcolor, width
from xml import dom
import os
import tkinter.filedialog
import time
from tkinter import *
from tkinter.ttk import *

import SaperInterfaceGame as sapergame


dane_konfig="data/tc.txt"


class SaperGui(tk.Frame):
    
    def __init__(self, master=None):
        self.config= configparser.ConfigParser()
        self.config.read(dane_konfig, "UTF8")        
        tk.Frame.__init__(self, master)
        self.parent=master
        self.parent.title("Saper")

        self.windowController = saper.WindowController()
        self.parent.protocol("WM_DELETE_WINDOW", self.appQuit)

        defaultCon=self.config["DEFAULT"]
        self.geometria_baza=defaultCon.get('bazowa_geometria',"1000x800+50+50")

        self.availableStyles=defaultCon.get('availableStyles', cons.INTERFACE_DEFAULT_AVAILABLE_STYLES).split(";")
        self.currentStyle=defaultCon.get('currentStyle', cons.INTERFACE_DEFAULT_STYLE)

        self.initialBoardSettings()

        self.interfaceParts = None
        self.loadInterface()
        

        self.parent.geometry(self.geometria_baza)
        self.createMenu()
        self.createMenuScore()

        self.createMenuButtons()

        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        self.parent.rowconfigure(2, weight=1)
        self.backgroundColorChange()
        


     #settings of a board taken from the file
    def initialBoardSettings(self):
        defaultBoard=self.config["BOARD"]

        self.gameMode=defaultBoard.get("gameMode", "M")
        gSettingAnswer = defaultBoard.get("gameSettings", None)
        if gSettingAnswer != None and gSettingAnswer != str(None):
            self.gameSettingsTuple=tuple(map( lambda x: int(x),gSettingAnswer.split(";")))
        else:
            self.gameSettingsTuple=None
    
    #used as a decorator, for proper working of Board interface with menu interface
    def interfaceButton(func):
        def inner(self, *args):
            if self.windowController.isSignalSingular():
                return func(self, *args)
            else:
                return
        return inner



    def createMenu(self):
        self.menubar = tk.Menu(self.parent)
        self.parent["menu"] = self.menubar
        fileMenu = tk.Menu(self.menubar, tearoff=False)
        for label, command, shortcut_text, shortcut in (
                ("Start", self.appStart, "Ctrl+R", "<Control-r>"),
                ("Ustawienia", self.appSettings, "Ctrl+O", "<Control-o>"),
                ("Tablica wyników", self.appScores, "Ctrl+S", "<Control-s>"),
                (None, None, None, None),
                ("Wyjdź", self.appQuit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menubar.add_cascade(label="Gra", menu=fileMenu, underline=0) 
        pass
    
    def createMenuScore(self):
        fileMenu = tk.Menu(self.menubar, tearoff=False)
        for label, command, shortcut_text, shortcut in (
                ("Tabela wyników", self.appScores, "Ctrl+N", "<Control-n>"),

                (None, None, None, None),
                ("Wyjdź", self.appQuit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menubar.add_cascade(label="Wyniki", menu=fileMenu, underline=0) 
        pass
    
    def createMenuButtons(self):
        self.toolbar_images = []  
        self.toolbar = tk.Frame(self.parent)
        
        self.menuElements = {"label":[], "button":[]}

        #Interface menu game name - Label
        try:
            image = self.interfaceMainLabel
            self.toolbar_images.append(image)
            label = tkinter.Label(self.toolbar, image=image)
            self.menuElements["label"].append(label) 
            label.grid(row=len(self.toolbar_images), column=1, pady=7)
        except tkinter.TclError as err:
            print(err)
        
        #Interface menu buttons

        commandDict = {"start":self.appStart, "settings":self.appSettings, "quit":self.appQuit}
        for key in self.interfaceParts.keys():
            command = commandDict[key]
            try:
                image = self.interfaceParts[key]
                self.toolbar_images.append(image)
                button = tkinter.Button(self.toolbar, image=image,command=command) 
                self.menuElements["button"].append(button) 
                button.grid(row=len(self.toolbar_images), column=1, pady=5)
            except tkinter.TclError as err:
                print(err) 

        self.toolbar.grid(row=0, column=1)
        self.toolbar.rowconfigure(0, weight=1)

    #loades style, phots for board and colours
    def loadInterface(self):
        if self.interfaceParts == None:
            self.interfaceParts = {}

        interfacePath = cons.INTERFACE_FILE_PATH + self.currentStyle + "/"
        self.interfaceNameLabel = cons.INTERFACE_NAME_LABEL
        self.interfaceMainLabel = tkinter.PhotoImage(file=interfacePath+self.interfaceNameLabel[1])
        for key in cons.INTERFACE_MENU_ITEMS_DICT.keys():
            self.interfaceParts[key] = tkinter.PhotoImage(file=interfacePath+cons.INTERFACE_MENU_ITEMS_DICT[key])
        
        with open(file=interfacePath+cons.INTERFACE_BACKGROUND_COLOR_FILE, mode='r') as file:
            content = file.readlines()
            self.backgroundColor = content[0].replace("\n", "")
            self.buttonBackgroundColor = content[1].replace("\n", "")
            self.buttonClickBackgroundColor = content[2].replace("\n", "")

    def backgroundColorChange(self):
        self.parent.configure(background=self.backgroundColor)
        self.toolbar.configure(background=self.backgroundColor)

        for key in self.menuElements.keys():
            for elem in self.menuElements[key]:
                elem['bg'] = self.buttonBackgroundColor
                if key == "button":
                    elem.configure(activebackground=self.buttonClickBackgroundColor)

    #gets tuple of (sizeX, sizeY, Mines)
    def getSettingTuple(self):
        if self.gameMode == cons.GAME_MODE_CUSTOM:
            return self.gameSettingsTuple
        elif self.gameMode in cons.GAME_MODES_DICT.keys():
            return cons.GAME_MODES_DICT[self.gameMode]
        else:
            return (None, None, None)


    @interfaceButton
    def appStart(self):
        game= saper.Game(self.gameMode, self.gameSettingsTuple)
        #so as menu cannot be used during running of game board
        self.windowController.setSigMultiple()
        sapergame.main(game=game,styleFile=self.currentStyle,parentSignal=self.windowController)
    


    @interfaceButton
    def appSettings(self):
        wynik = SettingsMenu(self.parent,prompt="Ustawienia",polozenie=self.currentLocation(),
        availableStyles=self.availableStyles, boardSettings=self.getSettingTuple()).show()
        self.interfaceUpdateTuple(wynik)
    
    @interfaceButton
    def appScores(self):
        wynik = ScoreMenu(self.parent, prompt="Tablica wyników", polozenie=self.currentLocation()) 
    
    @interfaceButton
    def appQuit(self, event= None):
        reply = tkinter.messagebox.askyesno(
                        "Zakończenie programu",
                        cons.INTERFACE_GOODBYE_MESSAGE, parent=self.parent)
        event=event
        if reply:
            geometria=self.parent.winfo_geometry()
            styles = ""
            for st in self.availableStyles:
                if styles == "":
                    styles += st
                else:
                    styles += ";"
                    styles += st
            self.config["DEFAULT"]["bazowa_geometria"]=geometria
            self.config["DEFAULT"]["availableStyles"]=styles
            self.config["DEFAULT"]["currentStyle"]=self.currentStyle

            #BOARD settings

            gSettings = ""
            if self.gameSettingsTuple != None:
                for gs in self.gameSettingsTuple:
                    if gSettings == "":
                        gSettings += str(gs)
                    else:
                        gSettings += ";"
                        gSettings += str(gs)
            else:
                gSettings = str(None)
            
            self.config["BOARD"]["gameMode"]=self.gameMode
            self.config["BOARD"]["gameSettings"]=gSettings

            with open(dane_konfig, 'w') as konfig_plik:
                self.config.write(konfig_plik)
            self.parent.destroy()
        pass

    #current locatio of the window "+winX+winY"
    def currentLocation(self):
        return "+%d+%d" % (self.parent.winfo_x(), self.parent.winfo_y())
    
    def interfaceUpdateTuple(self, settingTuple=(None,None,None)):
        style, gameMode, gameSettingsTuple = settingTuple
        self.interfaceUpdate(style, gameMode, gameSettingsTuple)

    #update interface with style, gamemode and/or tuple of board settings
    def interfaceUpdate(self, style=None, gameMode=None, gameSettingsTuple=None):
        if style != None and style != self.currentStyle:
            self.currentStyle = style
            self.loadInterface()
            self.backgroundColorChange()

        if gameMode==cons.GAME_MODE_CUSTOM: 
            self.gameMode = gameMode
            self.gameSettingsTuple = gameSettingsTuple
        elif gameMode != None:
            self.gameMode = gameMode
            self.gameSettingsTuple = None


class SettingsMenu(tk.Toplevel):
    def __init__(self, parent, prompt, polozenie="+450+250", availableStyles=cons.INTERFACE_DEFAULT_AVAILABLE_STYLES_LIST, boardSettings=None):
        tk.Toplevel.__init__(self, parent)
        self.geometry("%s" %polozenie)
        parent.wm_attributes("-disabled", True)
        self.transient(parent)
        self.title(prompt)
        self.root=parent    

        self.styleAnswer = tk.StringVar()
        self.styleAnswer.set(cons.SETTINGS_MENU_DEFAULT_STYLE)
        self.sizeX = tk.IntVar()
        self.sizeX.set(cons.SETTINGS_MENU_DEFAULT_NUMBER)
        self.sizeY = tk.IntVar()
        self.sizeY.set(cons.SETTINGS_MENU_DEFAULT_NUMBER)
        self.mineCount = tk.IntVar()
        self.mineCount.set(cons.SETTINGS_MENU_DEFAULT_NUMBER)

        if boardSettings != None:
            self.initalSettings = boardSettings

        self.availableStyles = availableStyles

        self.protocol("WM_DELETE_WINDOW", self.cancelOperation)

        self.backgroundColor = "light gray"
        self.config(background=self.backgroundColor)

        self.resizable(False, False)

        self.ustaw_kontrolki()

    def ustaw_kontrolki(self):
        self.maxColumnNumber = 4

        minSizeC = int(cons.SETTINGS_MENU_DEFAULT_WIDTH/self.maxColumnNumber)


        #Configuration of scales for User to choose parameters of the board
        self.slideSideX = tk.Scale(self, from_=cons.BOARD_MINIMUM_X, to=cons.BOARD_MAXIMUM_X, orient=HORIZONTAL, length=(minSizeC-15)*2)
        self.slideSideX.config(background=self.backgroundColor, highlightbackground = self.backgroundColor, highlightcolor= self.backgroundColor)

        self.slideSideY = tk.Scale(self, from_=cons.BOARD_MINIMUM_Y, to=cons.BOARD_MAXIMUM_Y, orient=HORIZONTAL, length=(minSizeC-15)*2)
        self.slideSideY.config(background=self.backgroundColor, highlightbackground = self.backgroundColor, highlightcolor= self.backgroundColor)

        self.slideMineCount = tk.Scale(self, from_=1, to=int(0.5*self.slideSideX.get()*self.slideSideY.get()), orient=HORIZONTAL, length=(minSizeC-15)*2)
        self.slideMineCount.config(background=self.backgroundColor, highlightbackground = self.backgroundColor, highlightcolor= self.backgroundColor)
        
        #Saves current state of scales into variables
        def saveAndExit():
            self.sizeX.set(self.slideSideX.get())
            self.sizeY.set(self.slideSideY.get())
            self.mineCount.set(self.slideMineCount.get())
            self.close_toplevel()

        #Changes current state of scales according to the tuple (X,Y,M)
        def setSliders(settingTuple):
            sX, sY, mC = settingTuple
            def inner():
                self.slideSideX.set(sX)
                self.slideSideY.set(sY)
                adjustMineCountMax()
                self.slideMineCount.set(mC)
            return inner
        
        #Ensures mine count is acceptable (mine count <= sizeX*sizeY*0.5)
        def adjustMineCountMax(var=None):
            tempMax = int(0.5*self.slideSideX.get()*self.slideSideY.get())
            if self.slideMineCount.get() > tempMax:
                self.slideMineCount.set(tempMax)
            self.slideMineCount.config(to=tempMax)
        
        #as scales X and Y are changes, so should change scope of mine count
        self.slideSideX.config(command=adjustMineCountMax)
        self.slideSideY.config(command=adjustMineCountMax)

        #uses initial settings provided
        if self.initalSettings != None:
            setSliders(self.initalSettings)()
 

        modeNumber = 0
        self.modeButtons = []
        #so as after going into the loop we get to index 0 during first iteration
        self.currentRowNumber = -1

        for mode in cons.GAME_MODES_NAMES.keys():
            if mode != cons.GAME_MODE_CUSTOM:
                button = Button(self, text=cons.GAME_MODES_NAMES[mode], command=setSliders(cons.GAME_MODES_DICT[mode]))
                if modeNumber%self.maxColumnNumber == 0:
                    self.currentRowNumber += 1
                button.grid(column=modeNumber%self.maxColumnNumber, row=self.currentRowNumber, pady=5)
                self.modeButtons.append(button)
                modeNumber += 1
        
        for i in range(self.maxColumnNumber):
            self.grid_columnconfigure(i, minsize=minSizeC)

        self.currentRowNumber += 1

        Label(self, text="Wysokość").grid(column=0, row=self.currentRowNumber)
        self.slideSideX.grid(column=1, row=self.currentRowNumber, columnspan=2) 
        self.currentRowNumber += 1

        Label(self, text="Szerokość").grid(column=0, row=self.currentRowNumber)
        self.slideSideY.grid(column=1, row=self.currentRowNumber, columnspan=2) 
        self.currentRowNumber += 1

        Label(self, text="Liczba min").grid(column=0, row=self.currentRowNumber)
        self.slideMineCount.grid(column=1, row=self.currentRowNumber, columnspan=2)
        

        def setStyleLambda(newStyle, button:tk.Button):
            def inner():
                self.styleAnswer.set(newStyle)

                for but in self.styleButtons:
                    but.config(background=cons.SETTINGS_MENU_BUTTON_BACKGROUND)
                button.config(background=cons.SETTINGS_MENU_BUTTON_ACTIVE)
                
            return inner
        styleNumber = 0
        self.styleButtons = []
        for style in self.availableStyles:
            if styleNumber%self.maxColumnNumber == 0:
                self.currentRowNumber += 1
            styleName = ""

            with open(file=cons.INTERFACE_FILE_PATH + style + "/" + cons.INTERFACE_STYLE_NAME_FILE, mode='r') as file:
                content = file.readlines()
                styleName = content[0].replace("\n", "")

            button = tk.Button(self, text=styleName)
            button.config(command=setStyleLambda(style, button), background=cons.SETTINGS_MENU_BUTTON_BACKGROUND, 
            foreground=cons.SETTINGS_MENU_BUTTON_FOREGROUND, activebackground=cons.SETTINGS_MENU_BUTTON_ACTIVE, 
            activeforeground=cons.SETTINGS_MENU_BUTTON_FOREGROUND)

            button.grid(column=styleNumber%self.maxColumnNumber, row=self.currentRowNumber, pady=5)
            styleNumber += 1
            self.styleButtons.append(button)
            

        self.currentRowNumber += 1

        self.acceptButton = Button(self, text="Zapisz", command=saveAndExit)
        self.acceptButton.grid(column=1, row=self.currentRowNumber, pady=10)

        self.cancelButton = Button(self, text="Anuluj", command=lambda: self.cancelOperation())
        self.cancelButton.grid(column=2, row=self.currentRowNumber, pady=10)
        self.currentRowNumber += 1

    def cancelOperation(self):
        self.styleAnswer.set(cons.SETTINGS_MENU_DEFAULT_STYLE)
        self.sizeX.set(cons.SETTINGS_MENU_DEFAULT_NUMBER)
        self.sizeY.set(cons.SETTINGS_MENU_DEFAULT_NUMBER)
        self.mineCount.set(cons.SETTINGS_MENU_DEFAULT_NUMBER)
        self.close_toplevel()

    #returns the settings chosen by the usere
    def show(self):
        self.wait_window()

        wynik = [self.styleAnswer.get(), None, (self.sizeX.get(), self.sizeY.get(), self.mineCount.get())]
        if wynik[0] == cons.SETTINGS_MENU_DEFAULT_STYLE:
            wynik[0] = None
        if wynik[2] == (cons.SETTINGS_MENU_DEFAULT_NUMBER,cons.SETTINGS_MENU_DEFAULT_NUMBER,cons.SETTINGS_MENU_DEFAULT_NUMBER):
            wynik[2] = None
        else:
            for boardSetting in cons.GAME_MODES_DICT.keys():
                if wynik[2] == cons.GAME_MODES_DICT[boardSetting]:
                    wynik[1] = boardSetting
            if wynik[1] == None:
                wynik[1] = cons.GAME_MODE_CUSTOM
        self.close_toplevel()       
        return tuple(wynik)

    def jest_ok(self):
        self.root.wm_attributes("-disabled", False)
        self.destroy()
        pass

    def close_toplevel(self):
        self.root.wm_attributes("-disabled", False)
        self.destroy()


class ScoreMenu(tk.Toplevel):
    def __init__(self, parent, prompt, polozenie="+450+250"):
        tk.Toplevel.__init__(self, parent)
        self.geometry("%s" % polozenie)
        parent.wm_attributes("-disabled", True)
        self.transient(parent)
        self.title(prompt)
        self.root=parent    

        self.gameMode = tk.StringVar()
        self.gameMode.set(cons.SCORE_MENU_DEFAULT_MODE)
        self.loadScore()

        self.protocol("WM_DELETE_WINDOW", self.cancelOperation)

        self.backgroundColor = "light gray"
        self.config(background=self.backgroundColor)

        self.resizable(False, False)

        self.ustaw_kontrolki()
    
    def loadScore(self):
        self.scoreReader= configparser.ConfigParser()
        self.scoreReader.read(cons.SCORE_MENU_FILE_PATH, "UTF8") 
        self.scores = dict()
        for gameType in cons.SCORE_MENU_VALID_KEYS:
            self.scores[gameType]=[]
            tempScores = self.scoreReader[gameType].get(cons.SCORE_MENU_KEY_NAME, "")
            if tempScores != "":
                self.scores[gameType]=list(sorted(map(lambda x: int(x),tempScores.split(";"))))
        

    def ustaw_kontrolki(self):
        self.maxColumnNumber = 4

        minSizeC = 20

        self.currentRowNumber = 0
        
        
        modeNumber = 0
        self.modeButtons = {}
        self.currentRowNumber = -1 #so as aftergoing into the loop we get to index 0 during first iteration
        for mode in cons.GAME_MODES_NAMES.keys():
            if mode != cons.GAME_MODE_CUSTOM:
                button = tk.Button(self, text=cons.GAME_MODES_NAMES[mode], bg=cons.SCORE_MENU_DEFAULT_MODE_COLOR, activebackground=cons.SCORE_MENU_CURRENT_MODE_COLOR)
                if modeNumber%self.maxColumnNumber == 0:
                    self.currentRowNumber += 1
                if self.gameMode.get() == mode:
                    button.config(bg=cons.SCORE_MENU_CURRENT_MODE_COLOR)
                button.grid(column=modeNumber%self.maxColumnNumber, row=self.currentRowNumber, pady=5)
                self.modeButtons[mode] = button
                modeNumber += 1
        
        
        for i in range(self.maxColumnNumber):
            self.grid_columnconfigure(i, minsize=30)
        

        self.currentRowNumber += 1

        labelName1 = tk.Label(self, text="Miejsce", bg="#BBBBBB", width=minSizeC//3,) 
        labelName1 .grid(column=1, row=self.currentRowNumber, sticky="e")
        labelName2 = tk.Label(self, text="Czas", width=minSizeC//3, bg="#BBBBBB") 
        labelName2.grid(column=2, row=self.currentRowNumber, sticky="w")

        self.currentRowNumber += 1

        self.records = []

        filledRecordNumber = self.getRecordsNumber()

        for recordNumber in range(cons.SCORE_MENU_MAX_SCORE_SIZE):
            number = tk.Label(self, text="%d." % (recordNumber+1), bg="white", width=minSizeC//3, anchor="e")
            number.grid(column=1, row=self.currentRowNumber, sticky="e")
            record = tk.Label(self, text="-", width=minSizeC//3, anchor="e")
            if recordNumber < filledRecordNumber:
                record.config(text=self.scores[self.gameMode.get()][recordNumber])
            record.grid(column=2, row=self.currentRowNumber, sticky="w")
            self.records.append(record)
            self.currentRowNumber += 1

        def setMode(mode):
            def inner():
                self.modeButtons[self.gameMode.get()].config(bg=cons.SCORE_MENU_DEFAULT_MODE_COLOR)
                self.gameMode.set(mode)
                self.modeButtons[self.gameMode.get()].config(bg=cons.SCORE_MENU_CURRENT_MODE_COLOR)
                recNumber = self.getRecordsNumber()
                for recordNumber, record in enumerate(self.records):
                    if recordNumber < recNumber:
                        record.config(text=self.scores[self.gameMode.get()][recordNumber])
                    else:
                        record.config(text="-")
                
            return inner
        
        for mode in self.modeButtons.keys():
            self.modeButtons[mode].config(command=setMode(mode))
            
        self.currentRowNumber += 1

        self.acceptButton = Button(self, text="Zamknij", command=lambda: self.close_toplevel())
        self.acceptButton.grid(column=1, row=self.currentRowNumber, pady=10)

        def removeScore():
            def inner():
                if self.removeRecords():
                    setMode(self.gameMode.get())()
            return inner

        self.cancelButton = Button(self, text="Wyczyść", command=removeScore())
        self.cancelButton.grid(column=2, row=self.currentRowNumber, pady=10)
        self.currentRowNumber += 1
        #self.grid_columnconfigure(0, minsize=50)
        #self.grid_columnconfigure(1, minsize=50)
        #self.grid_columnconfigure(2, minsize=50)

        for columnI in range(0, self.maxColumnNumber):
            self.grid_columnconfigure(columnI, minsize=minSizeC)
        #self.grid_columnconfigure(3, minsize=50)
 
        #self.ok_button = tk.Button(self, text="OK", command=self.on_ok)   
        #self.x_button = tk.Button(self, text="nie", command=self.not_ok)    

    def removeRecords(self):
        reply = tkinter.messagebox.askyesno("Usuwanie wyników",
        "Czy napewno chcesz usunąć wyniki dla poziomu trudności %s?" % cons.GAME_MODES_NAMES[self.gameMode.get()], parent=self)
        if reply:
            self.scores[self.gameMode.get()] = []
        return reply

    def getRecordsNumber(self):
        return len(self.scores[self.gameMode.get()])
    def cancelOperation(self):
        self.close_toplevel()

    def show(self):
        #self.wm_deiconify()
        self.wait_window()
     
        return None

    def jest_ok(self):
        self.root.wm_attributes("-disabled", False)
        self.destroy()
        pass
    def close_toplevel(self):
        self.root.wm_attributes("-disabled", False)
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
        self.destroy()


def main():
    root = tk.Tk()
    game = SaperGui(master=root)
    game.mainloop()

if __name__ == "__main__":
    main()