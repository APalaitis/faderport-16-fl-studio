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

class NavigationButtons(Abstract):
    def __init__(self):
        for key in JogSourceButtons:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleJogSources)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_Metronome, True), self.handleMetronome)

        self.RegisterLEDUpdate(self.UpdateJogLEDs)

    def handleJogSources(self, event):
        self.JogSource = event.data1
        self.UpdateJogLEDs()

    def handleMetronome(self, event):
        transport.globalTransport(
            midi.FPT_Metronome, 1, event.pmeFlags)
        if (ui.isMetronomeEnabled):
            self.SendMsgToFL("Metronome is Enabled")
        else:
            self.SendMsgToFL("Metronome is Disabled")

    def UpdateJogLEDs(self):
        for jogKey in JogSourceButtons:
            device.midiOutNewMsg((jogKey << 8) + midi.TranzPort_OffOnT[jogKey == self.JogSource], 26)
        device.midiOutNewMsg((B_Metronome << 8) + midi.TranzPort_OffOnT[general.getUseMetronome()], 12)

