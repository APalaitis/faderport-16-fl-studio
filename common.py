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

MackieCU_KnobOffOnT = [(midi.MIDI_CONTROLCHANGE + (1 << 6)) << 16,
                       midi.MIDI_CONTROLCHANGE + ((0xB + (2 << 4) + (1 << 6)) << 16)]

# -----------------
# STATIC VARIABLES
# -----------------
# Mackie CU pages
MackieCUPage_Volume = 0
MackieCUPage_Sends = 1
MackieCUPage_Pan = 2
MackieCUPage_FX = 3
MackieCUPage_EQ = 4 # Not yet assigned to any button
MackieCUPage_Stereo = 5 # Not yet assigned to any button
MasterPeak = 0

ExtenderLeft = 0
ExtenderRight = 1

# SYSEX
HEADER = bytearray([0xF0, 0x00, 0x01, 0x06, 0x16])
FOOTER = bytearray([0xF7])

# Operations
OP_Text = bytearray([0x12])
OP_TextMode = bytearray([0x13])

# Button Groups
SoloButtons = [0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57]
MuteButtons = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F]
SelectButtons = [0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x7, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27]
PageSelectors = [0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D]
FunctionButtons = [0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]
ArrowButtons = [0x60, 0x61, 0x62, 0x63]
FaderHold = [0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0x6F]
JogSourceButtons = [0x54, 0x65]

# Buttons
B_VCA_FX = 0x41
B_BusOutputs = 0x40
B_AudioInputs = 0x3E
B_VI_MIDI = 0x3F
B_AllUser = 0x42

B_BankLeft = 0x3C
B_BankRight = 0xFF
B_TrackLeft = 0x2E
B_TrackRight = 0x2F

B_Flip = 0x32
B_User1 = 0x53
B_User2 = 0x52

B_Stop = 0x5D
B_Play = 0x5E
B_Record = 0x5F
B_Loop = 0x56

B_Metronome = 0x3B
B_LShift = 0x46
B_Clear = 0x01
B_Save = 0x43
B_Link = 0x05

# Faders 
Faders = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]


OffOnStr = ('off', 'on')

BankingColours = [-22508, -15461356, -14397697, -60167, -98028, -
                  1768, -8126692, -14617601, -2479873, -54171, -52992, -98028]
TrackColours = [-4930828, -16777216, -14737633, -12632257, -10526881, -8421505, -6316129, -4210753,
                -12037802, -251649, -244993, -238081, -165633, -158721, -151809, -79361, -
                72449, -16382223, -14605838, -12763660, -
                10921483, -9079305, -7302919, -5460742,
                -3618564, -34560, -30692, -26567, -22442, -18317, -14193, -10068, -5943, -
                2555897, -2286810, -1952187, -1617564, -1282941, -1013854, -679231,
                -344608, -16763645, -15118819, -13408457, -11763631, -10053013, -8408187, -6697825, -
                5052999, -13608273, -12425032, -11175998, -
                9926964, -8677930, -7428896, -6179862,
                -2105377, -13762559, -12052197, -10341834, -
                8631472, -6920853, -5210490, -3500128,
                -1789765, -1119232, -1053161, -987090, -921019, -854692, -788621, -722550, -
                656479, -22508, -15461356, -14397697, -60167, -98028, -1768, -8126692,
                -14617601, -2479873, -54171, -52992, -98028, -12037802, -251649, -244993, -
                238081, -165633, -158721, -151809, -79361, -72449, -16382223, -14605838,
                -12763660, -10921483, -9079305, -7302919, -5460742, -3618564, -34560, -
                30692, -26567, -22442, -18317, -14193, -10068, -5943, -2555897, -2286810,
                -1952187, -1617564, -1282941, -1013854, -679231, -
                344608, -16763645, -15118819, -13408457,
                -11763631, -10053013, -8408187, -6697825, -5052999, -13608273, -12425032, -11175998, -
                9926964, -8677930, -7428896, -6179862, -4930828, -
                16777216, -14737633, -12632257, -10526881,
                -8421505, -6316129, -4210753, -2105377, -13762559, -12052197, -10341834, -8631472, -6920853, -
                5210490, -3500128, -1789765, -1119232, -1053161, -
                987090, -921019, -854692, -788621, -722550,
                -656479, -22508, -15461356, -14397697, -60167, -98028, -1768, -8126692, -14617601, -2479873, -54171, -52992, -98028]

AlwaysShowSelectedTrack=False #=Track Related:=Always show me the selected track instead of the current assignment (which is probably lit up anyway!)
ShowTrackNos=True #=Track Related:=Show Track Numbers in row 2 (or longer track names if off)
SelectTrackWithBanking=False #=Track Related:=Always select the relevant track in the bank to synchronise with mixer display in FL
RouteTempTextToClassic=False #=Display Related:=Route any temporary messages to Scribble Strips / Main Display
RouteTempTextToFLDisplay=True #=Display Related:=Duplicate temporary messages to the FL Studio Hint Panel and Bar
BankNoInTimeWindow=False #=Display Related:=Always show me the current bank number in the last section of the time display
DefaultFreeDisplayToZen=False #=Free Controls:=Defaults Free control descriptions to reflect Zenology parameters
DefaultFreeDisplayToGen=True #=Free Controls:=Defaults Free control descriptions to reflect common pararmeters
TouchFaderToSelect=False #=Fader Related:=Touch a fader to select the track (can makes adjusting multiple faders at once a litle messy)
DebuggingOn=False #=General:=Developers Only (will slow down performance)
EMAGIC=False #=General:=Use for EMAGIC MCU Display Compatibility
TargetMasterMeters=False #=Enhanced Hardware:=Adds functionality for control surfaces that have a set of stereo master meters
TargetSecondDisplays=False #=Enhanced Hardware:= Provides additional information for control surfaces that have twin displays in their mixer section
FaderPortSupport = False #=Device Specific:=Some additional Support for Presonus faderport 8 and 16
CompactDescriptors = False#=Device Specific:=Tidies up some display options
SplitAccrossScribbleStrips = True#=Device Specific:=Tidies up Text accross seperate Scribble Strips

#################################
# CLASS FOR COLUMN RELATED ITEMS
#################################

class TMackieCol:
    def __init__(self):
        self.TrackNum = 0
        self.BaseEventID = 0
        self.KnobEventID = 0
        self.KnobPressEventID = 0
        self.KnobResetEventID = 0
        self.KnobResetValue = 0
        self.KnobMode = 0
        self.KnobCenter = 0
        self.SliderEventID = 0
        self.Peak = 0
        self.Tag = 0
        self.SliderName = ""
        self.KnobName = ""
        self.LastValueIndex = 0
        self.ZPeak = False
        self.Dirty = False
        self.KnobHeld = False
        #self.PrevProc="unknown"

