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

class TransportControls(Abstract):
    def __init__(self):
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_Stop, True), self.handleStop)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_Play, True), self.handlePlay)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_Record, True), self.handleRecord)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_Loop, True), self.handleLoop)

        self.RegisterLEDUpdate(self.UpdateTransportLEDs)

    def handleStop(self, event):
        transport.globalTransport(midi.FPT_Stop, 1, event.pmeFlags)

    def handlePlay(self, event):
        transport.globalTransport(midi.FPT_Play, 1, event.pmeFlags)

    def handleRecord(self, event):
        transport.globalTransport(midi.FPT_Record, 1, event.pmeFlags)

    def handleLoop(self, event):
        transport.globalTransport(midi.FPT_Loop, 1, event.pmeFlags)

    def UpdateTransportLEDs(self):
        device.midiOutNewMsg((B_Stop << 8) + midi.TranzPort_OffOnT[transport.isPlaying() == midi.PM_Stopped], 0)
        device.midiOutNewMsg((B_Loop << 8) + midi.TranzPort_OffOnT[transport.getLoopMode() == midi.SM_Pat], 1)
        device.midiOutNewMsg((B_Record << 8) + midi.TranzPort_OffOnT[transport.isRecording()], 2)
