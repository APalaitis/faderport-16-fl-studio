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

from Constants import *
from Types import *

from Faders import Faders
from TransportControls import TransportControls
from ParamKnob import ParamKnob
from NavigationControls import NavigationControls
from NavigationButtons import NavigationButtons
from Pages import Pages
from Windows import Windows
from SelectControls import SelectControls
from MuteSoloButtons import MuteSoloButtons
from LeftSideButtons import LeftSideButtons
from TopRightButtons import TopRightButtons

#################################
# MAIN
#################################

class Base(
        Faders,
        TransportControls,
        ParamKnob,
        NavigationControls,
        NavigationButtons,
        Pages,
        Windows,
        SelectControls,
        MuteSoloButtons,
        LeftSideButtons,
        TopRightButtons
    ):
    def __init__(self, isFP8: bool = False, isExtension: bool = False):
        self.isFP8 = isFP8
        self.TrackCount = 8 if isFP8 else 16
        self.isExtension = isExtension
        self.FirstTrack = self.TrackCount if isExtension else 0
        for x in range(0, self.TrackCount):
            self.ColT[x] = FaderColumn()

        Faders.__init__(self)
        TransportControls.__init__(self)
        ParamKnob.__init__(self)
        NavigationControls.__init__(self)
        NavigationButtons.__init__(self)
        Pages.__init__(self)
        Windows.__init__(self)
        SelectControls.__init__(self)
        MuteSoloButtons.__init__(self)
        LeftSideButtons.__init__(self)
        TopRightButtons.__init__(self)


# -------------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
# -------------------------------------------------------------------------------------------------------------------------------
    
    
    #############################################################################################################################
    #                                                                                                                           #
    #  Called when the script has been started.                                                                                 #
    #                                                                                                                           #
    #############################################################################################################################
    def OnInit(self):
        self.FirstTrack = 0
        self.FirstTrackT[0] = self.FirstTrack
        self.SmoothSpeed = 469

        device.setHasMeters()
        self.SetPage(self.Page)
        ui.setHintMsg(device.getName())    
        self.UpdateValueBars()

    #############################################################################################################################
    #                                                                                                                           #
    #   Called before the script will be stopped.                                                                               #
    #                                                                                                                           #
    #############################################################################################################################
    def OnDeInit(self):
        return

    #############################################################################################################################
    #                                                                                                                           #
    #  CALLED BY FL WHENEVER IT IS NOT BUSY                                                                                     #
    #                                                                                                                           #
    #############################################################################################################################
    def OnIdle(self):
        # ----------------
        # REFRESH METERS
        # ---------------
        if device.isAssigned():
            for m in range(0, self.TrackCount):
                self.ColT[m].Tag = utils.Limited(
                    self.ColT[m].Peak, 0, self.MeterMax)
                self.ColT[m].Peak = 0
                if self.ColT[m].Tag == 0:
                    if self.ColT[m].ZPeak:
                        continue
                    else:
                        self.ColT[m].ZPeak = True
                else:
                    self.ColT[m].ZPeak = False

        # -------------------------------
        # MANAGE ANY TEMPORARY MESSAGES
        # -------------------------------
        if (self.TempMsgCount > 0) & (self.SliderHoldCount <= 0) & (not ui.isInPopupMenu()):
            self.TempMsgCount -= 1
            if self.TempMsgCount == 0:
                self.UpdateTempMsg()
        
        device.midiOutMsg(0x0000A0)

    #############################################################################################################################
    #                                                                                                                           #
    #   Called on mixer track(s) change, 'index' indicates track index of track that changed or -1 when all tracks changed.     #
    #                                                                                                                           #
    #############################################################################################################################
    def OnDirtyMixerTrack(self, SetTrackNum):
        for m in range(0, self.TrackCount):
            if (self.ColT[m].TrackNum == SetTrackNum) | (SetTrackNum == -1):
                self.ColT[m].Dirty = True

    #############################################################################################################################
    #                                                                                                                           #
    #  Called when something changed that the script might want to respond to.                                                  #
    #                                                                                                                           #
    #############################################################################################################################
    def OnRefresh(self, flags):
        if flags & midi.HW_Dirty_Mixer_Sel:
            self.UpdateLEDs()

        if flags & midi.HW_Dirty_Mixer_Display:
            self.UpdateTextDisplay()
            self.UpdateColT()
            self.UpdateLEDs()

        if flags & midi.HW_Dirty_Mixer_Controls:
            self.UpdateLEDs()
            self.UpdateValueBars()
            for n in range(0, self.TrackCount):
                if self.ColT[n].Dirty:
                    self.UpdateCol(n)

        # AP: listens to updates from plugins, updates the controller state if necessary.
        if flags & midi.HW_Dirty_ControlValues:
            self.UpdateColT()

        if flags & midi.HW_Dirty_RemoteLinks:
            self.UpdateColT()
            self.UpdateTextDisplay()

        # LEDs
        if flags & midi.HW_Dirty_LEDs:
            self.UpdateLEDs()

        if flags & midi.HW_Dirty_Colors:
            self.UpdateLEDs()
        
        if flags & midi.HW_Dirty_FocusedWindow:
            self.UpdateLEDs()

        if flags & midi.HW_Dirty_Performance:
            self.UpdateLEDs()

    #############################################################################################################################
    #                                                                                                                           #
    #  Called when the beat indicator has changes.                                                                              #
    #                                                                                                                           #
    #############################################################################################################################
    def OnUpdateBeatIndicator(self, Value):
        SyncLEDMsg = [midi.MIDI_NOTEON + (B_Play << 8), midi.MIDI_NOTEON + (
            B_Play << 8) + (0x7F << 16), midi.MIDI_NOTEON + (B_Play << 8) + (0x7F << 16)]

        if device.isAssigned():
            device.midiOutNewMsg(SyncLEDMsg[Value], 128)

