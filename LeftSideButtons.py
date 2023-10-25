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
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Arm, True), self.handleArmMode)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Link, True), self.handleLink)

        for key in [B_ClearSolo, B_ClearMute]:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, False), self.handleResponsiveButtonLED)

        self.RegisterLEDUpdate(self.UpdateLeftSideLEDs)


    def handleShift(self, event):
        self.Shift = event.data2 > 0
        self.UpdateLEDs()

    def handleSoloClear(self, event):
        if self.lastSoloTrack != -1:
            mixer.soloTrack(self.lastSoloTrack, 0)
        self.SendMsgToFL("All mixer tracks unsoloed")

    def handleMuteClear(self, event):
        for track in range(0, mixer.trackCount()):
            mixer.muteTrack(track, 0)
        self.SendMsgToFL("All mixer tracks unmuted")
    
    def handleBypass(self, event):
        state = not mixer.isTrackSlotsEnabled(mixer.trackNumber())
        mixer.enableTrackSlots(mixer.trackNumber(), state)
        if state:
            self.SendMsgToFL(f"FX enabled for CH{mixer.trackNumber()} {mixer.getTrackName(mixer.trackNumber())}")
        else:
            self.SendMsgToFL(f"FX disabled for CH{mixer.trackNumber()} {mixer.getTrackName(mixer.trackNumber())}")

    def handleArmMode(self, event):
        self.armMode = not self.armMode
        if self.armMode:
            self.SendMsgToFL("Arming mode on - select tracks to be armed")
        else:
            self.SendMsgToFL("Arming mode off")

        self.UpdateLEDs()

    def handleLink(self, event):
        if self.Shift:
            for index in range(0, self.TrackCount):
                device.linkToLastTweaked(0, index + 1)
            self.UpdateLEDs()
            self.UpdateTextDisplay()
            self.UpdateColT()
            self.SendMsgToFL('Unlinked last tweaked parameter')
        else:
            self.linkMode = not self.linkMode
            self.UpdateLEDs()
            self.SendMsgToFL('Move a fader to assign it to the last tweaked parameter')

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

        # Arm button
        device.midiOutNewMsg((B_Arm << 8) + midi.TranzPort_OffOnT[self.armMode], 33)
