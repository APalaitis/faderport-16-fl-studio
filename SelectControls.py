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

class SelectControls(Abstract):
    def __init__(self):
        for key in SelectButtons:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, True), self.handleSelectButtons)

        self.RegisterLEDUpdate(self.UpdateSelectLEDs)
    
    def handleSelectButtons(self, event):
        index = SelectButtons.index(event.data1)
        event.handled = True
        if self.Page == Page_Links:
            event.handled = False
        elif self.Shift and self.Page in [Page_Volume, Page_Pan, Page_Stereo]:
            if self.Page == Page_Volume:
                mixer.setTrackVolume(self.ColT[index].TrackNum, 0.8)
            elif self.Page == Page_Pan:
                mixer.setTrackPan(self.ColT[index].TrackNum, 0)
            elif self.Page == Page_Stereo:
                mixer.setTrackStereoSep(self.ColT[index].TrackNum, 0)
        elif self.armMode:
            mixer.armTrack(self.ColT[index].TrackNum)
            if mixer.isTrackArmed(self.ColT[index].TrackNum):
                self.SendMsgToFL(mixer.getTrackName(
                    self.ColT[index].TrackNum) + ' recording to ' + mixer.getTrackRecordingFileName(self.ColT[index].TrackNum))
            else:
                self.SendMsgToFL(mixer.getTrackName(
                    self.ColT[index].TrackNum) + ' unarmed')
        else:
            if self.Page in [Page_Volume, Page_Pan, Page_Stereo]:
                ui.showWindow(midi.widMixer)
                ui.setFocused(midi.widMixer)
                self.UpdateLEDs()
                mixer.setTrackNumber(self.ColT[index].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)
                self.SendMsgToFL("Channel selected: " + mixer.getTrackName(self.ColT[index].TrackNum))
            elif self.Page == Page_FX:
                if self.CurPluginID == -1:
                    if plugins.isValid(mixer.trackNumber(), index):
                        self.CurPluginID = index
                        self.PluginParamOffset = 0
                        mixer.focusEditor(mixer.trackNumber(), index)
                        self.UpdateColT()
                        self.UpdateLEDs()
                        self.UpdateTextDisplay()
                else:
                    # AP: Ignore button presses, there's no functionality that makes sense in this case
                    pass
            elif self.Page == Page_Sends:
                fromTrack = mixer.trackNumber()
                toTrack = self.FirstTrackT[self.FirstTrack] + index
                state = not mixer.getRouteSendActive(fromTrack, toTrack)
                mixer.setRouteTo(fromTrack, toTrack, state)
                if state:
                    self.SendMsgToFL(f"Track #{fromTrack} routed to track #{toTrack}")
                else:
                    self.SendMsgToFL(f"Track #{fromTrack} no longer routed to track #{toTrack}")


    def UpdateSelectLEDs(self):
        for index in range(0, self.TrackCount):
            state = False
            rgb = [0x7F, 0x7F, 0x7F]
            if self.Page == Page_FX:
                if (self.CurPluginID == -1):
                    rgb = [0x7F, 0x7F, 0x0]
                    if index < 10:
                        pluginValid = plugins.isValid(self.PluginTrack, index)
                        state = pluginValid
                else:
                    rgb = [0x7F, 0x3F, 0x0]
                    try: paramCount = plugins.getParamCount(self.PluginTrack, self.CurPluginID)
                    except: paramCount = 0
                    state = index + self.PluginParamOffset < paramCount
            else:
                if self.armMode:
                    rgb = [0xFF, 0x0, 0x0]
                    state = mixer.isTrackArmed(self.ColT[index].TrackNum)
                elif self.Shift and self.Page in [Page_Volume, Page_Pan, Page_Stereo]:
                    rgb = [0x0, 0x5F, 0x0]
                    state = True
                else:
                    if self.Page == Page_Sends:
                        state = mixer.getRouteSendActive(mixer.trackNumber(), self.ColT[index].TrackNum) or (index == mixer.trackNumber())
                    else:
                        state = self.ColT[index].TrackNum == mixer.trackNumber()

                    trackNum = self.ColT[index].TrackNum
                    if trackNum == 0:
                        color = 0xFFFFFF
                    else:
                        color = mixer.getTrackColor(self.ColT[index].TrackNum) & 0xFFFFFF
                    rgb = [
                        # AP: Shaping the color intensity curve (y = x) -> (y = x^2 / 128)
                        pow(((color & 0x00FF0000) >> 16) / 2, 2) / 128,
                        pow(((color & 0x0000FF00) >> 8) / 2, 2) / 128,
                        pow((color & 0x000000FF) / 2, 2) / 128
                    ]

            device.midiOutMsg((0x7F if state else 0) << 16 | (SelectButtons[index] << 8) | MSG_ON_OFF)
            device.midiOutMsg(int(rgb[0]) << 16 | (SelectButtons[index]) << 8 | MSG_RED)
            device.midiOutMsg(int(rgb[1]) << 16 | (SelectButtons[index]) << 8 | MSG_GREEN)
            device.midiOutMsg(int(rgb[2]) << 16 | (SelectButtons[index]) << 8 | MSG_BLUE)

