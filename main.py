import time
import threading
import ctypes
import string
import json

import tkinter as tk
from tkinter import Toplevel, ttk
from tkinter import Menu
from tkinter import filedialog

settings = {}

with open("options.json", "r") as read:
    settings = json.load(read)

alphanumeric = []
alphanumeric = list(string.ascii_lowercase)
alphanumeric.extend(range(0, 10))
alphanumeric = [str(i) for i in alphanumeric]

keyCodes = [
    0x41,
    0x42,
    0x43,
    0x44,
    0x45,
    0x46,
    0x47,
    0x48,
    0x49,
    0x4A,
    0x4B,
    0x4C,
    0x4D,
    0x4E,
    0x4F,
    0x50,
    0x51,
    0x52,
    0x53,
    0x54,
    0x55,
    0x56,
    0x57,
    0x58,
    0x59,
    0x5A,
    0x30,
    0x31,
    0x32,
    0x33,
    0x34,
    0x35,
    0x36,
    0x37,
    0x38,
    0x39,
]

user32 = ctypes.WinDLL("user32", use_last_error=True)

root = tk.Tk()
root.title("Sturdy Clicker")
root.iconbitmap("mouse.ico")

class Clicker(threading.Thread):
    def __init__(self, delay):
        super(Clicker, self).__init__()
        self.delay = delay
        self.running = False
        self.program_running = True

        self.currentAutoKey = settings["autoKey"]

        self.currentStart = settings["currentStart"]
        self.currentStop = settings["currentStop"]

        self.currentStartByte = keyCodes[alphanumeric.index(self.currentStart)]
        self.currentStopByte = keyCodes[alphanumeric.index(self.currentStop)]
        self.currentAutoByte = keyCodes[alphanumeric.index(self.currentAutoKey)]

        self.listeningStart = False
        self.listeningStop = False

        self.listeningAutoKey = False

    def start_clicking(self):
        self.running = True
        self.run()

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        if mouseEnabled.get() == 1:
            user32.mouse_event(2, 0, 0, 0, 0)
            user32.mouse_event(4, 0, 0, 0, 0)
        if kbEnabled.get() == 1:
            user32.keybd_event(self.currentAutoByte, 0)
        if self.running:
            root.after(self.delay, lambda: self.run())


class listener(threading.Thread):
    def __init__(self, delay, attached):
        self.delay = delay
        self.attachedClicker = attached
        self.justUpdated = False

    def update(self):
        root.after(self.delay, lambda: self.update())
        if self.justUpdated:
            self.justUpdated = False
        else:
            currentStartState = user32.GetKeyState(
                self.attachedClicker.currentStartByte
            )
            if currentStartState != 0 and currentStartState != 1:
                startClicking()
            currentStopState = user32.GetKeyState(self.attachedClicker.currentStopByte)
            if currentStopState != 0 and currentStopState != 1:
                stopClicking()


currentClicker = Clicker(settings["delay"])

main = listener(100, currentClicker)
main.update()


def updateTexts():
    startButtonText.set("Start (" + currentClicker.currentStart + ")")
    changeStartButtonText.set("Change start key: " + currentClicker.currentStart)
    stopButtonText.set("Stop (" + currentClicker.currentStop + ")")
    changeStopButtonText.set("Change stop key: " + currentClicker.currentStop)
    changeKeyText.set("Change auto key: " + currentClicker.currentAutoKey)
    autoText.set("Keyboard (" + currentClicker.currentAutoKey + ")")
    if currentClicker.running:
        statusText.set("Currently running at " + str(currentClicker.delay) + " ms")
    else:
        statusText.set("Not running")


def startClicking():
    if currentClicker.running == False:
        currentClicker.start_clicking()
    updateTexts()


def stopClicking():
    if currentClicker.running == True:
        currentClicker.stop_clicking()
    updateTexts()


def changeKey(sType):
    if sType == 0:
        if (
            currentClicker.listeningStop == False
            and currentClicker.listeningAutoKey == False
        ):
            currentClicker.listeningStart = True
            changeStartButtonText.set("Change start key: Listening for input...")
    if sType == 1:
        if (
            currentClicker.listeningStart == False
            and currentClicker.listeningAutoKey == False
        ):
            currentClicker.listeningStop = True
            changeStopButtonText.set("Change start key: Listening for input...")
    if sType == 2:
        if (
            currentClicker.listeningStart == False
            and currentClicker.listeningStop == False
        ):
            currentClicker.listeningAutoKey = True
            changeKeyText.set("Change auto key: Listening for input...")


