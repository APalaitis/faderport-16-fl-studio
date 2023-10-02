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

class Windows(Abstract):
    def __init__(self):
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, None, B_VCA_FX, True), self.handleOpenPianoRoll)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, None, B_BusOutputs, True), self.handleOpenPlaylist)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, None, B_AudioInputs, True), self.handleOpenMixer)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, None, B_VI_MIDI, True), self.handleOpenChannelRack)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, None, B_AllUser, True), self.handleOpenBrowser)

        self.RegisterLEDUpdate(self.UpdateWindowLEDs)
    
    def handleOpenPlaylist(self, event):
        self.SendMsg2("Toggle playlist")
        self.toggleWindow(midi.widPlaylist)

    def handleOpenMixer(self, event):
        self.SendMsg2("Toggle mixer")
        self.toggleWindow(midi.widMixer)

    def handleOpenChannelRack(self, event):
        self.SendMsg2("Toggle channel rack")
        self.toggleWindow(midi.widChannelRack)

    def handleOpenPianoRoll(self, event):
        self.SendMsg2("Toggle piano roll")
        self.toggleWindow(midi.widPianoRoll)

    def handleOpenBrowser(self, event):
        self.SendMsg2("Toggle browser")
        self.toggleWindow(midi.widBrowser)

    def toggleWindow(self, window):
        if ui.getVisible(window) and ui.getFocused(window):
            ui.hideWindow(window)
        else:
            ui.showWindow(window)
            ui.setFocused(window)
        self.UpdateLEDs()

    def UpdateWindowLEDs(self):
        device.midiOutNewMsg((B_AudioInputs << 8) + midi.TranzPort_OffOnT[ui.getVisible(midi.widMixer)], 22)
        device.midiOutNewMsg((B_VI_MIDI << 8) + midi.TranzPort_OffOnT[ui.getVisible(midi.widChannelRack)], 23)
        device.midiOutNewMsg((B_BusOutputs << 8) + midi.TranzPort_OffOnT[ui.getVisible(midi.widPlaylist)], 24)
        device.midiOutNewMsg((B_VCA_FX << 8) + midi.TranzPort_OffOnT[ui.getVisible(midi.widPianoRoll)], 25)
        device.midiOutNewMsg((B_AllUser << 8) + midi.TranzPort_OffOnT[ui.getVisible(midi.widBrowser)], 25)

        rgbFocused = [0x0, 0x7F, 0x0]
        rgbDefault = [0x7F, 0x7F, 0x7F]
        for c in range(0, 3):
            device.midiOutMsg((rgbFocused[c] if ui.getFocused(midi.widMixer)          else rgbDefault[c] << 16) | B_AudioInputs  << 8 | (MSG_RED + c))
            device.midiOutMsg((rgbFocused[c] if ui.getFocused(midi.widChannelRack)    else rgbDefault[c] << 16) | B_VI_MIDI      << 8 | (MSG_RED + c))
            device.midiOutMsg((rgbFocused[c] if ui.getFocused(midi.widPlaylist)       else rgbDefault[c] << 16) | B_BusOutputs   << 8 | (MSG_RED + c))
            device.midiOutMsg((rgbFocused[c] if ui.getFocused(midi.widPianoRoll)      else rgbDefault[c] << 16) | B_VCA_FX       << 8 | (MSG_RED + c))
            device.midiOutMsg((rgbFocused[c] if ui.getFocused(midi.widBrowser)        else rgbDefault[c] << 16) | B_AllUser      << 8 | (MSG_RED + c))
