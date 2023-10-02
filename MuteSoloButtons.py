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

class MuteSoloButtons(Abstract):
    def __init__(self):
        for key in SoloButtons:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, True), self.handleSolo)
        for key in MuteButtons:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, True), self.handleMute)

        self.RegisterLEDUpdate(self.UpdateMuteLEDs)
        self.RegisterLEDUpdate(self.UpdateSoloLEDs)
    
    def handleSolo(self, event):
        if (self.Page in [Page_Pan, Page_Volume]):
            i = SoloButtons.index(event.data1)
            self.ColT[i].solomode = midi.fxSoloModeWithDestTracks
            mixer.soloTrack(self.ColT[i].TrackNum,
                midi.fxSoloToggle, self.ColT[i].solomode)

    def handleMute(self, event):
        index = MuteButtons.index(event.data1)
        if (self.Page in [Page_Pan, Page_Volume]):
            mixer.enableTrack(self.ColT[index].TrackNum)
        elif self.Page == Page_FX and self.CurPluginID == -1 and index < 10:
            state = mixer.getEventValue(mixer.getTrackPluginId(self.PluginTrack, index) + midi.REC_Plug_Mute) > 0
            mixer.automateEvent(
                mixer.getTrackPluginId(self.PluginTrack, index) + midi.REC_Plug_Mute,
                0 if state else int(midi.MaxInt / 2),
                self.SmoothSpeed
            )

    def UpdateMuteLEDs(self):
        for index in range(0, self.TrackCount):
            if (self.Page == Page_FX):
                if (self.CurPluginID == -1):
                    paramIndex = index + (self.TrackCount if self.isExtension else 0)
                    if paramIndex < 10:
                        pluginEnabled = mixer.getEventValue(mixer.getTrackPluginId(self.PluginTrack, index) + midi.REC_Plug_Mute) > 0
                        device.midiOutMsg((MuteButtons[index] << 8) + midi.TranzPort_OffOnT[not pluginEnabled])
                else:
                    device.midiOutMsg((MuteButtons[index] << 8) + midi.TranzPort_OffOnT[False])
            else:
                device.midiOutMsg((MuteButtons[index] << 8) + midi.TranzPort_OffOnT[not mixer.isTrackEnabled(self.ColT[index].TrackNum)])

    def UpdateSoloLEDs(self):
        for index in range(0, self.TrackCount):
            if (self.Page == Page_FX):
                if (self.CurPluginID == -1):
                    paramIndex = index + (self.TrackCount if self.isExtension else 0)
                    if paramIndex < 10:
                        device.midiOutMsg((SoloButtons[index] << 8) + midi.TranzPort_OffOnT[False])
                else:
                    device.midiOutMsg((SoloButtons[index] << 8) + midi.TranzPort_OffOnT[False])
            else:
                device.midiOutMsg((SoloButtons[index] << 8) + midi.TranzPort_OffOnT[mixer.isTrackSolo(self.ColT[index].TrackNum)])
