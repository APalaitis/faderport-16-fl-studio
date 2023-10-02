import arrangement
import channels
import device
import general
import launchMapPages
import midi
import mixer
import patterns
import playlist
import plugins
import transport
import ui
import utils

from Types import *
from Constants import *
from Abstract import Abstract

class TopRightButtons(Abstract):
    def __init__(self):
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User1, True), self.handleUser1)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User2, True), self.handleUser2)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Save, True), self.handleSave)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Link, True), self.handleLink)

    def handleUser1(self, event):
        self.SetPage(Page_Stereo)

    def handleUser2(self, event):
        self.SetPage(Page_EQ)

    def handleSave(self, event):
        transport.globalTransport(
            midi.FPT_Save + int(self.Shift), int(event.data2 > 0) * 2, event.pmeFlags)
        
    def handleLink(self, event):
        if self.Shift:
            for index in range(0, self.TrackCount):
                device.linkToLastTweaked(0, index + 1)
            self.UpdateLEDs()
            self.UpdateTextDisplay()
            self.UpdateColT()
            self.SendMsg2('Unlinked last tweaked parameter')
        else:
            self.linkMode = not self.linkMode
            self.UpdateLEDs()