class TMackieCU_Base():
    def __init__(self, isExtension: bool):
        self.isExtension = isExtension
        self.TempMsgT = ["", ""]
        self.LastTimeMsg = bytearray(10)
        self.Shift = False
        self.TempMsgDirty = False
        self.JogSource = 0
        self.TempMsgCount = 0
        self.SliderHoldCount = 0
        self.FirstTrack = 8 if isExtension else 0
        self.FirstTrackT = [0, 0]
        self.TrackCount = 16
        self.ColT = [0 for x in range(self.TrackCount)]
        for x in range(0, self.TrackCount):
            self.ColT[x] = TMackieCol()
        self.Clicking = False
        self.Scrub = False
        self.Flip = False
        self.MeterMode = 1  # enabled!
        self.CurMeterMode = 0
        self.Page = MackieCUPage_Volume # AP: The device itself seems to default to this page.
        self.SmoothSpeed = 0
        self.MeterMax = 0
        self.ActivityMax = 0
        self.MackieCU_PageNameT = (
            'Panning                          (press VPOTS to reset)',
            'Stereo Separation               (press VPOTS to reset)',
            '" - press VPOTS to enable',
            '" - turn VPOTS to adjust',
            '" - press VPOTS to reset',
            '(Free Controls)'
        )
        self.ArrowsStr = chr(0x7F) + chr(0x7E) + chr(0x32)
        self.AlphaTrack_SliderMax = round(13072 * 16000 / 12800)
        self.CurPluginID = -1
        self.LCD1 = bytearray([0xF0, 0x00, 0x00, 0x66, 0x15 if isExtension else 0x14, 0x12, 0])  #Base Mackie Address
        self.LCD2 = bytearray([0xF0, 0x00, 0x00, 0x67, 0x15, 0x13, 0])  #Base QCON Screen 2 Address
        #                     [0xF0, 0x00, 0x00, 0x67, 0x15, 0x13
        self.MasterPeak = 0
        self.Msg2 = ''
        self.ShowTrackNumbers = ShowTrackNos
        self.MixerScroll = SelectTrackWithBanking
        self.PrevProc="-"
        if (not isExtension):
            self.ExtenderPos = ExtenderLeft
        self.PluginTrack = 0
        self.midiListeners = []
        self.soloMuteClear = False
        self.linkMode = False