# -------------------------------------------------------------------------------------------------------------------------------
# PROCEDURES
# -------------------------------------------------------------------------------------------------------------------------------

    #############################################################################################################################
    #                                                                                                                           #
    #   SEND A MESSAGE TO A DISPLAY                                                                                             #
    #                                                                                                                           #
    #############################################################################################################################

    def SendMsg(self, Msg, Channel=0, Row=0):
        sysex = bytes((HEADER_8 if self.isFP8 else HEADER_16) + Sysex_Text + bytearray([Channel, Row, 0x0]) + bytearray(Msg, 'utf-8') + FOOTER)
        device.midiOutSysex(sysex)

    #############################################################################################################################
    #                                                                                                                           #
    #   SEND A SECONDARY MESSAGE                                                                                                #
    #                                                                                                                           #
    #############################################################################################################################
    def SendMsgToFL(self, Msg):
        if len(Msg)>2:
            ui.setHintMsg((Msg+' '*56)[0:56])
    
    #############################################################################################################################
    #                                                                                                                           #
    #  HANDLES PRINCIPAL LOGIC FOR DISPLAYING TRACK DATA ON DISPLAYS / SCRIBBLE STRIPS                                          #
    #                                                                                                                           #
    #############################################################################################################################
    def UpdateTextDisplay(self):
        for index in range(0, self.TrackCount):
            line1 = ''
            line2 = ''
            line3 = ''
            if self.Page == Page_FX and self.CurPluginID == -1:
                pluginIndex = index + (self.TrackCount if self.isExtension else 0)
                if pluginIndex < 10:
                    tag = "FX"
                    if plugins.isValid(self.PluginTrack, pluginIndex):
                        t = (plugins.getPluginName(self.PluginTrack, pluginIndex)).split()
                        [line1, line2] = self.formatDisplayText(t)
                    else:
                        line1 = ""  # invalid
                        line2 = "-"
                    line3 = tag + str(pluginIndex + 1).zfill(2)
            elif self.Page == Page_FX and self.CurPluginID > -1:  # plugin params
                paramIndex = index + self.PluginParamOffset
                try: paramCount = plugins.getParamCount(self.PluginTrack, self.CurPluginID)
                except: paramCount = 0
                if paramIndex < paramCount:
                    tag = "PR"
                    t = self.ColT[index].TrackName.split()
                    [line1, line2] = self.formatDisplayText(t)
                    if paramIndex > 99:
                        line3 = tag[0] + str(paramIndex).zfill(2)
                    else:
                        line3 = tag + str(paramIndex).zfill(2)
            elif self.Page in [Page_Pan, Page_Stereo, Page_Volume, Page_Sends]:
                tag = "CH"
                t = mixer.getTrackName(self.ColT[index].TrackNum, 12).split()
                [line1, line2] = self.formatDisplayText(t)
                if self.Page == Page_Sends:
                    if self.ColT[index].TrackNum == mixer.trackNumber():
                        line3 = 'FROM'
                    if mixer.getRouteSendActive(mixer.trackNumber(), self.ColT[index].TrackNum):
                        line3 = 'TO'
                else:
                    if self.ColT[index].TrackNum > 99:
                        line3 = tag[0] + str(self.ColT[index].TrackNum).zfill(2)
                    else:
                        line3 = tag + str(self.ColT[index].TrackNum).zfill(2)

            elif self.Page == Page_EQ:
                if index < 7:
                    line1 = ("Low","Med","High","Low","Med","High","Reset")[index]
                    line2 = ("Freq","Freq","Freq","Width","Width","Width","All")[index]
            elif self.Page == Page_Links:
                link = self.checkFaderLink(index)
                if link[1] >= 0:
                    [line1, line2] = self.formatDisplayText(link[0].split())
                    line3 = 'LINK'
                else:
                    line1 = '--'
                    line2 = 'No Link'
                    line3 = '--'

            self.SendMsg(line1, index, 0)
            self.SendMsg(line2, index, 1)
            self.SendMsg(line3, index, 2)

    def formatDisplayText(self, string):
        if len(string) > 0:
            line1 = string[0][0:6]
            line2 = ''
            if len(string) == 3:
                # otherwise we can miss important aspects of the name
                string[1] = string[1] + string[2]
            if len(string) >= 2:
                line2 = string[1][0:6].title()
            elif (len(string) == 1 and len(string[0]) > 6):
                line2 = string[0][6:]
                # This just looks ugly so instead:
                if len(line2) == 1:
                    line1 = string[0][0:5]
                    line2 = string[0][5:]
            return [line1, line2]
        return ['', '']

    #############################################################################################################################
    #                                                                                                                           #
    #   UPDATE VALUE BARS                                                                                                       #
    #                                                                                                                           #
    #############################################################################################################################

    def UpdateValueBars(self):
        for index in range(self.FirstTrack, self.FirstTrack + self.TrackCount):
            self.UpdateValueBar(index)
    
    def UpdateValueBar(self, index):
        stripId = index % 8
        sectionId = int(index / 8)
        valueMessage = (0x30 if sectionId == 0 else 0x40) + stripId
        modeMessage = valueMessage + 8
        value = 0x0
        mode = 0x4

        if self.Page == Page_Volume:
            mode = 0x1
            value = int((mixer.getTrackPan(self.ColT[index].TrackNum) + 1) * 64) - 1
        elif self.Page == Page_Pan:
            mode = 0x2
            value = int(mixer.getTrackVolume(self.ColT[index].TrackNum) * 128) - 1
        elif self.Page == Page_Sends:
            if mixer.getRouteSendActive(self.ColT[index].TrackNum, mixer.trackNumber()):
                mode = 0x2
                eventId = mixer.getTrackPluginId(self.ColT[index].TrackNum, 0) + midi.REC_Mixer_Send_First + mixer.trackNumber()
                value = int(mixer.getEventValue(eventId) / midi.MaxInt * 2 * 128) - 1

        device.midiOutMsg(value << 16 | valueMessage << 8 | 0xB0)
        device.midiOutMsg(mode << 16 | modeMessage << 8 | 0xB0)

    #############################################################################################################################
    #                                                                                                                           #
    #   HANDLE MIDI EVENTS                                                                                                      #
    #                                                                                                                           #
    #############################################################################################################################

    def OnMidiMsg(self, event):
        for listener in self.midiListeners:
            eventInfo = listener[0]
            callback = listener[1]
            setEventHandled = listener[2]
            if (event.midiId == eventInfo.midiId) and (not isinstance(eventInfo.data1, int) or event.data1 == eventInfo.data1):
                shouldRun = callable(callback) \
                    and (not eventInfo.pmeFlags or event.pmeFlags & eventInfo.pmeFlags != 0) \
                    and (not eventInfo.data2NonZero or event.data2 > 0)
                if shouldRun:
                    callback(event)
                    if setEventHandled:
                        event.handled = True
                elif eventInfo.data2NonZero and setEventHandled:
                    event.handled = True

    def handleResponsiveButtonLED(self, event):
        device.midiOutMsg((event.data1 << 8) + midi.TranzPort_OffOnT[event.data2 > 0])

    def automateEvent(self, eventId, value, smoothSpeed):
        mixer.automateEvent(eventId, value, midi.REC_MIDIController, smoothSpeed)
        eventName = mixer.getEventIDName(eventId)
        stringValue = mixer.getEventIDValueString(eventId, mixer.getAutoSmoothEventValue(eventId)) \
            or round(mixer.getEventValue(eventId, mixer.getAutoSmoothEventValue(eventId)) / midi.MaxInt * 2,)
        self.SendMsgToFL(f"{eventName}: {stringValue}")

