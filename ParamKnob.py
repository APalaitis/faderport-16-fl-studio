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

class ParamKnob(Abstract):
    def __init__(self):
        self.RegisterMidiListener(EventInfo(midi.MIDI_CONTROLCHANGE, 0, CC1_PanParam), self.handleParamKnob)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_PanParam, True), self.handleParamKnobClick)

    def handleParamKnob(self, event):
        delta = int((midi.MaxInt / -75) if event.data2 > CC2_DirectionThreshold else (midi.MaxInt / 75))
        if self.Page == Page_Volume:
            eventId = midi.REC_Mixer_Pan + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            value = min(int(midi.MaxInt / 2), max(0, mixer.getEventValue(eventId) + delta))
            self.automateEvent(eventId, value, self.SmoothSpeed)
        elif self.Page == Page_Pan:
            eventId = midi.REC_Mixer_Vol + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            value = min(int(midi.MaxInt / 2), max(0, mixer.getEventValue(eventId) + delta))
            self.automateEvent(eventId, mixer.getEventValue(eventId) + delta, self.SmoothSpeed)
        elif self.Page == Page_Sends:
            delta = -1 if event.data2 > CC2_DirectionThreshold else 1
            track = mixer.trackNumber() + delta
            mixer.setTrackNumber(track, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)
            self.SendMsgToFL("Channel selected: " + mixer.getTrackName(track))

    def handleParamKnobClick(self, event):
        if self.Page == Page_Volume:
            eventId = midi.REC_Mixer_Pan + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            self.automateEvent(eventId, int(midi.MaxInt / 2 * 0.5), self.SmoothSpeed)
        elif self.Page == Page_Pan:
            eventId = midi.REC_Mixer_Vol + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            self.automateEvent(eventId, int(midi.MaxInt / 2 * 0.8), self.SmoothSpeed)

