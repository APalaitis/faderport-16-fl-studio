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
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Save, True), self.handleSave)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Redo, True), self.handleRedo)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Undo, True), self.handleUndo)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User1, True), self.handleUser1)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User2, True), self.handleUser2)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User3, True), self.handleUser3)

        for key in [B_Save, B_Redo, B_Undo]:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, False), self.handleResponsiveButtonLED)

        self.RegisterLEDUpdate(self.UpdateTopRightLEDs)

    def handleUser1(self, event):
        self.SetPage(Page_Stereo)

    def handleUser2(self, event):
        self.SetPage(Page_EQ)

    def handleUser3(self, event):
        self.SetPage(Page_Links)

    def handleSave(self, event):
        transport.globalTransport(midi.FPT_Save, 1, event.pmeFlags)
        
    def handleRedo(self, event):
        transport.globalTransport(midi.FPT_UndoJog, 1, event.pmeFlags)

    def handleUndo(self, event):
        transport.globalTransport(midi.FPT_UndoJog, -1, event.pmeFlags)

    def UpdateTopRightLEDs(self):
        # Stereo width page
        device.midiOutMsg((B_User1 << 8) + midi.TranzPort_OffOnT[self.Page == Page_Stereo])

        # EQ page
        device.midiOutMsg((B_User2 << 8) + midi.TranzPort_OffOnT[self.Page == Page_EQ])

        # Links page
        device.midiOutMsg((B_User3 << 8) + midi.TranzPort_OffOnT[self.Page == Page_Links])