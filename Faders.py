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

class Faders(Abstract):
    def __init__(self):
        self.RegisterMidiListener(EventInfo(midi.MIDI_PITCHBEND), self.handleFaders)
        for key in FaderHold:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, None, key, True), self.sliderHold)

    
    def checkFaderLink(self, midiChan):
        eventId = device.findEventID(midi.EncodeRemoteControlID(device.getPortNumber(), midiChan, 255), 1)
        value = device.getLinkedValue(eventId)
        name = ''
        try: name = device.getLinkedParamName(eventId)
        except: pass
        return [
            name,
            value
        ]
    
    def handleFaders(self, event):
        index = event.midiChan

        if self.linkMode:
            self.linkMode = False
            device.linkToLastTweaked(0, index + 1)
            device.linkToLastTweaked(255, index + 1)
            self.UpdateLEDs()
            self.UpdateTextDisplay()
            self.UpdateColT()
            return

        if index >= self.TrackCount:
            return
        
        # AP: Check if the fader is linked to a param, and if so - unlink it from vol/pan
        if (self.checkFaderLink(index)[1] > -1 and self.Page in [Page_Pan, Page_Volume]):
            self.UpdateColT()
            # The event will continue to the linked parameter
            event.handled = False
            return

        event.inEv = event.data1 + (event.data2 << 7)
        event.outEv = (event.inEv << 16) // 16383

        if self.Page == Page_FX and self.CurPluginID >= 0:
            if (plugins.isValid(self.PluginTrack, self.CurPluginID + self.CurPluginOffset)):
                paramIndex = index + self.PluginParamOffset + (self.TrackCount if self.isExtension else 0)
                count = plugins.getParamCount(self.PluginTrack, self.CurPluginID + self.CurPluginOffset)
                if paramIndex < count:
                    level = self.AlphaTrack_SliderToLevel(event.inEv) / midi.FromMIDI_Max
                    plugins.setParamValue(level, paramIndex, self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))
                    event.handled = True
                    self.UpdateColT()
                    # hint
                    self.SendMsg2(
                        plugins.getParamName(paramIndex, self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))
                        + ': '
                        + str(round(level, 2)))
        elif self.ColT[index].SliderEventID >= 0:
            # slider (mixer track volume)
            event.handled = True
            mixer.automateEvent(self.ColT[index].SliderEventID, self.AlphaTrack_SliderToLevel(
                event.inEv), midi.REC_MIDIController, self.SmoothSpeed)
            # hint
            n = mixer.getAutoSmoothEventValue(
                self.ColT[index].SliderEventID)
            s = mixer.getEventIDValueString(
                self.ColT[index].SliderEventID, n)
            if s != '':
                s = ': ' + s
            self.SendMsg2(self.ColT[index].SliderName + s)

    def sliderHold(self, event):
        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)
        event.handled = True


    #############################################################################################################################
    #                                                                                                                           #
    #  PRINCIPAL FUNCTION RESPONSIBLE FOR UPDATING COLUMNS                                                                      #
    #                                                                                                                           #
    #############################################################################################################################
    def UpdateCol(self, Num):
        data1 = 0
        data2 = 0
        center = 0

        if device.isAssigned():
            # AP: By default, values come from REC events
            sv = mixer.getEventValue(self.ColT[Num].SliderEventID)
            
            linkValue = self.checkFaderLink(Num)[1]
            # AP: Plugin params don't have REC events associated with them, so we use functions to get the values
            if self.Page == Page_FX:
                if (self.CurPluginID >= 0):
                    if (plugins.isValid(self.PluginTrack, self.CurPluginID)):
                        paramCount = plugins.getParamCount(self.PluginTrack, self.CurPluginID)
                        paramIndex = Num + (self.TrackCount if self.isExtension else 0) + self.PluginParamOffset
                        if paramIndex < paramCount:
                            paramValue = plugins.getParamValue(paramIndex, self.PluginTrack, self.CurPluginID)
                            sv = int(midi.FromMIDI_Max * paramValue)
            
            # elif linkValue > -1 and self.Page in [Page_Pan, Page_Volume]:
            #     sv = int(midi.FromMIDI_Max * linkValue)

            if Num < self.TrackCount:
                # V-Pot
                center = self.ColT[Num].KnobCenter
                if self.ColT[Num].KnobEventID >= 0:
                    m = mixer.getEventValue(
                        self.ColT[Num].KnobEventID, midi.MaxInt, False)
                    if center < 0:
                        if self.ColT[Num].KnobResetEventID == self.ColT[Num].KnobEventID:
                            center = int(
                                m != self.ColT[Num].KnobResetValue)
                        else:
                            center = int(
                                sv != self.ColT[Num].KnobResetValue)

                    if self.ColT[Num].KnobMode < 2:
                        data1 = 1 + round(m * (10 / midi.FromMIDI_Max))
                    else:
                        data1 = round(m * (11 / midi.FromMIDI_Max))
                    if self.ColT[Num].KnobMode > 3:
                        data1 = (center << 6)
                    else:
                        data1 = data1 + \
                            (self.ColT[Num].KnobMode << 4) + (center << 6)

            # slider
            # AP: If the control is linked, don't move the fader
            if not (linkValue > -1 and self.Page in [Page_Pan, Page_Volume]):
                data1 = self.AlphaTrack_LevelToSlider(sv)
                data2 = data1 & 127
                data1 = data1 >> 7
                device.midiOutMsg(midi.MIDI_PITCHBEND + Num + (data2 << 8) + (data1 << 16))

    #############################################################################################################################
    #                                                                                                                           #
    #  PRINCIPAL PROCEDURE FOR HANDLING INTERNAL COLUMN LIST                                                                    #
    #                                                                                                                           #
    #############################################################################################################################
    def UpdateColT(self):
        f = self.FirstTrackT[self.FirstTrack]
        CurID = mixer.getTrackPluginId(mixer.trackNumber(), 0)

        for m in range(0, len(self.ColT)):
            self.ColT[m].KnobPressEventID = -1
            ch = 'CH'+str(self.ColT[m].TrackNum).zfill(2) + ' - '

            self.ColT[m].KnobEventID = -1
            self.ColT[m].KnobResetEventID = -1
            self.ColT[m].KnobResetValue = midi.FromMIDI_Max >> 1
            self.ColT[m].KnobName = ''
            self.ColT[m].KnobMode = 1  # parameter, pan, volume, off
            self.ColT[m].KnobCenter = -1
            self.ColT[m].TrackName = ''
            self.ColT[m].BaseEventID = mixer.getTrackPluginId(self.ColT[m].TrackNum, 0)
            self.ColT[m].TrackNum = midi.TrackNum_Master + ((f + m) % mixer.trackCount())

            if self.Page == Page_Volume:
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_Vol
                self.ColT[m].SliderName = ch+mixer.getTrackName(self.ColT[m].TrackNum) + ' - Volume'
            if self.Page == Page_Pan:
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_Pan
                self.ColT[m].SliderName = ch+mixer.getTrackName(self.ColT[m].TrackNum) + ' - ' + 'Pan'
            elif self.Page == Page_Stereo:
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_SS
                self.ColT[m].SliderName = mixer.getTrackName(self.ColT[m].TrackNum) + ' - ' + 'Separation'
            elif self.Page == Page_Sends:
                self.ColT[m].SliderEventID = CurID + midi.REC_Mixer_Send_First + self.ColT[m].TrackNum
                self.ColT[m].SliderName = mixer.getEventIDName(self.ColT[m].SliderEventID)
            elif self.Page == Page_FX:
                if self.CurPluginID == -1:  # Plugin not selected
                    index = m + self.CurPluginOffset + (self.TrackCount if self.isExtension else 0)
                    if index < 10:
                        self.PluginTrack = mixer.trackNumber()
                        self.ColT[m].CurID = mixer.getTrackPluginId(self.PluginTrack, index)
                        self.ColT[m].SliderEventID = self.ColT[m].CurID + midi.REC_Plug_MixLevel
                        self.ColT[m].SliderName = mixer.getEventIDName(self.ColT[m].SliderEventID)

                        IsValid = mixer.isTrackPluginValid(self.PluginTrack, index)
                        if IsValid:
                            self.ColT[m].TrackName = plugins.getPluginName(self.PluginTrack, index)
                    else:
                        self.ColT[m].SliderEventID = midi.REC_None
                        self.ColT[m].SliderName = ''

                else:  # Plugin selected
                    pluginIndex = self.CurPluginID + self.CurPluginOffset
                    self.ColT[m].CurID = mixer.getTrackPluginId(self.PluginTrack, pluginIndex)
                    if (plugins.isValid(self.PluginTrack, pluginIndex)):
                        paramIndex = m + self.PluginParamOffset + (self.TrackCount if self.isExtension else 0)
                        if paramIndex < plugins.getParamCount(self.PluginTrack, pluginIndex):
                            self.ColT[m].TrackName = plugins.getParamName(paramIndex, self.PluginTrack, pluginIndex)
                        self.ColT[m].KnobMode = 2
                        self.ColT[m].KnobEventID = self.ColT[m].CurID + midi.REC_PlugReserved
            elif self.Page == Page_EQ:
                if m < 3:
                    # gain & freq
                    self.ColT[m].SliderEventID = CurID + midi.REC_Mixer_EQ_Gain + m
                    self.ColT[m].KnobResetEventID = self.ColT[m].SliderEventID
                    self.ColT[m].SliderName = mixer.getEventIDName(self.ColT[m].SliderEventID)
                    self.ColT[m].KnobEventID = CurID + midi.REC_Mixer_EQ_Freq + m
                    self.ColT[m].KnobName = mixer.getEventIDName(self.ColT[m].KnobEventID)
                    self.ColT[m].KnobResetValue = midi.FromMIDI_Max >> 1
                    self.ColT[m].KnobCenter = -2
                    self.ColT[m].KnobMode = 0
                elif m < 6:
                    # Q
                    self.ColT[m].SliderEventID = CurID + midi.REC_Mixer_EQ_Q + m - 3
                    self.ColT[m].KnobResetEventID = self.ColT[m].SliderEventID
                    self.ColT[m].SliderName = mixer.getEventIDName(self.ColT[m].SliderEventID)
                    self.ColT[m].KnobEventID = self.ColT[m].SliderEventID
                    self.ColT[m].KnobName = self.ColT[m].SliderName
                    self.ColT[m].KnobResetValue = 17500
                    self.ColT[m].KnobCenter = -1
                    self.ColT[m].KnobMode = 2
                else:
                    self.ColT[m].SliderEventID = -1
                    self.ColT[m].KnobEventID = -1
                    self.ColT[m].KnobMode = 4

                self.ColT[m].KnobEventID, self.ColT[m].SliderEventID = utils.SwapInt(self.ColT[m].KnobEventID, self.ColT[m].SliderEventID)
                self.ColT[m].SliderName = self.ColT[m].KnobName
                self.ColT[m].KnobName = self.ColT[m].SliderName
                self.ColT[m].KnobMode = 2
                if not (self.Page in [Page_Pan, Page_FX, Page_EQ, Page_Volume]):
                    self.ColT[m].KnobCenter = -1
                    self.ColT[m].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                    self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID

            self.ColT[m].LastValueIndex = 48 + m * 6
            self.ColT[m].Peak = 0
            self.ColT[m].ZPeak = False
            self.UpdateCol(m)

    #############################################################################################################################
    #                                                                                                                           #
    #  SETS UP THE FIRST TRACK AFTER TRACK RELATED MOVEMENT OPERATIONS ARE CARRIED OUT                                          #
    #                                                                                                                           #
    #############################################################################################################################
    def SetFirstTrack(self, Value):
        self.FirstTrackT[self.FirstTrack] = (
            Value + mixer.trackCount()) % mixer.trackCount()
        s = utils.Zeros(self.FirstTrackT[self.FirstTrack], 2, ' ')
        self.UpdateColT()
        device.hardwareRefreshMixerTrack(-1)
