###########################################################
# name=MCUE Presonus FaderPort 16
# receiveFrom=MCUE Presonus FaderPort 16 Extender
# supportedDevices=MCU Compatible
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
        common.TMackieCU_Base.__init__(self, False)

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
        ArrowStepT = [2, -2, -1, 1] #--
        CutCopyMsgT = ('Cut', 'Copy', 'Paste', 'Insert','Delete')  #--


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
                    self.Jog(event) #--
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
#->                    
                    # F1..F8
                    if self.Shift & (event.data1 in [0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]):
                        transport.globalTransport(midi.FPT_F1 - 0x36 +
                                                  event.data1, int(event.data2 > 0) * 2, event.pmeFlags)
                        event.data1 = 0xFF

                    if self.Control & (event.data1 in [0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]):
                        ui.showWindow(midi.widPlaylist)
                        ui.setFocused(midi.widPlaylist)
                        transport.globalTransport(midi.FPT_Menu, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                        time.sleep(0.1)
                        f = int(1 + event.data1 - 0x36)
                        for x in range(0, f):
                            transport.globalTransport(midi.FPT_Down, int(
                                event.data2 > 0) * 2, event.pmeFlags)
                            time.sleep(0.01)
                        time.sleep(0.1)
                        transport.globalTransport(midi.FPT_Enter, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                        event.data1 = 0xFF
#-<
                    # ---------------
                    # MODE (METERS)
                    # ---------------
                    if event.data1 == 0x34:
                        if event.data2 > 0:                           
                            if self.Shift:
                                self.ExtenderPos = abs(self.ExtenderPos - 1)
                                self.FirstTrackT[self.FirstTrack] = 1
                                self.SetPage(self.Page)
                                self.SendMsg2(
                                    'Extender on ' + self.MackieCU_ExtenderPosT[self.ExtenderPos], 1500)
                            else:                             
                                self.MeterMode = (self.MeterMode + 1) % 3
                                self.SendMsg2(self.MackieCU_MeterModeNameT[self.MeterMode])
                                self.ShowSelectedTrackInTimeWindow=(self.MeterMode==2) #Selected Track
                                self.UpdateMeterMode()
                                device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                                device.midiOutSysex(bytes(bytearray([0xd1, 0, 0xF7])))
                                device.midiOutSysex(bytes(bytearray([0xd1, 16, 0xF7])))
#->                                
                    # -------------
                    # TIME FORMAT
                    # -------------
                    elif event.data1 == 0x35:
                        if event.data2 > 0:
                            ui.setTimeDispMin()
                            if ui.getTimeDispMin():
                                SendMsg2("Time display set to M:S:CS (Time)")
                            else:
                                SendMsg2("Time display set to B:S:T (Beats)")
                    # --------------
                    # SCRUB BUTTON
                    # --------------
                    elif event.data1 == 0x65:  # self.Scrub
                        if event.data2 > 0:
                            self.Scrub = not self.Scrub
                            self.UpdateLEDs()

                    # --------------
                    # JOG SOURCES
                    # --------------
                    # elif event.data1 in [0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x48, 0x55, 0x64, 0x46, 0x4C]: (X-Touch specific?)
                    elif event.data1 in [0x3E, 0x3F, 0x40, 0x41, 0x48, 0x64, 0x46, 0x4C]:
                        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)
                        if event.data1 in [0x64, 0x4C]:
                            device.directFeedback(event)
                        if event.data2 == 0:
                            if self.JogSource == event.data1:
                                self.SetJogSource(0)
                        else:
                            self.SetJogSource(event.data1)
                            if event.data1 == 0x48:  # markers
                                if ui.getVisible(midi.widPlaylist):
                                    ui.hideWindow(midi.widPlaylist)
                                else:
                                    ui.showWindow(midi.widPlaylist)
                                    ui.setFocused(midi.widPlaylist)
                        event.outEv = 0
                        self.Jog(event)  # for visual feedback


                    # ---------------
                    # ARROW BUTTONS
                    # ---------------
                    elif event.data1 in [0x60, 0x61, 0x62, 0x63]:
                        if self.JogSource == 0x64:
                            if event.data1 == 0x60:
                                transport.globalTransport(
                                    midi.FPT_VZoomJog + int(self.Shift), -1, event.pmeFlags)
                            elif event.data1 == 0x61:
                                transport.globalTransport(
                                    midi.FPT_VZoomJog + int(self.Shift), 1, event.pmeFlags)
                            elif event.data1 == 0x62:
                                transport.globalTransport(
                                    midi.FPT_HZoomJog + int(self.Shift), -1, event.pmeFlags)
                            elif event.data1 == 0x63:
                                transport.globalTransport(
                                    midi.FPT_HZoomJog + int(self.Shift), 1, event.pmeFlags)

                        elif self.JogSource == 0:
                            transport.globalTransport(
                                midi.FPT_Up - 0x60 + event.data1, int(event.data2 > 0) * 2, event.pmeFlags)
                        else:
                            if event.data2 > 0:
                                event.inEv = ArrowStepT[event.data1 -
                                                        0x60]
                                event.outEv = event.inEv
                                self.Jog(event)
                    # ------------
                    # COUNTDOWN:
                    # ------------
                    elif event.data1 == 0x58:
                        if event.data2 == 0:
                            transport.globalTransport(midi.FPT_CountDown, 1)
                            if ui.isPrecountEnabled():
                                SendMsg2("Count in enabled for recording")
                            else:
                                SendMsg2("Count in disabled for recording")
                    # ----------------
                    # PATTERN / SONG
                    # ----------------
                    elif event.data1 == 0x5a:
                        if event.data2 > 0:
                            transport.globalTransport(midi.FPT_Loop, 1)
                            Looper = transport.getLoopMode()
                            if (Looper == midi.SM_Pat):
                                self.SendMsg2("Pattern Mode")
                            else:
                                self.SendMsg2("Song Mode")
                    # -------------------
                    # CONTROL SMOOTHING
                    # -------------------
                    elif event.data1 == 0x33:
                        if event.data2 > 0:
                            self.SmoothSpeed = int(self.SmoothSpeed == 0) * 469
                            self.UpdateLEDs()
                            self.SendMsg2('Control smoothing ' +
                                          common.OffOnStr[int(self.SmoothSpeed > 0)])

                    # ------------------------------
                    # CUT/COPY/PASTE/INSERT/DELETE
                    # ------------------------------
                    elif event.data1 in [0x36, 0x37, 0x38, 0x39, 0x3A]:
                        transport.globalTransport(midi.FPT_Cut + event.data1 -
                                                  0x36, int(event.data2 > 0) * 2, event.pmeFlags)
                        if event.data2 > 0:
                            self.SendMsg2(
                                CutCopyMsgT[midi.FPT_Cut + event.data1 - 0x36 - 50])
                    # -------------------
                    # TOGGLE UNDO / REDO
                    # -------------------
                    elif event.data1 in [0x3C, 0x3d]:
                        if (transport.globalTransport(midi.FPT_Undo, int(event.data2 > 0) * 2, event.pmeFlags) == midi.GT_Global) & (event.data2 > 0):
                            self.SendMsg2(ui.getHintMsg() + ' (level ' + general.getUndoLevelHint() + ')')

                    # --------
                    # PATTERN
                    # --------
                        elif event.data1 == 0x3E:
                            if event.data2 > 0:
                                # if self.Shift:
                                #    #open the piano roll:
                                #    ui.hideWindow(midi.widPlaylist)
                                #    ui.showWindow(midi.widPianoRoll)
                                #    ui.setFocused(midi.widPianoRoll)
                                # else:
                                if ui.getVisible(midi.widPlaylist):
                                    ui.hideWindow(midi.widPlaylist)
                                else:
                                    ui.showWindow(midi.widPlaylist)
                                    ui.setFocused(midi.widPlaylist)
                                    sel = -1
                                    for p in range(0, patterns.patternCount()-1):
                                        if patterns.isPatternSelected(p):
                                            sel = p
                                            break
                                    if sel == -1:
                                        SendMsg2(
                                            "Playlist Opened (use jog dial to navigate patterns)")

                                    else:
                                        SendMsg2(
                                            "Pattern Selected:"+patterns.getPatternName(p)+" (use jog dial to navigate)")
                                        patterns.selectPattern(p)
                                # Ensure that we are in Pattern Mode:
                                if transport.getLoopMode() == 1:
                                    transport.globalTransport(midi.FPT_Loop, int(
                                        event.data2 > 0) * 2, event.pmeFlags)

                    # ---------------------------
                    # FREE1 - UNMUTE ALL TRACKS
                    # ---------------------------
                    elif event.data1 == 0x42:
                        if event.data2 > 0:
                            if self.Shift:
                                for m in range(0,  mixer.trackCount()):
                                    if mixer.isTrackArmed(m):
                                        mixer.armTrack(m)
                                self.SendMsg2("All tracks disarmed")
                            else:
                                for m in range(0,  mixer.trackCount()):
                                    if mixer.isTrackMuted(m):
                                        mixer.muteTrack(m)
                                self.SendMsg2("All tracks unmuted")

                    # -----------------------------------------------------------
                    # FREE2 - SELECT FIRST TRACK ON MIXER BANKING (DEFAULT OFF)
                    # -----------------------------------------------------------
                  
                    elif event.data1 == 0x43:
                        if False: # LightendarkenMixercolours:
                            if event.data2 > 0:
                                for m in range(0,  mixer.trackCount()):
                                    c=mixer.getTrackColor(m)
                                    mixer.setTrackColor(m, utils.LightenColor(c,100))
                            else:
                                for m in range(0,  mixer.trackCount()):
                                    c=mixer.getTrackColor(m)
                                    mixer.setTrackColor(m, utils.LightenColor(c,-100))
                        else:
                            if event.data2 > 0:
                                if self.MixerScroll:
                                    self.MixerScroll = False
                                    self.SendMsg2(
                                        "Banking functionality reset to default")
                                else:
                                    self.MixerScroll = True
                                    self.SendMsg2(
                                        "Banking always selects and shows first track in the bank")


                    # ----------------------------------------------
                    # FREE4 - DEFAULTING BANKING COLOURS FOR MIXER
                    # ---------------------------------------------

                    # Could add more options here?
                    # Would be good to be able to invoke the new colour picker?
                    elif event.data1 == 0x45:
                        if event.data2 > 0:
                            # Activate the mixer so we can see what is happening:
                            ui.showWindow(midi.widMixer)
                            ui.setFocused(midi.widMixer)
                            s = "Defaulted"
                            if self.Shift:
                                for m in range(0,  mixer.trackCount()):
                                    mixer.setTrackColor(m, -10261391)
                            else:
                                if self.colourOptions == 0:
                                    s = "Banking Optimised (with gradient fills)"
                                    self.colourOptions = 1
                                    for m in range(0,  mixer.trackCount()):
                                        mixer.setTrackColor(m, common.TrackColours[m])
                                        #LightenColor(Color, Value)
                                        # self.setLinkedChannelColour(m,TrackColours[m])
                                else:
                                    self.colourOptions = 0
                                    s = "Banking Optimised (with solid colours)"
                                    splitter = 0
                                    color = common.BankingColours[splitter]
                                    for m in range(0,  mixer.trackCount()):
                                        mixer.setTrackColor(m,color)
                                        if math.remainder(m, 8) == 0:
                                            splitter = splitter+1
                                            if splitter == 12:
                                                splitter = 0
                                            color = common.BankingColours[splitter]
                            self.SendMsg2("Mixer colours:"+s)

                    # ---------
                    # BROWSER
                    # ---------
                    elif event.data1 == 0x4a:
                        ui.showWindow(midi.widBrowser)
                        # ui.setFocused(midi.widBrowser)
                        self.SendMsg2("Browser Window Open")

                    # ------
                    # MAIN
                    # ------
                    elif event.data1 == 0x4b:
                        if event.data2 > 0:
                            transport.globalTransport(
                                midi.FPT_F11, 1)  # Main song Window
                            self.SendMsg2("Main Window Open")
                            # ui.showWindow(midi.widChannelRack)
                            # ui.setFocused(midi.widChannelRack)
#-<
                    # -------------------------------
                    # BANK UP / DOWN (8/16 - 24 tracks is static?)
                    # -------------------------------
                    elif (event.data1 == 0x2E) | (event.data1 == 0x2F):  # mixer bank
                        if event.data2 > 0:
                            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
                            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            for m in range(0,  0 if self.isExtension else 1):
                                self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
                                device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            
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
                            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))

                    # ---------------------
                    # PAGE SELECTORS
                    # ---------------------
                    elif event.data1 == 0x32:  # self.Flip
                        if event.data2 > 0:
                            self.Flip = not self.Flip
                            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            self.UpdateColT()
                            self.UpdateLEDs()

                    elif event.data1 in common.PageSelectors:
                        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)
                        if event.data2 > 0:
                            n = event.data1 - 0x28
                            self.SetPage(n)
                            self.SendMsg2(self.MackieCU_PageNameT[n])
                            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))

                    elif event.data1 == 0x54:  # self.Shift
                        self.Shift = event.data2 > 0
                        device.directFeedback(event)

                    # elif event.data1 == 0x47:  # self.Option
                    #    self.Option = event.data2 > 0
                    #    device.directFeedback(event)
                    # elif event.data1 == 0x49:  # self.Alt
                    #    self.Alt = event.data2 > 0
                    #    device.directFeedback(event)

                    # ------
                    # MENU
                    # ------
                    elif event.data1 == 0x51:  # menu (was self.Control)
                        #    self.Control = event.data2 > 0
                        #    device.directFeedback(event)
                        self.SendMsg2(
                            "Use the arrow & enter keys to navigate the menu")
                        transport.globalTransport(midi.FPT_Menu, int(
                            event.data2 > 0) * 2, event.pmeFlags)

                    # --------
                    # EDISON
                    # --------
                    elif event.data1 == 0x55:  # -1:  # open audio editor in current mixer track
                        if event.data2 > 0:
                            ui.launchAudioEditor(False, '', mixer.trackNumber(),
                                                 'AudioLoggerTrack.fst', '')
                            self.SendMsg2(
                                'Audio editor ready for track '+mixer.getTrackName(mixer.trackNumber()))

                    # -----------
                    # METRONOME
                    # -----------
                    elif event.data1 == 0x59:  # metronome/button self.Clicking
                        if event.data2 > 0:
                            if self.Shift:
                                self.Clicking = not self.Clicking
                                self.UpdateClicking()
                                self.SendMsg2(
                                    'Metronome self clicking is ' + common.OffOnStr[self.Clicking])
                            else:
                                transport.globalTransport(
                                    midi.FPT_Metronome, 1, event.pmeFlags)
                                # if (ui.isMetronomeEnabled):
                                #    self.SendMsg2("Metronome is Enabled")
                                # else:
                                #    self.SendMsg2("Metronome is Disabled")

                    elif event.data1 == -1:  # precount
                        if event.data2 > 0:
                            transport.globalTransport(
                                midi.FPT_CountDown, 1, event.pmeFlags)

                    # ---------
                    # << & >>
                    # ---------
                    elif (event.data1 == 0x5B) | (event.data1 == 0x5C):
                        if self.Shift:
                            if event.data2 == 0:
                                v2 = 1
                            elif event.data1 == 0x5B:
                                v2 = 0.5
                            else:
                                v2 = 2
                            transport.setPlaybackSpeed(v2)
                        else:
                            transport.globalTransport(midi.FPT_Rewind + int(event.data1 ==
                                                                            0x5C), int(event.data2 > 0) * 2, event.pmeFlags)
                        device.directFeedback(event)

                    # ------
                    # STOP
                    # ------
                    elif event.data1 == 0x5D:
                        transport.globalTransport(midi.FPT_Stop, int(
                            event.data2 > 0) * 2, event.pmeFlags)

                    # ------
                    # PLAY
                    # ------
                    elif event.data1 == 0x5E:
                        transport.globalTransport(midi.FPT_Play, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                    # --------
                    # RECORD
                    # --------
                    elif event.data1 == 0x5F:  # record
                        transport.globalTransport(midi.FPT_Record, int(
                            event.data2 > 0) * 2, event.pmeFlags)

                    # -------------
                    # SONG / LOOP
                    # -------------
                    elif event.data1 == 0x5A:  # song/loop
                        transport.globalTransport(midi.FPT_Loop, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                    # ------
                    # SNAP
                    # ------
                    elif event.data1 == 0x4E:
                        if self.Shift:
                            if event.data2 > 0:
                                transport.globalTransport(
                                    midi.FPT_SnapMode, 1, event.pmeFlags)
                            else:
                                transport.globalTransport(midi.FPT_Snap, int(
                                    event.data2 > 0) * 2, event.pmeFlags)

                    # --------
                    # ESCAPE
                    # --------
                    elif event.data1 == 0x52:
                        if (self.Shift == False):
                            transport.globalTransport(
                                midi.FPT_Escape + int(self.Shift) * 2, int(event.data2 > 0) * 2, event.pmeFlags)
                    # --------
                    # ENTER
                    # --------
                    elif event.data1 == 0x53:
                        transport.globalTransport(
                            midi.FPT_Enter + int(self.Shift) * 2, int(event.data2 > 0) * 2, event.pmeFlags)
#-<
                    # ------------
                    # SELECT BUTTONS (EX)
                    # ------------
                    elif event.data1 in common.SelectButtonsEX:
                        if event.data2 > 0:
                            isReceiver = event.data2 == 0x7e
                            selectIndex = event.data1 - 0x20
                            selectIndex += (8 if isReceiver else 0)
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
#-> 
                    # shift options with f1 ..f8
                    # F1..F8
                    # if self.Shift & (event.data1 in [0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]):
                    #    transport.globalTransport(midi.FPT_F1 - 0x36 +
                    #                              event.data1, int(event.data2 > 0) * 2, event.pmeFlags)
                    #     event.data1 = 0xFF
                    # -----------------------------------------------
                    # LINK SELECTED CHANNELS TO CURRENT MIXER TRACK
                    # -----------------------------------------------
                    elif event.data1 == 0x47:
                        if event.data2 > 0:
                            if self.Shift:
                                mixer.linkTrackToChannel(
                                    midi.ROUTE_StartingFromThis)
                            else:
                                mixer.linkTrackToChannel(midi.ROUTE_ToThis)
                                self.SendMsg2(
                                    "Chanel Track and Mixer Track now linked")
                    # -----------
                    # ITEM MENU
                    # -----------
                    elif event.data1 == 0x3B:
                        transport.globalTransport(midi.FPT_ItemMenu, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                        if event.data2 > 0:
                            self.SendMsg2('Item Menu', 10)

                    # -------------------
                    # IN / OUT / SELECT
                    # -------------------
                    elif event.data1 in [0x4D, 0x4E, 0x4F]:
                        # Ensure the playlist is selected:
                        ui.showWindow(midi.widPlaylist)
                        ui.setFocused(midi.widPlaylist)
                        SendMsg2("Punching Enabled "+str(event.data1))
                        if event.data1 == 0x4F:
                            n = midi.FPT_Punch
                        else:
                            n = midi.FPT_PunchIn + event.data1 - 0x4D
                        if event.data1 >= 0x4E:
                            self.SliderHoldCount += -1 + \
                                (int(event.data2 > 0) * 2)
                        if not ((event.data1 == 0x4D) & (event.data2 == 0)):
                            device.directFeedback(event)
                        if (event.data1 >= 0x4E) & (event.data2 >= int(event.data1 == 0x4E)):
                            if device.isAssigned():
                                device.midiOutMsg(
                                    (0x4D << 8) + midi.TranzPort_OffOnT[False])
                        if transport.globalTransport(n, int(event.data2 > 0) * 2, event.pmeFlags) == midi.GT_Global:
                            t = -1
                            if n == midi.FPT_Punch:
                                if event.data2 != 1:
                                    t = int(event.data2 != 2)
                            elif event.data2 > 0:
                                t = int(n == midi.FPT_PunchOut)
                            if t >= 0:
                                self.SendMsg2(ui.getHintMsg())

                    # -----------
                    # ADD MARKER
                    # -----------
                    elif (event.data1 == 0x49):
                        if (transport.globalTransport(midi.FPT_AddMarker + int(self.Shift), int(event.data2 > 0) * 2, event.pmeFlags) == midi.GT_Global) & (event.data2 > 0):
                            self.SendMsg2(ui.getHintMsg())
#-<
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
#->
    #############################################################################################################################
    #                                                                                                                           #
    # TRACK SELECTION                                                                                                           #
    #                                                                                                                           #
    #############################################################################################################################

    def TrackSel(self, Index, Step):
        Index = 2 - Index
        device.baseTrackSelect(Index, Step)
        if Index == 0:
            s = channels.getChannelName(channels.channelNumber())
            self.SendMsg2('Selected Channel: ' + s)
        elif Index == 1:
            self.SendMsg2('Selected Mixer track: ' +
                          mixer.getTrackName(mixer.trackNumber()))
        elif Index == 2:
            # if self.Shift:
            #    #open the piano roll:
            #    ui.hideWindow(midi.widPlaylist)
            #    ui.showWindow(midi.widPianoRoll)
            #    ui.setFocused(midi.widPianoRoll)
            # else:
            s = patterns.getPatternName(patterns.patternNumber())
            self.SendMsg2('Selected Pattern: ' + s)
            if transport.getLoopMode() == 1:
                # Ensure that we are in Pattern Mode:
                transport.globalTransport(midi.FPT_Loop, 2)
                patterns.selectPattern(patterns.patternNumber())


    #############################################################################################################################
    #                                                                                                                           #
    # PRINCIPAL JOG DIAL OPERATIONS                                                                                             #
    #                                                                                                                           #
    #############################################################################################################################

    def Jog(self, event):
        if self.JogSource == 0:
            transport.globalTransport(midi.FPT_Jog + int(self.Shift ^ self.Scrub), event.outEv, event.pmeFlags) # relocate
        elif self.JogSource == 0x46:
            transport.globalTransport(midi.FPT_MoveJog, event.outEv, event.pmeFlags)
        elif self.JogSource == 0x48:
            if self.Shift:
                s = 'Marker selection'
            else:
                s = 'Marker jump'
            if event.outEv != 0:
                if transport.globalTransport(midi.FPT_MarkerJumpJog + int(self.Shift), event.outEv, event.pmeFlags) == midi.GT_Global:
                    s = ui.getHintMsg()
            self.SendMsg2(self.ArrowsStr + s, 500)

        elif self.JogSource == 0x3c:
            if event.outEv == 0:
                s = 'Undo history'
            elif transport.globalTransport(midi.FPT_UndoJog, event.outEv, event.pmeFlags) == midi.GT_Global:
                s = ui.GetHintMsg()
            self.SendMsg2(self.ArrowsStr + s + ' (level ' + general.getUndoLevelHint() + ')', 500)

        elif self.JogSource == 0x64:
            if event.outEv != 0:
                transport.globalTransport(midi.FPT_HZoomJog + int(self.Shift), event.outEv, event.pmeFlags)

        elif self.JogSource == 0x4c:

            if event.outEv != 0:
                transport.globalTransport(midi.FPT_WindowJog, event.outEv, event.pmeFlags)
            s = ui.getFocusedFormCaption()
            if s != "":
                self.SendMsg2(self.ArrowsStr + 'Current window: ' + s, 500)

        elif (self.JogSource == 0x3e) | (self.JogSource == 0x3f) | (self.JogSource == 0x40):
            self.TrackSel(self.JogSource - 0x3e, event.outEv)

        elif self.JogSource == 0x41:
            if event.outEv != 0:
                channels.processRECEvent(midi.REC_Tempo, channels.incEventValue(midi.REC_Tempo, event.outEv, midi.EKRes), midi.PME_RECFlagsT[int(event.pmeFlags & midi.PME_LiveInput != 0)] - midi.REC_FromMIDI)
            self.SendMsg2(self.ArrowsStr + 'Tempo: ' + mixer.getEventIDValueString(midi.REC_Tempo, mixer.getCurrentTempo()), 500)

        elif self.JogSource in [common.MackieCUNote_Free1, common.MackieCUNote_Free2, common.MackieCUNote_Free3, common.MackieCUNote_Free4]:
            # CC
            event.data1 = 390 + self.JogSource - common.MackieCUNote_Free1

            if event.outEv != 0:
                event.isIncrement = 1
                s = chr(0x7E + int(event.outEv < 0))
                self.SendMsg2(self.ArrowsStr + 'Free jog ' + str(event.data1) + ': ' + s, 500)
                device.processMIDICC(event)
                return
            else:
                self.SendMsg2(self.ArrowsStr + 'Free jog ' + str(event.data1), 500)
                

    #############################################################################################################################
    #                                                                                                                           #
    #   UPDATE THE TIME DISPLAY                                                                                                 #
    #                                                                                                                           #
    #############################################################################################################################

    def SendTimeMsg(self, Msg):
        TempMsg = bytearray(10)
        for n in range(0, len(Msg)):
            TempMsg[n] = ord(Msg[n])

        if device.isAssigned():
            # send chars that have changed
            for m in range(0, min(len(self.LastTimeMsg), len(TempMsg))):
                if self.LastTimeMsg[m] != TempMsg[m]:
                    device.midiOutMsg(midi.MIDI_CONTROLCHANGE +
                                      ((0x49 - m) << 8) + ((TempMsg[m]) << 16))

        self.LastTimeMsg = TempMsg

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