# -------------------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
# -------------------------------------------------------------------------------------------------------------------------------

    #############################################################################################################################
    #                                                                                                                           #
    # Display shortened name to fit to 7 characters (e.g., Fruity Chorus = FChorus, EQ Enhancer = EQEnhan)                      #
    #                                                                                                                           #
    #############################################################################################################################

    def DisplayName(self,name):
        if name == '':
            return ''

        words = name.split()
        if len(words) == 0:
            return ''

        shortName = ''

        for w in words:
            first = True
            for c in w:
                if c.isupper():
                    shortName += c
                elif first:
                    shortName += c
                else:
                    break
                first = False

        lastWord = words[len(words)-1]
        shortName += lastWord[1:]
        return shortName[0:6]

    #############################################################################################################################
    #                                                                                                                           #
    # Tidy Up Text over 8 char seperated scribble strips                                                                        #
    #                                                                                                                           #
    #############################################################################################################################

    #############################################################################################################################
    #                                                                                                                           #
    # Tidy Up Text over 7 chars for seperated scribble s                                                                        #
    # ToDo: Allow for multiple words per scribble strip?                                                                        #
    #############################################################################################################################

    def TidyScribbles(self,name):
        self.PrevProc='DisplayName()'
        if name == '':
            return ''
        words = name.split()
        if len(words) == 0:
            return ''
        #tidyName = ''
        #for w in words:
        #   if not w.__contains__('-'):
        #        tidyName+=((w+' '*6)[0:7])
        s = "";
        s1=""
        n = 0;
        n1 = 1;
        words = name.split()
        while (n < len(words)):        
            if (n + 1 >= len(words)):
                n1 = 0;
            s1 = words[n] + " " + words[n + n1];
            if (len(s1)<8):
                s =s+ (s1+" "*7)[0:7];
                n = n + 2;
            else:
                s = s+ (words[n]+" "*7)[0:7];
                n=n+1
        return s
    
    #############################################################################################################################
    #                                                                                                                           #
    #  CALLED FROM UPDATECOL TO RETURN SLIDER / LEVEL VALUEDS                                                                   #
    #                                                                                                                           #
    #############################################################################################################################
    def AlphaTrack_LevelToSlider(self, Value, Max=midi.FromMIDI_Max):
        return round(Value / Max * self.AlphaTrack_SliderMax)

    #############################################################################################################################
    #                                                                                                                           #
    #  CALLED FROM UPDATECOL TO RETURN SLIDER / LEVEL VALUEDS                                                                   #
    #                                                                                                                           #
    #############################################################################################################################
    def AlphaTrack_SliderToLevel(self, Value, Max=midi.FromMIDI_Max):
        return min(round(Value / self.AlphaTrack_SliderMax * Max), Max)
    
    #############################################################################################################################
    #                                                                                                                           #
    #  Called when the script has been started.                                                                                 #
    #                                                                                                                           #
    #############################################################################################################################
    def OnInit(self):
        self.FirstTrack = 0
        self.FirstTrackT[0] = self.FirstTrack
        self.SmoothSpeed = 469
        self.Clicking = True

        # device.setHasMeters()
        self.LastTimeMsg = bytearray(10)
        # self.SetBackLight(2)  # backlight timeout to 2 minutes
        # self.UpdateClicking()
        # self.UpdateMeterMode()
        # self.SetPage(self.Page)
        # ui.setHintMsg(device.getName())    
        # self.RegisteDefaultMidiListeners()

    #############################################################################################################################
    #                                                                                                                           #
    #      Called before the script will be stopped.                                                                               #
    #                                                                                                                           #
    #############################################################################################################################
    def OnDeInit(self):
        if device.isAssigned():
            for m in range(0, self.TrackCount):
                device.midiOutSysex(
                    bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x20, m, 0, 0xF7]))
                device.midiOutSysex(bytes(bytearray([0xd1, 0, 0xF7])))
                device.midiOutSysex(bytes(bytearray([0xd1, 16, 0xF7])))

            if ui.isClosing():
                self.SendMsg2(ui.getProgTitle() + ' session closed at ' +
                              time.ctime(time.time())+chr(32)*60, 0)
            else:
                self.SendMsg('', 1)

            self.SendAssignmentMsg('   ')


    #############################################################################################################################
    #                                                                                                                           #
    #  CALLED BY FL WHENEVER IT IS NOT BUSY \\:-)                                                                               #
    #                                                                                                                           #
    #############################################################################################################################
    def OnIdle(self):
        # ----------------
        # REFRESH METERS
        # ---------------
        if device.isAssigned():
            for m in range(0,  len(self.ColT)):
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
                device.midiOutMsg(midi.MIDI_CHANAFTERTOUCH + (self.ColT[m].Tag << 8) + (m << 12))

        # -------------------------
        # UPDATE THE TIME DISPLAY
        # -------------------------
        n=device.dispatchReceiverCount()+1
        if ui.getTimeDispMin():
            # HHH.MM.SS.CC_
            if playlist.getVisTimeBar() == -midi.MaxInt:
                s = '-   0'
            else:
                h, m = utils.DivModU(n, 60)
                if BankNoInTimeWindow: #loose ticks for readability
                    bank = str(math.ceil(int(self.ColT[m].TrackNum)/n)).zfill(3)
                    s = utils.Zeros_Strict((h * 100 + m) * utils.SignOf(playlist.getVisTimeBar()), 5, ' ')
                    s = s + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2)  + bank             
                else:    
                    s = utils.Zeros_Strict((h * 100 + m) * utils.SignOf(playlist.getVisTimeBar()), 5, ' ')
                    s = s + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2) + utils.Zeros_Strict(playlist.getVisTimeTick(), 2) + ' '               
        else:
            # BBB.BB.__.TTT
            if BankNoInTimeWindow:
                bank = str(math.ceil(int(self.ColT[m].TrackNum)/n)).zfill(3)
                s = utils.Zeros_Strict(playlist.getVisTimeBar(), 3, ' ') + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2) + '  ' + bank 
            else:
                s = utils.Zeros_Strict(playlist.getVisTimeBar(), 3, ' ') + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2) + '  ' + utils.Zeros_Strict(playlist.getVisTimeTick(), 3)
        if (not self.isExtension):
            self.SendTimeMsg(s)
        # -------------------------------
        # MANAGE ANY TEMPORARY MESSAGES
        # -------------------------------
        if self.TempMsgDirty:
            self.UpdateTempMsg()
            self.TempMsgDirty = False

        if (self.TempMsgCount > 0) & (self.SliderHoldCount <= 0) & (not ui.isInPopupMenu()):
            self.TempMsgCount -= 1
            if self.TempMsgCount == 0:
                self.UpdateTempMsg()

    #############################################################################################################################
    #                                                                                                                           #
    #  HANDLES KNOB FUNCTIONS                                                                                                   #
    #                                                                                                                           #
    #############################################################################################################################

    def SetKnobValue(self, Num, Value, Res=midi.EKRes):
        CurPluginID = Num
        Num %= self.TrackCount
        if (self.ColT[Num].KnobEventID >= 0) & (self.ColT[Num].KnobMode < 4):
            if Value == midi.MaxInt:
                if self.Page == MackieCUPage_FX:
                    if plugins.isValid(mixer.trackNumber(), CurPluginID):
                        if self.ColT[Num].KnobPressEventID >= 0:
                            # Value = channels.incEventValue(self.ColT[Num].KnobPressEventID, 0, midi.EKRes)
                            # channels.processRECEvent(self.ColT[Num].KnobPressEventID, Value, midi.REC_Controller)
                            s = mixer.getEventIDName(self.ColT[Num].KnobPressEventID)
                            self.SendMsg2("CH"+str(mixer.trackNumber()).zfill(2)+" - "+mixer.getTrackName(mixer.trackNumber())+" ("+self.ColT[Num].TrackName+")".ljust(56, ' '))
                        self.CurPluginID = CurPluginID
                        self.PluginParamOffset = 0
                        mixer.focusEditor(mixer.trackNumber(), CurPluginID)
                        self.UpdateColT()
                        self.UpdateCommonLEDs()
                        self.UpdateTextDisplay()
                        return
                else:
                    mixer.automateEvent(
                        self.ColT[Num].KnobResetEventID, self.ColT[Num].KnobResetValue, midi.REC_MIDIController, self.SmoothSpeed)
            else:
                mixer.automateEvent(
                    self.ColT[Num].KnobEventID, Value, midi.REC_Controller, self.SmoothSpeed, 1, Res)
            # hint
            n = mixer.getAutoSmoothEventValue(self.ColT[Num].KnobEventID)
            s = mixer.getEventIDValueString(self.ColT[Num].KnobEventID, n)
            if s != '':
                s = ': ' + s
            #self.SendMsg2((self.ColT[Num].KnobName + s).ljust(56, ' '))
            self.SendMsg2(self.ColT[Num].KnobName + s)
        #mixer.automateEvent(self.ColT[Num].KnobEventID, Value, midi.REC_Controller, self.SmoothSpeed, 1, Res)

    #############################################################################################################################
    #                                                                                                                           #
    #      Called on mixer track(s) change, 'index' indicates track index of track that changed or -1 when all tracks changed.     #
    #                                                                                                                           #
    #############################################################################################################################
    def OnDirtyMixerTrack(self, SetTrackNum):
        for m in range(0, len(self.ColT)):
            if (self.ColT[m].TrackNum == SetTrackNum) | (SetTrackNum == -1):
                self.ColT[m].Dirty = True

    #############################################################################################################################
    #                                                                                                                           #
    #  Called when something changed that the script might want to respond to.                                                  #
    #                                                                                                                           #
    #############################################################################################################################
    def OnRefresh(self, flags):
        if flags & midi.HW_Dirty_Mixer_Sel:
            self.UpdateMixer_Sel()

        if flags & midi.HW_Dirty_Mixer_Display:
            self.UpdateTextDisplay()
            self.UpdateColT()

        if flags & midi.HW_Dirty_Mixer_Controls:
            for n in range(0, len(self.ColT)):
                if self.ColT[n].Dirty:
                    self.UpdateCol(n)

        # AP: listens to updates from plugins, updates the controller state if necessary.
        if flags & midi.HW_Dirty_ControlValues:
            self.UpdateColT()

        if flags & midi.HW_Dirty_RemoteLinks:
            self.UpdateColT()

        # LEDs
        if flags & midi.HW_Dirty_LEDs:
            self.UpdateCommonLEDs()

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

    #############################################################################################################################
    #                                                                                                                           #
    #  Called when peak meters needs to be updated                                                                              #
    #                                                                                                                           #
    #############################################################################################################################
    def OnUpdateMeters(self):
        if self.CurMeterMode >= 1:
            # for m in range(0, len(self.ColT) - 1):
            #    self.ColT[m].Peak = max(self.ColT[m].Peak, round(mixer.getTrackPeaks(self.ColT[m].TrackNum, midi.PEAK_LR_INV) * self.MeterMax))
            for m in range(0, len(self.ColT)):
                self.ColT[m].Peak = max(0, round(mixer.getTrackPeaks(self.ColT[m].TrackNum, 0) * self.MeterMax))
            n = max(0, round(mixer.getTrackPeaks(MasterPeak, 0) * self.MeterMax))
            device.midiOutSysex(bytes(bytearray([0xd1, n, 0xF7])))
            n = max(0, round(mixer.getTrackPeaks(MasterPeak, 1) * self.MeterMax))
            device.midiOutSysex(bytes(bytearray([0xd1, n+16, 0xF7])))

    #############################################################################################################################
    #                                                                                                                           #
    #  UPDATE BUTTON LEDS                                                                                                       #
    #                                                                                                                           #
    #############################################################################################################################

    def UpdateCommonLEDs(self):
        if device.isAssigned():
            # stop
            device.midiOutNewMsg(
                (B_Stop << 8) + midi.TranzPort_OffOnT[transport.isPlaying() == midi.PM_Stopped], 0)
            # loop
            LoopMode = transport.getLoopMode()
            device.midiOutNewMsg((B_Loop << 8) +
                                 midi.TranzPort_OffOnT[LoopMode == midi.SM_Pat], 1)
            # record
            r = transport.isRecording()
            device.midiOutNewMsg(
                (B_Record << 8) + midi.TranzPort_OffOnT[r], 2)
            # self.Page
            for m in range(0,  6):
                device.midiOutNewMsg(
                    ((PageSelectors[0] + m) << 8) + midi.TranzPort_OffOnT[m == self.Page], 5 + m)
            # changed flag
            device.midiOutNewMsg(
                (B_Save << 8) + midi.TranzPort_OffOnT[general.getChangedFlag() > 0], 11)
            # metronome
            device.midiOutNewMsg(
                (B_Metronome << 8) + midi.TranzPort_OffOnT[general.getUseMetronome()], 12)
            # focused windows
            BusLed = ui.getFocused(midi.widMixer) & (
                self.ColT[0].TrackNum >= 100)
            OutputLed = ui.getFocused(midi.widMixer) & (
                self.ColT[0].TrackNum >= 0) & (self.ColT[0].TrackNum <= 1)
            InputLed = ui.getFocused(midi.widMixer) & (
                not OutputLed) & (not BusLed)
            device.midiOutNewMsg((B_AudioInputs << 8) +
                                 midi.TranzPort_OffOnT[InputLed], 22)
            device.midiOutNewMsg((B_VI_MIDI << 8) +
                                 midi.TranzPort_OffOnT[ui.getFocused(midi.widChannelRack)], 23)
            device.midiOutNewMsg((B_BusOutputs << 8) +
                                 midi.TranzPort_OffOnT[BusLed], 24)
            device.midiOutNewMsg(
                (B_BusOutputs << 8) + midi.TranzPort_OffOnT[OutputLed], 25)

