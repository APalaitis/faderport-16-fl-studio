###########################################################
# name=MCUE Presonus FaderPort 16 Extender
# receiveFrom=MCUE Presonus FaderPort 16
# supportedDevices=Configured MCUE device Extenders
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=254916#p1607888
###########################################################
import math
import time

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

import common

##################################
# CLASS FOR GENERAL FUNCTIONALITY
##################################

class TMackieCU(common.TMackieCU_Base):
    def __init__(self):
        common.TMackieCU_Base.__init__(self, True)

# --------------------------------------------------------------------------------------------------------------------------------
# EVENTS:
# --------------------------------------------------------------------------------------------------------------------------------               
    #############################################################################################################################
    #                                                                                                                           #
    #  Called for all MIDI messages that were not handled by OnMidiIn.       .                                                  #
    #                                                                                                                           #
    #############################################################################################################################
    def OnMidiMsg(self, event):
        #  FLC Processing:
        #if (event.data1 >= 0x36 and event.data1<=0x45):
        #    pointer=event.data1-0x36
        #    event.data1=(event.data1+FLC_Mapping[pointer])
        event.data1=common.MCUELU.get(event.data1,event.data1)
        if common.ThrottleStickSupport:
            ###################################################
            ## Do something relevant with the Throttle Stick:
            ###################################################
            self.PreviousCommand=event.data1
            if event.data1==0x0:
                if (ui.getFocused(midi.widPlaylist) or (ui.getFocused(midi.widPianoRoll))):  #Zoom in or out of the PlayList
                    ui.horZoom(event.data2-self.LastData2)
                    ui.verZoom(event.data2-self.LastData2)
                    self.LastData2=(event.data2)
                elif  (ui.getFocused(midi.widMixer)): #Raise or lower volume of selected tracks
                    for x in range(0, 24): #mixer.trackCount()):
                        if mixer.isTrackEnabled(x):
                            mixer.setTrackVolume(x,mixer.getTrackVolume(x)+((event.data2-64)/264))  #I think we can improve on this algorythm?


        #############################################################################################################################
        #                                                                                                                           #
        #   CONTROL CHANGE                                                                                                          #
        #                                                                                                                           #
        #############################################################################################################################
        if (event.midiId == midi.MIDI_CONTROLCHANGE):
            if (event.midiChan == 0):
                event.inEv = event.data2
                if event.inEv >= 0x40:
                    event.outEv = -(event.inEv - 0x40)
                else:
                    event.outEv = event.inEv
                   
                if event.data1 == 0x3C:             
                    event.handled = True

                # knobs
                elif event.data1 in [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]:
                    r = utils.KnobAccelToRes2(event.outEv)  # todo outev signof
                    Res = r * (1 / (40 * 2.5))
                    self.SetKnobValue(event.data1 - 0x10, event.outEv, Res)
                    event.handled = True
                else:
                    event.handled = False  # for extra CCs in emulators
            else:
                event.handled = False  # for extra CCs in emulators

        #############################################################################################################################
        #                                                                                                                           #
        #   PITCH BEND (FADERS)                                                                                                     #
        #                                                                                                                           #
        #############################################################################################################################
        elif event.midiId == midi.MIDI_PITCHBEND:
            self.handleFaders(event)

        #############################################################################################################################
        #                                                                                                                           #
        #   MIDI NOTEON/OFF                                                                                                         #
        #                                                                                                                           #
        #############################################################################################################################
        elif (event.midiId == midi.MIDI_NOTEON) | (event.midiId == midi.MIDI_NOTEOFF):  # NOTE
            if event.midiId == midi.MIDI_NOTEON:
                if event.data2 > 0:
                    if event.data1 in [0x68, 0x69, 0x70]:
                        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)

                    # -----------
                    # Piano Roll
                    # -----------
                    if event.data1 == 0x90: 
                        if ui.getVisible(midi.widPianoRoll):
                            ui.hideWindow(midi.widPianoRoll)
                            self.SendMsg2("The Piano Roll Window is Closed")
                        else:
                            ui.showWindow(midi.widPianoRoll)
                            ui.setFocused(midi.widPianoRoll)
                            self.SendMsg2("The Piano Roll is Open")

                    # -----------------
                    # Hide all Windows
                    # -----------------
                    if event.data1 == 0x91: 
                        for x in range(0, 5):
                            ui.hideWindow(x)


                    # --------------
                    # Playlist
                    # --------------
                    if event.data1 == 0x92: 
                        if ui.getVisible(midi.widPlaylist):
                            ui.hideWindow(midi.widPlaylist)
                            self.SendMsg2("The PlayList/Song Window is Closed")
                        else:
                            ui.showWindow(midi.widPlaylist)
                            ui.setFocused(midi.widPlaylist)
                            self.SendMsg2("The Playlist/Song Window is Open")

                    # -------
                    # MIXER
                    # -------
                    elif event.data1 == 0x3F:  # Mixer
                        if self.Shift:
                            if self.ShowTrackNumbers:
                                self.ShowTrackNumbers = False
                            else:
                                self.ShowTrackNumbers = True
                            self.UpdateTextDisplay()
                        else:
                            if ui.getVisible(midi.widMixer):
                                ui.hideWindow(midi.widMixer)
                                self.SendMsg2("The Mixer Window is Closed")
                            else:
                                ui.showWindow(midi.widMixer)
                                ui.setFocused(midi.widMixer)
                                self.SendMsg2("The Mixer Window is Open")
                    # ---------
                    # CHANNEL
                    # --------
                    elif event.data1 == 0x40:  # Channel Rack
                        if self.Shift:
                            if ui.getFocused(5) == 0:
                                channels.focusEditor(channels.getChannelIndex(
                                    channels.selectedChannel()))
                                channels.showCSForm(channels.getChannelIndex(
                                    channels.selectedChannel(-1)))
                            else:
                                channels.focusEditor(channels.getChannelIndex(
                                    channels.selectedChannel()))
                                channels.showCSForm(channels.getChannelIndex(
                                    channels.selectedChannel(-1)), 0)
                        else:
                            if ui.getVisible(midi.widChannelRack):
                                ui.hideWindow(midi.widChannelRack)
                                self.SendMsg2("The Channel Rack Window is Closed")
                            else:
                                ui.showWindow(midi.widChannelRack)
                                ui.setFocused(midi.widChannelRack)
                                self.SendMsg2("The Channel Rack Window is Open")
                    # -------
                    # TEMPO
                    # -------
                    elif event.data1 == 0x41:
                        transport.globalTransport(midi.FPT_TapTempo, 1)
                        s = str(mixer.getCurrentTempo(True))[:-2]
                        self.SendMsg2("Tempo: "+s)
                    # --------
                    # WINDOW
                    # --------
                    elif event.data1 == 0x4c:
                        ui.nextWindow()
                        s = ui.getFocusedFormCaption()
                        if s != "":
                            self.SendMsg2('Current window: ' + s)

                if (event.pmeFlags & midi.PME_System != 0):
                    # ---------------
                    # MODE (METERS)
                    # ---------------
                    if event.data1 == 0x34:
                        if event.data2 > 0:                           
                            if self.Shift:
                                self.FirstTrackT[self.FirstTrack] = 1
                                self.SetPage(self.Page)
                                self.SendMsg2(
                                    'Extender on ' + self.MackieCU_ExtenderPosT[self.ExtenderPos], 1500)
                            else:                             
                                self.MeterMode = (self.MeterMode + 1) % 3
                                self.SendMsg2(self.MackieCU_MeterModeNameT[self.MeterMode])
                                self.ShowSelectedTrackInTimeWindow=(self.MeterMode==2) #Selected Track
                                self.UpdateMeterMode()
                                #device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                                device.midiOutSysex(bytes(bytearray([0xd1, 0, 0xF7])))
                                device.midiOutSysex(bytes(bytearray([0xd1, 16, 0xF7])))
                    # -------------------------------
                    # BANK UP / DOWN (8/16 - 24 tracks is static?)
                    # -------------------------------
                    elif (event.data1 == 0x2E) | (event.data1 == 0x2F):  # mixer bank
                        if event.data2 > 0:
                            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
                            #device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            for m in range(0,  0 if self.isExtension else 1):
                                self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
                                #device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            
                            if self.MixerScroll:
                                if self.ColT[event.midiChan].TrackNum >= 0:
                                    if mixer.trackNumber != self.ColT[event.midiChan].TrackNum:
                                        mixer.setTrackNumber(self.ColT[event.midiChan].TrackNum+(-1), midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

                            if (self.CurPluginID != -1):  # Selected Plugin
                                if (event.data1 == 0x2E) & (self.PluginParamOffset >= 8):
                                    self.PluginParamOffset -= 8
                                elif (event.data1 == 0x2F) & (self.PluginParamOffset + 8 < plugins.getParamCount(mixer.trackNumber(), self.CurPluginID + self.CurPluginOffset) - 8):
                                    self.PluginParamOffset += 8
                            else:  # No Selected Plugin
                                if (event.data1 == 0x2E) & (self.CurPluginOffset >= 2):
                                    self.CurPluginOffset -= 2
                                elif (event.data1 == 0x2F) & (self.CurPluginOffset < 2):
                                    self.CurPluginOffset += 2

                    # ---------------------------
                    # MOVE UP / DOWN (1 track)
                    # ---------------------------
                    elif (event.data1 == 0x30) | (event.data1 == 0x31):
                        if event.data2 > 0:
                            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 1 + int(event.data1 == 0x31) * 2)
                            #device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))

                    # ---------------------
                    # PAGE SELECTORS
                    # ---------------------
                    elif event.data1 == 0x32:  # self.Flip
                        if event.data2 > 0:
                            self.Flip = not self.Flip
                            #device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            self.UpdateColT()
                            self.UpdateLEDs()

                    elif event.data1 in common.PageSelectors:
                        if event.data2 > 0:
                            n = event.data1 - 0x28
                            self.SetPage(n)
                    # ------------
                    # SELECT BUTTONS (EX)
                    # ------------
                    elif event.data1 in common.SelectButtonsEX:
                        if event.data2 > 0:
                            isReceiver = event.data2 == 0x7e
                            selectIndex = event.data1 - 0x20
                            selectIndex += (8 if not isReceiver else 0)
                            if self.Page == common.MackieCUPage_EQ:
                                if event.data1 == 0x27:  # "Reset All"
                                    self.SetKnobValue(0, midi.MaxInt)
                                    self.SetKnobValue(1, midi.MaxInt)
                                    self.SetKnobValue(2, midi.MaxInt)
                                    self.SetKnobValue(3, midi.MaxInt)
                                    self.SetKnobValue(4, midi.MaxInt)
                                    self.SetKnobValue(5, midi.MaxInt)
                                    self.SetKnobValue(6, midi.MaxInt)
                                    self.SetKnobValue(7, midi.MaxInt)
                                    SendMsg2("All EQ levels reset")
                            elif self.Page == common.MackieCUPage_FX:
                                if self.CurPluginID == -1:
                                    self.SetKnobValue(selectIndex, midi.MaxInt)
                                    if not isReceiver:
                                        device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (0x7e << 16))
                                else:
                                    # AP: Ignore button presses, there's no functionality that makes sense in this case
                                    pass
                            elif self.Page == common.MackieCUPage_Sends:
                                mixer.setRouteTo(
                                    mixer.trackNumber(),
                                    selectIndex + 1,
                                    not mixer.getRouteSendActive(mixer.trackNumber(), selectIndex + 1)
                                )
                            else:
                                self.SetKnobValue(selectIndex, midi.MaxInt)

                if (event.pmeFlags & midi.PME_System_Safe != 0):              
                    if False:  #for script compatibility with extender
                        0+1
                    # --------
                    # SELECT
                    # --------
                    elif (event.data1 >= 0x18) & (event.data1 <= 0x1F):
                        if event.data2 > 0:
                            i = event.data1 - 0x18

                            ui.showWindow(midi.widMixer)
                            ui.setFocused(midi.widMixer)
                            self.UpdateLEDs()
                            mixer.setTrackNumber(
                                self.ColT[i].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

                            if self.Control:  # Link channel to track
                                mixer.linkTrackToChannel(midi.ROUTE_ToThis)
                            # Show Full Trackname on second display:
                            # EXPAND WITH CONTEXT?
                            SendMsg2(mixer.getTrackName(self.ColT[i].TrackNum))

                    # ------
                    # SOLO
                    # ------
                    elif (event.data1 >= 0x8) & (event.data1 <= 0xF):  # solo
                        if event.data2 > 0:
                            i = event.data1 - 0x8
                            self.ColT[i].solomode = midi.fxSoloModeWithDestTracks
                            if self.Shift:
                                common.Include(self.ColT[i].solomode,midi.fxSoloModeWithSourceTracks)
                            mixer.soloTrack(self.ColT[i].TrackNum,
                                            midi.fxSoloToggle, self.ColT[i].solomode)
                            # mixer.setTrackNumber(
                            #     self.ColT[i].TrackNum, midi.curfxScrollToMakeVisible)

                    # ------
                    # MUTE
                    # ------
                    elif (event.data1 >= 0x10) & (event.data1 <= 0x17):  # mute
                        if event.data2 > 0:
                            mixer.enableTrack(
                                self.ColT[event.data1 - 0x10].TrackNum)

                    elif (event.data1 >= 0x0) & (event.data1 <= 0x7):  # arm
                        if event.data2 > 0:
                            mixer.armTrack(self.ColT[event.data1].TrackNum)
                            if mixer.isTrackArmed(self.ColT[event.data1].TrackNum):
                                self.SendMsg2(mixer.getTrackName(
                                    self.ColT[event.data1].TrackNum) + ' recording to ' + mixer.getTrackRecordingFileName(self.ColT[event.data1].TrackNum), 2500)
                            else:
                                self.SendMsg2(mixer.getTrackName(
                                    self.ColT[event.data1].TrackNum) + ' unarmed')
                    # ------
                    # SAVE
                    # ------
                    elif event.data1 == 0x50:  # save/save new
                        transport.globalTransport(
                            midi.FPT_Save + int(self.Shift), int(event.data2 > 0) * 2, event.pmeFlags)
                    event.handled = True
                else:
                    event.handled = False
            else:
                event.handled = False


# -------------------------------------------------------------------------------------------------------------------------------
# PROCEDURES
# -------------------------------------------------------------------------------------------------------------------------------

MackieCU = TMackieCU()

#EOF
def OnInit():
    MackieCU.OnInit()


def OnDeInit():
    MackieCU.OnDeInit()


def OnDirtyMixerTrack(SetTrackNum):
    MackieCU.OnDirtyMixerTrack(SetTrackNum)


def OnRefresh(Flags):
    MackieCU.OnRefresh(Flags)


def OnMidiMsg(event):
    MackieCU.OnMidiMsg(event)


def SendMsg2(Msg, Duration=1000):
    MackieCU.SendMsg2(Msg, Duration)

def OnSendTempMsg(Msg, Duration=1000):
    MackieCU.OnSendTempMsg(Msg, Duration)


def OnUpdateBeatIndicator(Value):
    MackieCU.OnUpdateBeatIndicator(Value)


def OnUpdateMeters():
    MackieCU.OnUpdateMeters()


def OnIdle():
    MackieCU.OnIdle()


def OnWaitingForInput():
    MackieCU.OnWaitingForInput()