def key_press(event):
    if (
        currentClicker.listeningStart
        or currentClicker.listeningStop
        or currentClicker.listeningAutoKey
    ):
        if currentClicker.running == False:
            try:
                key = event.char
                indice = alphanumeric.index(key)
                if currentClicker.listeningStart:
                    currentClicker.currentStart = key
                    currentClicker.currentStartByte = keyCodes[indice]
                    updateTexts()
                    currentClicker.listeningStart = False
                if currentClicker.listeningStop:
                    currentClicker.currentStop = key
                    currentClicker.currentStopByte = keyCodes[indice]
                    updateTexts()
                    currentClicker.listeningStop = False
                if currentClicker.listeningAutoKey:
                    currentClicker.currentAutoKey = key
                    currentClicker.currentAutoByte = keyCodes[indice]
                    updateTexts()
                    currentClicker.listeningAutoKey = False
                main.justUpdated = True
            except:
                top = Toplevel(root)
                top.title("Popup")
                top.resizable(False, False)
                ttk.Label(
                    top, text="Alphanumeric key only!", font="Calibri 12", padding=20
                ).pack()
                ttk.Button(top, text="Okay", command=top.destroy).pack()


def updateDelay():
    currentClicker.delay = delayText.get()


def openSetting():
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select a File", filetypes=(("Json files", "*.json*"),)
    )
    with open(filename, "r") as read:
        global settings
        settings = json.load(read)
    currentClicker.__init__(settings["delay"])
    updateTexts()


def saveSetting():
    currentSettings = {
        "autoKey": currentClicker.currentAutoKey,
        "currentStart": currentClicker.currentStart,
        "currentStop": currentClicker.currentStop,
        "delay": currentClicker.delay,
        "mouseEnabled": mouseEnabled.get(),
        "kbEnabled": kbEnabled.get(),
    }
    with open("options.json", "w") as write:
        json.dump(currentSettings, write)


mouseEnabled = tk.IntVar()
mouseEnabled.set(settings["mouseEnabled"])
kbEnabled = tk.IntVar()
kbEnabled.set(settings["kbEnabled"])

startButtonText = tk.StringVar()
changeStartButtonText = tk.StringVar()
stopButtonText = tk.StringVar()
changeStopButtonText = tk.StringVar()
changeKeyText = tk.StringVar()
autoText = tk.StringVar()
statusText = tk.StringVar()

delayText = tk.IntVar()
delayText.set(currentClicker.delay)

frm = ttk.Frame(root, padding=10)
frm.grid()

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open Settings", command=lambda: openSetting())
filemenu.add_command(label="Save Settings", command=lambda: saveSetting())

filemenu.add_separator()

filemenu.add_command(label="Exit", command=root.quit)

menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)

status = ttk.Label(frm, textvariable=statusText).grid(column=3, row=0)

startButton = ttk.Button(
    frm, textvariable=startButtonText, command=lambda: startClicking()
).grid(column=1, row=0)

changeStartButton = ttk.Button(
    frm, textvariable=changeStartButtonText, command=lambda: changeKey(0)
).grid(column=1, row=2)

stopButton = ttk.Button(
    frm, textvariable=stopButtonText, command=lambda: stopClicking()
).grid(column=2, row=0)
changeStartButton = ttk.Button(
    frm, textvariable=changeStopButtonText, command=lambda: changeKey(1)
).grid(column=2, row=2)

changeAutoKey = ttk.Button(
    frm, textvariable=changeKeyText, command=lambda: changeKey(2)
).grid(column=2, row=4)

mouseCheck = ttk.Checkbutton(
    frm,
    text="Mouse",
    variable=mouseEnabled,
    onvalue=1,
    offvalue=0,
).grid(column=1, row=3)
kbCheck = ttk.Checkbutton(
    frm,
    textvariable=autoText,
    variable=kbEnabled,
    onvalue=1,
    offvalue=0,
).grid(column=1, row=4)

ttk.Label(frm, text="Delay (in ms):").grid(column=1, row=5)

updateDelayButton = ttk.Button(
    frm, text="Update Delay", command=lambda: updateDelay()
).grid(column=3, row=5)

delayInput = ttk.Entry(
    frm,
    textvariable=delayText,
    width=10,
).grid(column=2, row=5)


updateTexts()

root.bind("<Key>", key_press)
root.resizable(False, False)
root.mainloop()
