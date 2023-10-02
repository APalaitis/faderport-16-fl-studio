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

class LeftSideButtons(Abstract):
    def __init__(self):
        for key in ShiftButtons:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, False), self.handleShift)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_ClearSolo, True), self.handleSoloClear)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_ClearMute, True), self.handleMuteClear)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Bypass, True), self.handleBypass)

        self.RegisterLEDUpdate(self.UpdateLeftSideLEDs)


    def handleShift(self, event):
        self.Shift = event.data2 > 0
        self.UpdateLEDs()
        self.UpdateMixer_Sel()

    def handleSoloClear(self, event):
        for track in range(0, mixer.trackCount()):
            mixer.soloTrack(track, 0)

    def handleMuteClear(self, event):
        for track in range(0, mixer.trackCount()):
            mixer.muteTrack(track, 0)
    
    def handleBypass(self, event):
        mixer.enableTrackSlots(mixer.trackNumber(), not mixer.isTrackSlotsEnabled(mixer.trackNumber()))

    def UpdateLeftSideLEDs(self):
        # Link button
        if self.Shift:
            device.midiOutNewMsg(0x7F << 16 | B_Link << 8 | MSG_ON_OFF, 28)
            device.midiOutNewMsg(0x7F << 16 | B_Link << 8 | MSG_RED, 29)
            device.midiOutNewMsg(0x00 << 16 | B_Link << 8 | MSG_GREEN, 30)
            device.midiOutNewMsg(0x00 << 16 | B_Link << 8 | MSG_BLUE, 31)
        else:
            device.midiOutNewMsg(self.linkMode << 16 | B_Link << 8 | MSG_ON_OFF, 28)
            device.midiOutNewMsg(0x7F << 16 | B_Link << 8 | MSG_RED, 29)
            device.midiOutNewMsg(0x7F << 16 | B_Link << 8 | MSG_GREEN, 30)
            device.midiOutNewMsg(0x7F << 16 | B_Link << 8 | MSG_BLUE, 31)

        # Bypass button
        device.midiOutNewMsg((B_Bypass << 8) + midi.TranzPort_OffOnT[not mixer.isTrackSlotsEnabled(mixer.trackNumber())], 32)

        # Shift button
        for key in ShiftButtons:
                device.midiOutNewMsg((key << 8) + midi.TranzPort_OffOnT[self.Shift], 33)
