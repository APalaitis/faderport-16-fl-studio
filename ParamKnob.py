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
        self.RegisterMidiListener(EventInfo(midi.MIDI_CONTROLCHANGE), self.handleParamKnob)
        self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_PanParam, True), self.handleParamKnobClick)

    def handleParamKnob(self, event):
        delta = int((midi.MaxInt / -100) if event.data2 > CC2_DirectionThreshold else (midi.MaxInt / 100))
        if self.Page == Page_Volume:
            eventId = midi.REC_Mixer_Pan + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            mixer.automateEvent(eventId, mixer.getEventValue(eventId) + delta, midi.REC_MIDIController, self.SmoothSpeed)
        elif self.Page == Page_Pan:
            eventId = midi.REC_Mixer_Vol + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            mixer.automateEvent(eventId, mixer.getEventValue(eventId) + delta, midi.REC_MIDIController, self.SmoothSpeed)
        elif self.Page == Page_Sends:
            delta = -1 if event.data2 > CC2_DirectionThreshold else 1
            mixer.setTrackNumber(mixer.trackNumber() + delta, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

        event.handled = True

    def handleParamKnobClick(self, event):
        if self.Page == Page_Volume:
            eventId = midi.REC_Mixer_Pan + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            mixer.automateEvent(eventId, int(midi.MaxInt / 2 * 0.5), midi.REC_MIDIController, self.SmoothSpeed)
        elif self.Page == Page_Pan:
            eventId = midi.REC_Mixer_Vol + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            mixer.automateEvent(eventId, int(midi.MaxInt / 2 * 0.8), midi.REC_MIDIController, self.SmoothSpeed)

