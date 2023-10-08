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

class NavigationControls(Abstract):
    def __init__(self):
        self.RegisterMidiListener(EventInfo(midi.MIDI_CONTROLCHANGE, 0, CC1_RotaryEncoder), self.handleNavigationKnob)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_RotaryEncoder, True), self.handleNavigationKnobClick)
        for key in [B_ArrowLeft, B_ArrowRight]:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleArrowButtons)
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, False), self.handleResponsiveButtonLED)



    def handleNavigationKnob(self, event):
        if self.JogSource == Jog_Marker:
            transport.globalTransport(midi.FPT_Jog, 1 if event.data2 < CC2_DirectionThreshold else -1, event.pmeFlags)
        elif self.JogSource == Jog_Scroll:
            transport.globalTransport(midi.FPT_MoveJog, 1 if event.data2 < CC2_DirectionThreshold else -1, event.pmeFlags)
        elif self.JogSource == Jog_Zoom:
            transport.globalTransport(midi.FPT_HZoomJog + int(self.Shift), -1 if event.data2 > CC2_DirectionThreshold else 1, event.pmeFlags)
        elif self.JogSource in [Jog_Channel, Jog_Bank]:
            delta = -1 if event.data2 > CC2_DirectionThreshold else 1
            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] + delta)
        elif self.JogSource == Jog_Master:
            delta = int((midi.MaxInt / -100) if event.data2 > CC2_DirectionThreshold else (midi.MaxInt / 100))
            mixer.automateEvent(midi.REC_MainVol, mixer.getEventValue(midi.REC_MainVol) + delta, midi.REC_MIDIController, self.SmoothSpeed)
        elif self.JogSource == Jog_Section:
            pass

        event.handled = True

    def handleNavigationKnobClick(self, event):
        if self.JogSource == Jog_Master:
            mixer.automateEvent(midi.REC_MainVol, int(midi.MaxInt / 2 * 0.8), midi.REC_MIDIController, self.SmoothSpeed)
        elif self.JogSource == Jog_Marker:
            arrangement.addAutoTimeMarker(arrangement.currentTime(False), "New marker")

    def handleArrowButtons(self, event):       
        if self.Page == Page_FX:
            if (self.CurPluginID != -1):  # Selected Plugin
                if (event.data1 == B_ArrowLeft) & (self.PluginParamOffset >= 16):
                    self.PluginParamOffset -= 16
                elif (event.data1 == B_ArrowRight) & (self.PluginParamOffset + 16 < plugins.getParamCount(mixer.trackNumber(), self.CurPluginID + self.CurPluginOffset)):
                    self.PluginParamOffset += 16
                self.UpdateColT()
                device.hardwareRefreshMixerTrack(-1)
            else:  # No Selected Plugin
                pass
        else:
            if self.JogSource == Jog_Zoom:
                if event.data1 == B_ArrowLeft:
                    transport.globalTransport(midi.FPT_VZoomJog + int(self.Shift), -1, event.pmeFlags)
                elif event.data1 == B_ArrowRight:
                    transport.globalTransport(midi.FPT_VZoomJog + int(self.Shift), 1, event.pmeFlags)
            elif self.JogSource == Jog_Marker:
                if event.data1 == B_ArrowLeft:
                    arrangement.jumpToMarker(-1, False)
                elif event.data1 == B_ArrowRight:
                    arrangement.jumpToMarker(1, False)
            else:
                self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == B_ArrowRight) * self.TrackCount)
                if not self.isExtension:
                    device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                if self.Page != Page_FX:
                    for m in range(0, 0 if self.isExtension else 1):
                        self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == B_ArrowRight) * self.TrackCount)
        if not self.isExtension:
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