# -------------------------------------------------------------------------------------------------------------------------------
# PROCEDURES
# -------------------------------------------------------------------------------------------------------------------------------
    #############################################################################################################################
    #                                                                                                                           #
    #   SEND A MESSAGE TO A DISPLAY                                                                                             #
    #                                                                                                                           #
    #############################################################################################################################

    def SendMsg(self, Msg, Channel=0, Row=0, Display=0):
        sysex = HEADER + OP_Text + bytearray([Channel, Row, 0x0]) + bytearray(Msg, 'utf-8') + FOOTER
        device.midiOutSysex(bytes(sysex))        

    #############################################################################################################################
    #                                                                                                                           #
    #   SEND A SECONDARY MESSAGE                                                                                                #
    #                                                                                                                           #
    #############################################################################################################################
    def SendMsg2(self, Msg, Duration=500):
        #Msg=Msg.rstrip()
        if len(Msg)>2:
            if (RouteTempTextToFLDisplay):                
                ui.setHintMsg((Msg+' '*56)[0:56])
                
         
    def OnSendTempMsg(self, Msg, Duration = 500):
        if RouteTempTextToClassic: 
            self.TempMsgCount = (Duration // 48) + 1
            self.TempMsgT[1] = Msg.ljust(56, ' ')
            self.TempMsgDirty = True
            
    def UpdateTempMsg(self):
        return
    
    #############################################################################################################################
    #                                                                                                                           #
    #  Called for short MIDI out messages sent from MIDI Out plugin.                                                            #
    #                                                                                                                           #
    #############################################################################################################################
    def SendAssignmentMsg(self, Msg):
        s_ansi = Msg + chr(0) #AnsiString(Msg);
        if device.isAssigned():
            for m in range(1, 3):
                device.midiOutMsg(midi.MIDI_CONTROLCHANGE + ((0x4C - m) << 8) + (ord(s_ansi[m]) << 16))            

    #############################################################################################################################
    #                                                                                                                           #
    #  HANDLES PRINCIPAL LOGIC FOR DISPLAYING TRACK DATA ON DISPLAYS / SCRIBBLE STRIPS                                          #
    #                                                                                                                           #
    #############################################################################################################################
    def UpdateTextDisplay(self):
        s1 = ''
        s2 = ''
        s3 = ''
        ch = "CH"
        master = 'MASTER '
        EffectsExist = False
        if self.Page == MackieCUPage_FX:
            ch = "FX"
        elif self.Page == MackieCUPage_EQ:
            ch = "EQ"
        for index in range(0, len(self.ColT)):
            s = ''
            sa = ''
            sa2 = ''
            if self.Page == MackieCUPage_FX and self.CurPluginID == -1:
                pluginIndex = index + (8 if self.isExtension else 0)
                if pluginIndex < 10:
                    ch = "FX"
                    master = "FX08   "
                    if plugins.isValid(mixer.trackNumber(), pluginIndex):
                        EffectsExist = True
                        #s = DisplayName(plugins.getPluginName(self.ColT[m].TrackNum,m))
                        t = (plugins.getPluginName(mixer.trackNumber(), pluginIndex)).split()
                        s = t[0][0:6]
                        if len(t) == 3:
                            # otherwise we can miss important aspects of the plugin like version number
                            t[1] = t[1]+t[2]
                        if len(t) >= 2:
                            sa = t[1][0:6].title()
                        elif (len(t) == 1 and len(t[0]) > 6):
                            sa = t[0][6:]
                            if len(sa) == 1:  # This just looks ugly so instead:
                                s = t[0][0:5]
                                sa = t[0][5:]
                        else:
                            sa = "       "
                    else:
                        s = "   \\   "  # invalid
                        sa = "   \\   "
                    if self.ColT[index].TrackNum > 99:
                        sa2 = ch[1]+str(self.ColT[index].TrackNum).zfill(2)+'   '
                    else:
                        sa2 = 'ch'+str(self.ColT[index].TrackNum).zfill(2)+'   '
            elif self.Page == MackieCUPage_FX and self.CurPluginID > -1:  # plugin params
                t = self.ColT[index].TrackName.split()
                if len(t) > 0:
                    s = t[0][0:6]
                    if len(t) == 3:
                        # otherwise we can miss important aspects of the param
                        t[1] = t[1]+t[2]
                    if len(t) >= 2:
                        sa = t[1][0:6].title()
                    elif (len(t) == 1 and len(t[0]) > 6):
                        sa = t[0][6:]
                        if len(sa) == 1:  # This just looks ugly so instead:
                            s = t[0][0:5]
                            sa = t[0][5:]
                    else:
                        sa = "       "
                else:
                    s = "      "
                    sa = "      "
            elif ((self.Page == MackieCUPage_Sends) or (self.Page == MackieCUPage_Pan) or (self.Page == MackieCUPage_Stereo) or (self.Page == MackieCUPage_Volume)):
                if self.ShowTrackNumbers:
                    s = mixer.getTrackName(self.ColT[index].TrackNum, 6)
                    sa = '   '+str(self.ColT[index].TrackNum)+' '
                    if (self.Page == MackieCUPage_Sends):
                        if mixer.getRouteSendActive(mixer.trackNumber(), self.ColT[index].TrackNum):
                            sa = ' ->'+str(self.ColT[index].TrackNum)+'<-'
                        elif self.ColT[index].TrackNum == mixer.trackNumber():
                            sa = ' <-'+str(self.ColT[index].TrackNum)+'->'
                else:
                    t = mixer.getTrackName(self.ColT[index].TrackNum, 12).split()
                    if len(t) > 0:
                        s = t[0][0:6]
                        if len(t) == 3:
                            # otherwise we can miss important aspects of the name
                            t[1] = t[1]+t[2]
                        if len(t) >= 2:
                            sa = t[1][0:6].title()
                        elif (len(t) == 1 and len(t[0]) > 6):
                            sa = t[0][6:]
                            # This just looks ugly so instead:
                            if len(sa) == 1:
                                s = t[0][0:5]
                                sa = t[0][5:]
                        else:
                            sa = "       "
                    else:
                        s = "      "
                        sa = "      "
            # Now do everything outside that loop:
            if ((self.Page == MackieCUPage_Sends) or (self.Page == MackieCUPage_Pan) or (self.Page == MackieCUPage_Stereo) or (self.Page == MackieCUPage_FX) or (self.Page == MackieCUPage_Volume)):
                if self.ColT[index].TrackNum > 99:
                    sa2 = ch[1]+str(self.ColT[index].TrackNum).zfill(2)+'   '
                else:
                    sa2 = ch+str(self.ColT[index].TrackNum).zfill(2)+'   '
                for n in range(1, 7 - len(s) + 1):
                    s = s + ' '
                for n in range(1, 7 - len(sa) + 1):
                    sa = sa + ' '
                s1 = s1 + s
                s2 = s2 + sa
                s3 = s3 + sa2
            elif self.Page == MackieCUPage_EQ:
                s1 = "  Low    Med    High   Low    Med   High           Reset"
                s2 = "  Freq   Freq   Freq   Width  Width Width           All "                
            self.SendMsg(s, index, 0)
            self.SendMsg(sa, index, 1)
            self.SendMsg(sa2, index, 2)
        s3=" "*56+s3       
        n=device.dispatchReceiverCount()+1
        if (AlwaysShowSelectedTrack):
            self.SendAssignmentMsg(str(mixer.trackNumber()).zfill(3))
        #self.SendMsg2(s3[0:112] + 'BNK'+str(math.ceil(self.ColT[index].TrackNum/(8*n))).zfill(2))
        if RouteTempTextToClassic:
            self.TempMsgT[0] = s1[0:56]
            if self.TempMsgCount == 0:
                self.UpdateTempMsg()
            else:
                self.SendMsg(s1[0:56], 1)
        if TargetSecondDisplays:
            self.SendMsg2(s3[0:112] + 'BNK'+str(math.ceil(self.ColT[index].TrackNum/(8*n))).zfill(2))


    #############################################################################################################################
    #                                                                                                                           #
    #  HANDLES UPDATING OF CHANNEL STRIPS FOR ASSIGNMENT SENDS, FX AND FREE                                                     #
    #                                                                                                                           #
    #############################################################################################################################

    def UpdateMixer_Sel(self):
        if device.isAssigned():
            for m in range(0, len(self.ColT)):
                device.midiOutNewMsg(
                    ((SelectButtons[m]) << 8) +
                    midi.TranzPort_OffOnT[self.ColT[m].TrackNum == mixer.trackNumber()]
                , self.ColT[m].LastValueIndex + 4)

        if self.Page in [MackieCUPage_Pan, MackieCUPage_FX, MackieCUPage_Volume]:
            self.UpdateColT()

    #############################################################################################################################
    #                                                                                                                           #
    #  PRINCIPAL FUNCTION RESPONSIBLE FOR UPDATING COLUMNS                                                                       #
    #                                                                                                                           #
    #############################################################################################################################
    def UpdateCol(self, Num):
        data1 = 0
        data2 = 0
        center = 0

        if device.isAssigned():
            # AP: By default, values come from REC events
            sv = mixer.getEventValue(self.ColT[Num].SliderEventID)
            
            linkValue = self.checkFaderLink(Num)
            # AP: Plugin params don't have REC events associated with them, so we use functions to get the values
            if self.Page == MackieCUPage_FX:
                if (self.CurPluginID >= 0):
                    if (plugins.isValid(self.PluginTrack, self.CurPluginID)):
                        paramCount = plugins.getParamCount(self.PluginTrack, self.CurPluginID)
                        paramIndex = Num + (8 if self.isExtension else 0) + self.PluginParamOffset
                        if paramIndex < paramCount:
                            paramValue = plugins.getParamValue(paramIndex, self.PluginTrack, self.CurPluginID)
                            sv = int(midi.FromMIDI_Max * paramValue)
            # AP: If the control is linked, don't move the fader
            elif linkValue > -1 and self.Page in [MackieCUPage_Pan, MackieCUPage_Volume]:
                sv = int(midi.FromMIDI_Max * linkValue)

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

                device.midiOutNewMsg(
                    midi.MIDI_CONTROLCHANGE + ((B_TrackLeft + Num) << 8) + (data1 << 16), self.ColT[Num].LastValueIndex)

                # solo, mute
                # device.midiOutNewMsg(((ArmButtons[0] + Num) << 8) + midi.TranzPort_OffOnBlinkT[int(mixer.isTrackArmed(
                #     self.ColT[Num].TrackNum)) * (1 + int(transport.isRecording()))], self.ColT[Num].LastValueIndex + 1)
                if (self.Page == MackieCUPage_Sends):
                    isBeingSentTo = mixer.getRouteSendActive(mixer.trackNumber(), self.ColT[Num].TrackNum)
                    device.midiOutNewMsg((SelectButtons[Num] << 8) + midi.TranzPort_OffOnT[isBeingSentTo], self.ColT[Num].LastValueIndex + 2)
                elif (self.Page == MackieCUPage_FX):
                    if (self.CurPluginID == -1):
                        paramIndex = Num + (8 if self.isExtension else 0)
                        if paramIndex < 10:
                            pluginValid = plugins.isValid(mixer.trackNumber(), paramIndex)
                            device.midiOutNewMsg((SoloButtons[Num] << 8) + midi.TranzPort_OffOnT[pluginValid], self.ColT[Num].LastValueIndex + 2)
                            device.midiOutNewMsg((MuteButtons[Num] << 8) + midi.TranzPort_OffOnT[pluginValid], self.ColT[Num].LastValueIndex + 3)
                    else:
                        paramCount = plugins.getParamCount(mixer.trackNumber(), self.CurPluginID)
                        device.midiOutNewMsg((SoloButtons[Num] << 8) + midi.TranzPort_OffOnT[paramCount < Num], self.ColT[Num].LastValueIndex + 2)
                        device.midiOutNewMsg((MuteButtons[Num] << 8) + midi.TranzPort_OffOnT[paramCount < Num], self.ColT[Num].LastValueIndex + 3)

                else:
                    device.midiOutNewMsg((SoloButtons[Num] << 8) + midi.TranzPort_OffOnT[mixer.isTrackSolo(
                        self.ColT[Num].TrackNum)], self.ColT[Num].LastValueIndex + 2)
                    device.midiOutNewMsg((MuteButtons[Num] << 8) + midi.TranzPort_OffOnT[not mixer.isTrackEnabled(
                        self.ColT[Num].TrackNum)], self.ColT[Num].LastValueIndex + 3)

            # slider
            data1 = self.AlphaTrack_LevelToSlider(sv)
            data2 = data1 & 127
            data1 = data1 >> 7
            device.midiOutNewMsg(midi.MIDI_PITCHBEND + Num + (data2 << 8) +
                                    (data1 << 16), self.ColT[Num].LastValueIndex + 5)

            Dirty = False

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
            if CompactDescriptors:
                ch=""
            else:    
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

            if self.Page == MackieCUPage_Volume:
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_Vol
                self.ColT[m].SliderName = ch+mixer.getTrackName(self.ColT[m].TrackNum) + ' - Volume'
            if self.Page == MackieCUPage_Pan:
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_Pan
                #self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID
                self.ColT[m].SliderName = ch+mixer.getTrackName(self.ColT[m].TrackNum) + ' - ' + 'Pan'
            elif self.Page == MackieCUPage_Stereo:
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_SS
                #self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID
                self.ColT[m].SliderName = mixer.getTrackName(self.ColT[m].TrackNum) + ' - ' + 'Separation'
            elif self.Page == MackieCUPage_Sends:
                self.ColT[m].SliderEventID = CurID + midi.REC_Mixer_Send_First + self.ColT[m].TrackNum
                self.ColT[m].SliderName = mixer.getEventIDName(self.ColT[m].SliderEventID)
                #self.ColT[m].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                #self.ColT[m].KnobCenter = mixer.getRouteSendActive(mixer.trackNumber(), self.ColT[m].TrackNum)
                # if self.ColT[m].KnobCenter == 0:
                #     self.ColT[m].KnobMode = 4
                # else:
                #     self.ColT[m].KnobMode = 2
            elif self.Page == MackieCUPage_FX:
                if self.CurPluginID == -1:  # Plugin not selected
                    index = m + self.CurPluginOffset + (8 if self.isExtension else 0)
                    if index < 10:
                        self.PluginTrack = mixer.trackNumber()
                        self.ColT[m].CurID = mixer.getTrackPluginId(self.PluginTrack, index)
                        self.ColT[m].SliderEventID = self.ColT[m].CurID + midi.REC_Plug_MixLevel
                        self.ColT[m].SliderName = mixer.getEventIDName(self.ColT[m].SliderEventID)
                        #self.ColT[m].KnobResetValue = midi.FromMIDI_Max

                        IsValid = mixer.isTrackPluginValid(self.PluginTrack, index)
                        IsEnabledAuto = mixer.isTrackAutomationEnabled(self.PluginTrack, index)
                        if IsValid:
                            # self.ColT[m].KnobMode = 2
                            # self.ColT[m].KnobPressEventID = self.ColT[m].CurID + midi.REC_Plug_Mute
                            self.ColT[m].TrackName = plugins.getPluginName(self.PluginTrack, index)
                        # else:
                        #     self.ColT[m].KnobMode = 4
                        # self.ColT[m].KnobCenter = int(IsValid & IsEnabledAuto)
                else:  # Plugin selected
                    pluginIndex = self.CurPluginID + self.CurPluginOffset
                    self.ColT[m].CurID = mixer.getTrackPluginId(self.PluginTrack, pluginIndex)
                    if (plugins.isValid(self.PluginTrack, pluginIndex)):
                        paramIndex = m + self.PluginParamOffset + (8 if self.isExtension else 0)
                        if paramIndex < plugins.getParamCount(self.PluginTrack, pluginIndex):
                            self.ColT[m].TrackName = plugins.getParamName(paramIndex, self.PluginTrack, pluginIndex)
                        self.ColT[m].KnobMode = 2
                        self.ColT[m].KnobEventID = self.ColT[m].CurID + midi.REC_PlugReserved
            elif self.Page == MackieCUPage_EQ:
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

            # self.Flip knob & slider
            # if self.Flip:
                self.ColT[m].KnobEventID, self.ColT[m].SliderEventID = utils.SwapInt(self.ColT[m].KnobEventID, self.ColT[m].SliderEventID)
                self.ColT[m].SliderName = self.ColT[m].KnobName
                self.ColT[m].KnobName = self.ColT[m].SliderName
                self.ColT[m].KnobMode = 2
                if not (self.Page in [MackieCUPage_Pan, MackieCUPage_FX, MackieCUPage_EQ, MackieCUPage_Volume]):
                    self.ColT[m].KnobCenter = -1
                    self.ColT[m].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                    self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID

            self.ColT[m].LastValueIndex = 48 + m * 6
            self.ColT[m].Peak = 0
            self.ColT[m].ZPeak = False
            self.UpdateCol(m)

    def SetJogSource(self, Value):
        self.JogSource = Value

    def OnWaitingForInput(self):
        self.SendTimeMsg('..........')

    def UpdateClicking(self):
        # switch self.Clicking for transport buttons

        if device.isAssigned():
            device.midiOutSysex(
                bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x0A, int(self.Clicking), 0xF7]))
    
    # set backlight timeout (0 should switch off immediately, but doesn't really work well)
    def SetBackLight(self, Minutes):
        if device.isAssigned():
            device.midiOutSysex(
                bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x0B, Minutes, 0xF7]))

    #############################################################################################################################
    #                                                                                                                           #
    #  HANDLES THE DISPLAY METERS                                                                                                #
    #                                                                                                                           #
    #############################################################################################################################

    def UpdateMeterMode(self):
        # force vertical (activity) meter mode for free controls self.Page
        self.CurMeterMode = self.MeterMode

        if self.CurMeterMode > 0:
            self.TempMsgCount = -1
        else:
            self.TempMsgCount = 500 // 48 + 1

        # $D for horizontal, $E for vertical meters
        self.MeterMax = 0xD + int(self.CurMeterMode == 1)
        self.ActivityMax = 0xD - int(self.CurMeterMode == 1) * 6



    #############################################################################################################################
    #                                                                                                                           #
    #  HANDLES ASSIGNMENT SELECTION (PLUS CRUDE EXTENDER POSITIONING)                                                            #
    #                                                                                                                           #
    #############################################################################################################################

    def SetPage(self, Value):
        self.Page = Value

        self.FirstTrack = False
        receiverCount = device.dispatchReceiverCount()
        if receiverCount == 0:
            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack])

        self.CurPluginID = -1
        self.CurPluginOffset = 0

        self.UpdateColT()
        self.UpdateCommonLEDs()
        self.UpdateTextDisplay()

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

        elif (self.JogSource == 0x3e) | (self.JogSource == 0x3f) | (self.JogSource == B_AudioInputs):
            self.TrackSel(self.JogSource - 0x3e, event.outEv)

        elif self.JogSource == B_VI_MIDI:
            if event.outEv != 0:
                channels.processRECEvent(midi.REC_Tempo, channels.incEventValue(midi.REC_Tempo, event.outEv, midi.EKRes), midi.PME_RECFlagsT[int(event.pmeFlags & midi.PME_LiveInput != 0)] - midi.REC_FromMIDI)
            self.SendMsg2(self.ArrowsStr + 'Tempo: ' + mixer.getEventIDValueString(midi.REC_Tempo, mixer.getCurrentTempo()), 500)

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


    
# -------------------------------------------------------------------------------------------------------------------------------
# MIDI MESSAGE HANDLERS
# -------------------------------------------------------------------------------------------------------------------------------
    class EventInfo:
        def __init__(
            self,
            midiId: int = None,
            pmeFlags: int = None,
            data1: int = None,
            data2NonZero: bool = False,
        ):
            self.midiId: int = midiId
            self.pmeFlags: int = pmeFlags
            self.data1: int = data1
            self.data2NonZero: bool = data2NonZero
    
    def RegisterMidiListener(self, eventInfo: EventInfo, callback):
        self.midiListeners.append([eventInfo, callback])

    def OnMidiMsg(self, event):
        for listener in self.midiListeners:
            eventInfo = listener[0]
            callback = listener[1]
            shouldRun = (event.midiId == eventInfo.midiId and callable(callback)) \
                and (not eventInfo.pmeFlags or event.pmeFlags & eventInfo.pmeFlags != 0) \
                and (not isinstance(eventInfo.data1, int) or event.data1 == eventInfo.data1) \
                and (not eventInfo.data2NonZero or event.data2 > 0)
            if shouldRun:
                if (event.pmeFlags & midi.PME_System_Safe != 0):
                    event.handled = True
                callback(event)
            elif (event.midiId == midi.MIDI_NOTEOFF or event.pmeFlags & midi.PME_System_Safe == 0):
                event.handled = False

    def RegisteDefaultMidiListeners(self):
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_PITCHBEND), self.handleFaders)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_CONTROLCHANGE), self.handleControlChange)
        
        for key in FaderHold:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, key, True), self.sliderHold)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, B_VCA_FX, True), self.handleOpenPianoRoll)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, B_BusOutputs, True), self.handleOpenPlaylist)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, B_AudioInputs, True), self.handleOpenMixer)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, B_VI_MIDI, True), self.handleOpenChannelRack)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, B_AllUser, True), self.handleOpenBrowser)

        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_BankLeft, True), self.handleBankChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_BankRight, True), self.handleBankChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_TrackLeft, True), self.handleTrackChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_TrackRight, True), self.handleTrackChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_Flip, True), self.handleFlip)
        for key in PageSelectors:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handlePageChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User1, True), self.user1)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, B_User2, True), self.user2)
        for key in SelectButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, True), self.handleSelectButtons)
        for key in SoloButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, True), self.handleSolo)
        for key in MuteButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, True), self.handleMute)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Save, True), self.handleSave)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, B_Link, True), self.handleLink)

    #############################################################################################################################
    #                                                                                                                           #
    #   PITCH BEND (FADERS)                                                                                                     #
    #                                                                                                                           #
    #############################################################################################################################
    
    def checkFaderLink(self, midiChan):
        return device.getLinkedValue(device.findEventID(midi.EncodeRemoteControlID(device.getPortNumber(), midiChan, 255), 1))
    
    def handleFaders(self, event):
        index = event.midiChan
        if index >= self.TrackCount:
            return
        
        # AP: Check if the fader is linked to a param, and if so - unlink it from vol/pan
        if (self.checkFaderLink(index) > -1 and self.Page in [MackieCUPage_Pan, MackieCUPage_Volume]):
            self.UpdateColT()
            # The event will continue to the linked parameter
            event.handled = False
            return

        event.inEv = event.data1 + (event.data2 << 7)
        event.outEv = (event.inEv << 16) // 16383

        if self.Page == MackieCUPage_FX and self.CurPluginID >= 0:
            if (plugins.isValid(self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))):
                paramIndex = index + self.PluginParamOffset + (8 if self.isExtension else 0)
                count = plugins.getParamCount(self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))
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
            if self.ColT[index].TrackNum >= 0:
                if (self.Page != MackieCUPage_EQ) and (self.Page != MackieCUPage_FX):
                    if (TouchFaderToSelect):                       
                        if mixer.trackNumber != self.ColT[index].TrackNum:
                            mixer.setTrackNumber(self.ColT[index].TrackNum)
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

    #############################################################################################################################
    #                                                                                                                           #
    #   CONTROL CHANGE                                                                                                          #
    #                                                                                                                           #
    #############################################################################################################################
    def handleControlChange(self, event):
        if (event.midiChan == 0):
            event.inEv = event.data2
            if event.inEv >= B_AudioInputs:
                event.outEv = -(event.inEv - B_AudioInputs)
            else:
                event.outEv = event.inEv
                
            if event.data1 == 0x3C:
                if self.JogSource == 0x54:
                    transport.globalTransport(midi.FPT_Jog, 1 if event.data2 == 0x1 else -1, event.pmeFlags)
                elif self.JogSource == 0x65:
                    transport.globalTransport(midi.FPT_MoveJog, 1 if event.data2 == 0x1 else -1, event.pmeFlags)
                event.handled = True

            # if event.data1

            # knobs
            elif event.data1 in Faders:
                r = utils.KnobAccelToRes2(event.outEv)  # todo outev signof
                Res = r * (1 / (40 * 2.5))
                self.SetKnobValue(event.data1 - Faders[0], event.outEv, Res)
                event.handled = True
            else:
                event.handled = False  # for extra CCs in emulators
        else:
            event.handled = False  # for extra CCs in emulators

    #############################################################################################################################
    #                                                                                                                           #
    #   MIDI NOTEON/OFF                                                                                                         #
    #                                                                                                                           #
    #############################################################################################################################
        
    # -----------
    # Slider hold
    # -----------
    def sliderHold(self, event):
        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)

    # --------------
    # WINDOWS
    # --------------
    def handleOpenPlaylist(self, event):
        self.SendMsg2("Toggle playlist")
        if ui.getVisible(midi.widPlaylist) and ui.getFocused(midi.widPlaylist):
            ui.hideWindow(midi.widPlaylist)
        else:
            ui.showWindow(midi.widPlaylist)
            ui.setFocused(midi.widPlaylist)

    def handleOpenMixer(self, event):
        self.SendMsg2("Toggle mixer")
        if ui.getVisible(midi.widMixer) and ui.getFocused(midi.widMixer):
            ui.hideWindow(midi.widMixer)
        else:
            ui.showWindow(midi.widMixer)
            ui.setFocused(midi.widMixer)

    def handleOpenChannelRack(self, event):
        self.SendMsg2("Toggle channel rack")
        if ui.getVisible(midi.widChannelRack) and ui.getFocused(midi.widChannelRack):
            ui.hideWindow(midi.widChannelRack)
        else:
            ui.showWindow(midi.widChannelRack)
            ui.setFocused(midi.widChannelRack)

    def handleOpenPianoRoll(self, event):
        self.SendMsg2("Toggle piano roll")
        if ui.getVisible(midi.widPianoRoll) and ui.getFocused(midi.widPianoRoll):
            ui.hideWindow(midi.widPianoRoll)
        else:
            ui.showWindow(midi.widPianoRoll)
            ui.setFocused(midi.widPianoRoll)

    def handleOpenBrowser(self, event):
        self.SendMsg2("Toggle browser")
        if ui.getVisible(midi.widBrowser) and ui.getFocused(midi.widBrowser):
            ui.hideWindow(midi.widBrowser)
        else:
            ui.showWindow(midi.widBrowser)
            ui.setFocused(midi.widBrowser)

    # -------------------------------
    # BANK UP / DOWN (8/16 - 24 tracks is static?)
    # -------------------------------
    def handleBankChange(self, event):
        if self.Page == MackieCUPage_FX:
            if (self.CurPluginID != -1):  # Selected Plugin
                if (event.data1 == B_BankLeft) & (self.PluginParamOffset >= 16):
                    self.PluginParamOffset -= 16
                elif (event.data1 == B_BankRight) & (self.PluginParamOffset + 16 < plugins.getParamCount(mixer.trackNumber(), self.CurPluginID + self.CurPluginOffset)):
                    self.PluginParamOffset += 16
                self.UpdateColT()
                device.hardwareRefreshMixerTrack(-1)
            else:  # No Selected Plugin
                pass
        else:
            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == B_BankRight) * self.TrackCount)
            if not self.isExtension:
                device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
            if self.Page != MackieCUPage_FX:
                for m in range(0, 0 if self.isExtension else 1):
                    self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == B_BankRight) * self.TrackCount)
            if self.MixerScroll:
                if self.ColT[event.midiChan].TrackNum >= 0:
                    if mixer.trackNumber != self.ColT[event.midiChan].TrackNum:
                        mixer.setTrackNumber(self.ColT[event.midiChan].TrackNum+(-1), midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)
        if not self.isExtension:
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
    # ---------------------------
    # MOVE UP / DOWN (1 track)
    # ---------------------------
    def handleTrackChange(self, event):
        self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 1 + int(event.data1 == B_TrackRight) * 2)
        if not self.isExtension:
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))

    # ---------------------
    # PAGE SELECTORS
    # ---------------------
    def handleFlip(self, event):
        self.Flip = not self.Flip
        if not self.isExtension:
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
        self.UpdateColT()
        self.UpdateCommonLEDs()

    def handlePageChange(self, event):
        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)
        n = event.data1 - PageSelectors[0]
        self.SetPage(n)
        if not self.isExtension:
            self.SendMsg2(self.MackieCU_PageNameT[n])
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
    
    # --------
    # USER 1
    # --------
    def user1(self, event):
        self.SetPage(MackieCUPage_Stereo)
    # --------
    # USER 2
    # --------
    def user2(self, event):
        self.SetPage(MackieCUPage_EQ)

    # --------
    # SELECT
    # --------
    def handleSelectButtons(self, event):
        index = SelectButtons.index(event.data1)
        if self.Page in [MackieCUPage_Volume, MackieCUPage_Pan]:
            ui.showWindow(midi.widMixer)
            ui.setFocused(midi.widMixer)
            self.UpdateCommonLEDs()
            mixer.setTrackNumber(self.ColT[index].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)
            self.SendMsg2(mixer.getTrackName(self.ColT[index].TrackNum))
        elif self.Page == MackieCUPage_EQ:
            if event.data1 == 0x27:  # "Reset All"
                self.SetKnobValue(0, midi.MaxInt)
                self.SetKnobValue(1, midi.MaxInt)
                self.SetKnobValue(2, midi.MaxInt)
                self.SetKnobValue(3, midi.MaxInt)
                self.SetKnobValue(4, midi.MaxInt)
                self.SetKnobValue(5, midi.MaxInt)
                self.SetKnobValue(6, midi.MaxInt)
                self.SetKnobValue(7, midi.MaxInt)
                self.SendMsg2("All EQ levels reset")
        elif self.Page == MackieCUPage_FX:
            if self.CurPluginID == -1:
                if plugins.isValid(mixer.trackNumber(), index):
                    self.CurPluginID = index
                    self.PluginParamOffset = 0
                    mixer.focusEditor(mixer.trackNumber(), index)
                    self.UpdateColT()
                    self.UpdateCommonLEDs()
                    self.UpdateTextDisplay()
                    return
            else:
                # AP: Ignore button presses, there's no functionality that makes sense in this case
                pass
        elif self.Page == MackieCUPage_Sends:
            fromTrack = mixer.trackNumber()
            toTrack = self.FirstTrackT[self.FirstTrack] + index
            mixer.setRouteTo(
                fromTrack,
                toTrack,
                not mixer.getRouteSendActive(fromTrack, toTrack)
            )
        else:
            self.SetKnobValue(index, midi.MaxInt)


    # ------
    # SOLO
    # ------
    def handleSolo(self, event):
        if (self.Page in [MackieCUPage_Pan, MackieCUPage_Volume]):
            if (self.soloMuteClear):
                for track in range(0, mixer.trackCount()):
                    mixer.soloTrack(track, 0)
                self.SendMsg2("All mixer tracks solo removed")
            else:
                i = SoloButtons.index(event.data1)
                self.ColT[i].solomode = midi.fxSoloModeWithDestTracks
                mixer.soloTrack(self.ColT[i].TrackNum,
                    midi.fxSoloToggle, self.ColT[i].solomode)

    # ------
    # MUTE
    # ------
    def handleMute(self, event):
        if (self.Page in [MackieCUPage_Pan, MackieCUPage_Volume]):
            if (self.soloMuteClear):
                for track in range(0, mixer.trackCount()):
                    mixer.muteTrack(track, 0)
                self.SendMsg2("All mixer tracks unmuted")
            else:
                mixer.enableTrack(self.ColT[MuteButtons.index(event.data1)].TrackNum)

    # ------
    # ARM
    # ------
    def handleArm(self, event):
        if (self.Page in [MackieCUPage_Pan, MackieCUPage_Volume]):
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
    def handleSave(self, event):
        transport.globalTransport(
            midi.FPT_Save + int(self.Shift), int(event.data2 > 0) * 2, event.pmeFlags)
        
    def handleLink(self, event):
        self.linkMode = not self.linkMode
        self.UpdateCommonLEDs()
