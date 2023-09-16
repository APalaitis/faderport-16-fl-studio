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
MackieCU_nFreeTracks = 64

# -----------------
# STATIC VARIABLES
# -----------------
# Mackie CU pages
StartTime=time.time()
MackieCUPage_Stereo = 0 # Not yet assigned to any button
MackieCUPage_Sends = 1
MackieCUPage_Pan = 2
MackieCUPage_FX = 3
MackieCUPage_EQ = 4 # Not yet assigned to any button
MasterPeak = 0
#->
ExtenderLeft = 0
ExtenderRight = 1
#-<
# Standard Mackie
#LCD1 =
Ext1 =          bytearray([0xF0, 0x00, 0x00, 0x66, 0x15, 0x12, 0])  #Extender 1 Mackie Address
# QCON X Display 2
QCONX_LCD2 =    bytearray([0xF0, 0x00, 0x00, 0x67, 0x15, 0x13, 0])  #Base QCON Screen 2 Address
QCONX_Ext2 =    bytearray([0xF0, 0x00, 0x00, 0x67, 0x16, 0x13 ,0])  #Extender QCON Screen 2 Address????
# EMAGIC?
EMAGIC_LCD1 =   bytearray([0xF0, 0x00, 0x00, 0x66, 0x10, 0x12, 0])  #Base EMAGIC Mackie Address
EMAGIC_EXT =    bytearray([0xF0, 0x00, 0x00, 0x66, 0x11, 0x12, 0])  #Base EMAGIC Mackie Address

# Button Groups
SelectButtons = [0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F] # In the main volume/pan page
SelectButtonsEX = [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27] # When in pages like plugins or sends
PageSelectors = [0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D]
MuteButtons = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]
SoloButtons = [0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF]
Faders = [0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0x6F]

#->
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
#-<                
#!<
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
#->

#######################
# Current Key Mappings:
#######################

#Function Keys:
Function1=54 #Cut (Keyboard Equivelant of CTRL+X)
Function2=55 #Copy (Keyboard Equivelant of CTRL+C)
Function3=56 #Paste (Keyboard Equivelant of CTRL+V)
Function4=57 #Insert (Keyboard Insert Key)
Function5=58 #Delete (Keyboard Delete key)
Function6=59 #Item Menu (Shows the item menu of the currently selected Item)
Function7=60 #Undo/Redo (Undo/Redo toggle the last operation)
Function8=61 #Undo History (Use the Jog Dial to review the undo history)
Function9=62 #Pattern/Playlist Window (Selected Pattern will appear on secondary Display)
Function10=63 #Mixer Window (Shift toggles display layouts)
Function11=64 #Channel Window (Shift will bring up the current editor/plugin)
Function12=65 #Tempo (Tap out a tempo with this button)
Function13=66 #UnMute all Tracks (With Shift Will disarm all tracks)
Function14=67 #Banking Selection (Toggles Selection of tracks when Banking)|Colour Variations for selected FL Component
Function15=68 #Jog Toggle (Toggles control of the Jog Dial to the Playlist)
Function16=69 #Colour Toggle (toggles between colour setting for the Mixer - Shift for FL default)
FLC_Mapping=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#-<
MCUELU={}

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
        # [0=default], [1=parameter, pan, volume, off],[2=self.Flip],[3=centered?],[4=?]
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
        self.LastMsgLen = 0x37
        self.TempMsgT = ["", ""]
        self.LastTimeMsg = bytearray(10)
        self.Shift = False
        self.Control = False
        self.Option = False
        self.Alt = False
        self.TempMsgDirty = False
        self.JogSource = 0
        self.TempMsgCount = 0
        self.SliderHoldCount = 0
        self.FirstTrack = 9 if isExtension else 1
        self.FirstTrackT = [0, 0]
        self.ColT = [0 for x in range(9)]
        for x in range(0, 9):
            self.ColT[x] = TMackieCol()
        self.FreeCtrlT = [0 for x in range(
            MackieCU_nFreeTracks - 1 + 2)]  # 64+1 sliders
        self.Clicking = False
        self.Scrub = False
        self.Flip = False
        self.MeterMode = 1  # enabled!
        self.CurMeterMode = 0
        self.Page = MackieCUPage_Pan # AP: The device itself seems to default to this page.
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
        self.MackieCU_MeterModeNameT = ('Meters Disabled', 'Meters Enabled','+ Selected Track Shown')
        self.MackieCU_ExtenderPosT = ('left', 'right')
        self.FreeEventID = 400
        self.ArrowsStr = chr(0x7F) + chr(0x7E) + chr(0x32)
        self.AlphaTrack_SliderMax = round(13072 * 16000 / 12800)
        self.CurPluginID = -1
        self.LCD1 = bytearray([0xF0, 0x00, 0x00, 0x66, 0x15 if isExtension else 0x14, 0x12, 0])  #Base Mackie Address
        self.LCD2 = bytearray([0xF0, 0x00, 0x00, 0x67, 0x15, 0x13, 0])  #Base QCON Screen 2 Address
        #                     [0xF0, 0x00, 0x00, 0x67, 0x15, 0x13
        self.MasterPeak = 0
        self.Msg1 = ''
        self.Msg2 = ''
        self.ShowTrackNumbers = ShowTrackNos
        if (DefaultFreeDisplayToZen):
            self.FreeText = 0  # Zenology - change to 1 (generic) or -1 (blank)
        else:
            self.FreeText = -1  # Zenology - change to 1 (generic) or -1 (blank)            
        if (DefaultFreeDisplayToGen):
            self.FreeText = 1 #Generic) or -1 (blank)
        else:
            self.FreeText = -1  # Zenology - change to 1 (generic) or -1 (blank)            
        self.colourOptions = 0
        self.ShowSelectedTrackInTimeWindow=False
        self.MixerScroll = SelectTrackWithBanking
        self.PreviousCommand=0x0
        self.LastData2=0x0
        self.PrevProc="-"
        if (not isExtension):
            self.ExtenderPos = ExtenderLeft
        self.PluginTrack = 0
        self.midiListeners = []

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
        #self.FirstTrack = 1
        self.FirstTrackT[0] = self.FirstTrack
        self.SmoothSpeed = 469
        self.Clicking = True

        device.setHasMeters()
        self.LastTimeMsg = bytearray(10)

        for m in range(0, len(self.FreeCtrlT)):
            self.FreeCtrlT[m] = 8192  # default free faders to center
        if device.isAssigned():
            device.midiOutSysex(
                bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x0C, 1, 0xF7]))
        self.SetBackLight(2)  # backlight timeout to 2 minutes
        self.UpdateClicking()
        self.UpdateMeterMode()
        self.SetPage(self.Page)
        self.SendMsg(chr(32)*112)
        self.SendMsg2(chr(32)*112)
        ui.setHintMsg(device.getName())    
        #self.OnSendTempMsg('Linked to ' + ui.getProgTitle() + ' (' + ui.getVersion() + ')', 2000);
        self.OnSendTempMsg("MCUE script version 1.0.0            ", 2000)
        self.RegisteDefaultMidiListeners()

    #############################################################################################################################
    #                                                                                                                           #
    #      Called before the script will be stopped.                                                                               #
    #                                                                                                                           #
    #############################################################################################################################
    def OnDeInit(self):
        if device.isAssigned():
            for m in range(0, 8):
                device.midiOutSysex(
                    bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.Extension else 0x14, 0x20, m, 0, 0xF7]))
                device.midiOutSysex(bytes(bytearray([0xd1, 0, 0xF7])))
                device.midiOutSysex(bytes(bytearray([0xd1, 16, 0xF7])))

            if ui.isClosing():
                # self.SendMsg(chr(32)*112)
                self.SendMsg( "Your MCUE script version is 1.0.0 (Please check on www.gadgeteer.home.blog for updates).   ")
                # self.SendMsg2(chr(32)*112)
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
            for m in range(0,  len(self.ColT) - 1):
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
        Num %= 8
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
            if (self.CurPluginID > -1 and self.Page == MackieCUPage_FX):
                for n in range(0, len(self.ColT)):
                    self.UpdateCol(n)

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
        SyncLEDMsg = [midi.MIDI_NOTEON + (0x5E << 8), midi.MIDI_NOTEON + (
            0x5E << 8) + (0x7F << 16), midi.MIDI_NOTEON + (0x5E << 8) + (0x7F << 16)]

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
            for m in range(0, len(self.ColT) - 1):
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
                (0x5D << 8) + midi.TranzPort_OffOnT[transport.isPlaying() == midi.PM_Stopped], 0)
            # loop
            LoopMode = transport.getLoopMode()
            device.midiOutNewMsg((0x5A << 8) +
                                 midi.TranzPort_OffOnT[LoopMode == midi.SM_Pat], 1)
            # record
            r = transport.isRecording()
            device.midiOutNewMsg(
                (0x5F << 8) + midi.TranzPort_OffOnT[r], 2)
            # SMPTE/BEATS
            device.midiOutNewMsg(
                (0x71 << 8) + midi.TranzPort_OffOnT[ui.getTimeDispMin()], 3)
            device.midiOutNewMsg(
                (0x72 << 8) + midi.TranzPort_OffOnT[not ui.getTimeDispMin()], 4)
            # self.Page
            for m in range(0,  6):
                device.midiOutNewMsg(
                    ((0x28 + m) << 8) + midi.TranzPort_OffOnT[m == self.Page], 5 + m)
            # changed flag
            device.midiOutNewMsg(
                (0x50 << 8) + midi.TranzPort_OffOnT[general.getChangedFlag() > 0], 11)
            # metronome
            device.midiOutNewMsg(
                (0x59 << 8) + midi.TranzPort_OffOnT[general.getUseMetronome()], 12)
            # rec precount
            device.midiOutNewMsg(
                (0x58 << 8) + midi.TranzPort_OffOnT[general.getPrecount()], 13)
            # self.Scrub
            device.midiOutNewMsg((0x65 << 8) +
                                 midi.TranzPort_OffOnT[self.Scrub], 15)
            # use RUDE SOLO to show if any track is armed for recording
            b = 0
            for m in range(0,  mixer.trackCount()):
                if mixer.isTrackArmed(m):
                    b = 1 + int(r)
                    break

            device.midiOutNewMsg(
                (0x73 << 8) + midi.TranzPort_OffOnBlinkT[b], 16)
            # smoothing
            #device.midiOutNewMsg(
            #    (0x33 << 8) + midi.TranzPort_OffOnT[self.SmoothSpeed > 0], 17)
            # self.Flip
            device.midiOutNewMsg(
                (0x32 << 8) + midi.TranzPort_OffOnT[self.Flip], 18)
            # focused windows
            device.midiOutNewMsg(
                (0x45 << 8) + midi.TranzPort_OffOnT[ui.getFocused(midi.widBrowser)], 20)
            device.midiOutNewMsg((0x3E << 8) +
                                 midi.TranzPort_OffOnT[ui.getFocused(midi.widPlaylist)], 21)
            BusLed = ui.getFocused(midi.widMixer) & (
                self.ColT[0].TrackNum >= 100)
            OutputLed = ui.getFocused(midi.widMixer) & (
                self.ColT[0].TrackNum >= 0) & (self.ColT[0].TrackNum <= 1)
            InputLed = ui.getFocused(midi.widMixer) & (
                not OutputLed) & (not BusLed)
            device.midiOutNewMsg((0x3F << 8) +
                                 midi.TranzPort_OffOnT[InputLed], 22)
            device.midiOutNewMsg((0x41 << 8) +
                                 midi.TranzPort_OffOnT[ui.getFocused(midi.widChannelRack)], 23)
            device.midiOutNewMsg((0x43 << 8) +
                                 midi.TranzPort_OffOnT[BusLed], 24)
            device.midiOutNewMsg(
                (0x44 << 8) + midi.TranzPort_OffOnT[OutputLed], 25)

            # device.midiOutNewMsg((0x4B << 8) + midi.TranzPort_OffOnT[ui.getFocused(midi.widChannelRack)], 21)

# -------------------------------------------------------------------------------------------------------------------------------
# PROCEDURES
# -------------------------------------------------------------------------------------------------------------------------------
    #############################################################################################################################
    #                                                                                                                           #
    #   SEND A MESSAGE TO A DISPLAY                                                                                             #
    #                                                                                                                           #
    #############################################################################################################################

    def SendMsg(self, Msg, Row=0, Display=1):
        #Msg=Msg.rstrip()
        if Display == 1:
            if (EMAGIC):
                sysex = EMAGIC_LCD1 + bytearray(Msg, 'utf-8')
            else: 
                sysex = self.LCD1 + bytearray(Msg, 'utf-8') 
            sysex.append(0xF7)
            device.midiOutSysex(bytes(sysex))
    
        elif Display == 2:
            if (TargetSecondDisplays):
                sysex = self.LCD2 + bytearray(Msg, 'utf-8')
                sysex.append(0xF7)
                device.midiOutSysex(bytes(sysex))
            elif (RouteTempTextToClassic):
               #sysex = self.LCD1 + bytearray(Msg[0:56].rstrip(), 'utf-8')
               sysex = self.LCD1 + bytearray(Msg, 'utf-8')
               sysex.append(0xF7)
               device.midiOutSysex(bytes(sysex))
        elif Display == 3:
            ui.setHintMsg(Msg)
            

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
            if (TargetSecondDisplays):
                self.SendMsg('  '+Msg.ljust(54, ' '), 0, 2)
            elif RouteTempTextToClassic: 
                if SplitAccrossScribbleStrips:
                    self.OnSendTempMsg(self.TidyScribbles(Msg),Duration)
                else:    
                    self.OnSendTempMsg(Msg,Duration)
                
         
    def OnSendTempMsg(self, Msg, Duration = 500):
        if RouteTempTextToClassic: 
            self.TempMsgCount = (Duration // 48) + 1
            self.TempMsgT[1] = Msg.ljust(56, ' ')
            self.TempMsgDirty = True
            
    def UpdateTempMsg(self):
        if (RouteTempTextToClassic):
            self.SendMsg(self.TempMsgT[int(self.TempMsgCount != 0)],0,2) #todo was sendmsg

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
        for index in range(0, len(self.ColT) - 1):
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
            elif ((self.Page == MackieCUPage_Sends) or (self.Page == MackieCUPage_Pan) or (self.Page == MackieCUPage_Stereo)):
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
            if ((self.Page == MackieCUPage_Sends) or (self.Page == MackieCUPage_Pan) or (self.Page == MackieCUPage_Stereo) or (self.Page == MackieCUPage_FX)):
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
        s3=" "*56+s3       
        self.SendMsg(s1+s2,0,1)
        n=device.dispatchReceiverCount()+1
        if (AlwaysShowSelectedTrack):
            self.SendAssignmentMsg(str(mixer.trackNumber()).zfill(3))
#        self.SendMsg2(s3[0:112] + 'BNK'+str(math.ceil(self.ColT[m].TrackNum/(8*n))).zfill(2))
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
            for m in range(0, len(self.ColT) - 1):
                device.midiOutNewMsg(
                    ((0x18 + m) << 8) +
                    midi.TranzPort_OffOnT[self.ColT[m].TrackNum == mixer.trackNumber()]
                , self.ColT[m].LastValueIndex + 4)

        if self.Page in [MackieCUPage_Pan, MackieCUPage_FX]:
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
            
            linkValue = self.checkFaderLink(Num % 8)
            # AP: Plugin params don't have REC events associated with them, so we use functions to get the values
            if self.Page == MackieCUPage_FX:
                if (self.CurPluginID >= 0):
                    if (plugins.isValid(self.PluginTrack, self.CurPluginID)):
                        paramCount = plugins.getParamCount(self.PluginTrack, self.CurPluginID)
                        paramIndex = Num + (8 if self.isExtension else 0)
                        if paramIndex < paramCount:
                            paramValue = plugins.getParamValue(paramIndex, self.PluginTrack, self.CurPluginID)
                            sv = int(midi.FromMIDI_Max * paramValue)
            # AP: If the control is linked, don't move the fader
            elif linkValue > -1 and self.Page == MackieCUPage_Pan:
                sv = int(midi.FromMIDI_Max * linkValue)

            if Num < 8:
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
                    midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (data1 << 16), self.ColT[Num].LastValueIndex)

                # arm, solo, mute
                device.midiOutNewMsg(((0x00 + Num) << 8) + midi.TranzPort_OffOnBlinkT[int(mixer.isTrackArmed(
                    self.ColT[Num].TrackNum)) * (1 + int(transport.isRecording()))], self.ColT[Num].LastValueIndex + 1)
                if (self.Page == MackieCUPage_Sends):
                    isBeingSentTo = mixer.getRouteSendActive(mixer.trackNumber(), self.ColT[Num].TrackNum)
                    device.midiOutNewMsg(((0x08 + Num) << 8) + midi.TranzPort_OffOnT[isBeingSentTo], self.ColT[Num].LastValueIndex + 2)
                    device.midiOutNewMsg(((0x10 + Num) << 8) + midi.TranzPort_OffOnT[isBeingSentTo], self.ColT[Num].LastValueIndex + 3)
                else:
                    device.midiOutNewMsg(((0x08 + Num) << 8) + midi.TranzPort_OffOnT[mixer.isTrackSolo(
                        self.ColT[Num].TrackNum)], self.ColT[Num].LastValueIndex + 2)
                    device.midiOutNewMsg(((0x10 + Num) << 8) + midi.TranzPort_OffOnT[not mixer.isTrackEnabled(
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

            # mixer
            if m == 8:
                self.ColT[m].TrackNum = -2
                self.ColT[m].BaseEventID = midi.REC_MainVol
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID
                self.ColT[m].SliderName = 'Master Volume'
            else:
                self.ColT[m].TrackNum = midi.TrackNum_Master + \
                    ((f + m) % mixer.trackCount())
                self.ColT[m].BaseEventID = mixer.getTrackPluginId(
                    self.ColT[m].TrackNum, 0)
                self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + \
                    midi.REC_Mixer_Vol
                s = ch+mixer.getTrackName(self.ColT[m].TrackNum)
                self.ColT[m].SliderName = s + ' - Volume'

                self.ColT[m].KnobEventID = -1
                self.ColT[m].KnobResetEventID = -1
                self.ColT[m].KnobResetValue = midi.FromMIDI_Max >> 1
                self.ColT[m].KnobName = ''
                self.ColT[m].KnobMode = 1  # parameter, pan, volume, off
                self.ColT[m].KnobCenter = -1

                self.ColT[m].TrackName = ''

                if self.Page == MackieCUPage_Pan:
                    self.ColT[m].KnobEventID = self.ColT[m].BaseEventID + \
                        midi.REC_Mixer_Pan
                    self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID
                    self.ColT[m].KnobName = ch+mixer.getTrackName(
                        self.ColT[m].TrackNum) + ' - ' + 'Pan'
                elif self.Page == MackieCUPage_Stereo:
                    self.ColT[m].KnobEventID = self.ColT[m].BaseEventID + \
                        midi.REC_Mixer_SS
                    self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID
                    self.ColT[m].KnobName = mixer.getTrackName(
                        self.ColT[m].TrackNum) + ' - ' + 'Separation'
                elif self.Page == MackieCUPage_Sends:
                    self.ColT[m].KnobEventID = CurID + \
                        midi.REC_Mixer_Send_First + self.ColT[m].TrackNum
                    s = mixer.getEventIDName(self.ColT[m].KnobEventID)
                    self.ColT[m].KnobName = s
                    self.ColT[m].KnobResetValue = round(
                        12800 * midi.FromMIDI_Max / 16000)
                    self.ColT[m].KnobCenter = mixer.getRouteSendActive(
                        mixer.trackNumber(), self.ColT[m].TrackNum)
                    if self.ColT[m].KnobCenter == 0:
                        self.ColT[m].KnobMode = 4
                    else:
                        self.ColT[m].KnobMode = 2
                elif self.Page == MackieCUPage_FX:
                    if self.CurPluginID == -1:  # Plugin not selected
                        index = m + self.CurPluginOffset + (8 if self.isExtension else 0)
                        if not self.isExtension or index < 10:
                            self.PluginTrack = mixer.trackNumber()
                            self.ColT[m].CurID = mixer.getTrackPluginId(
                                self.PluginTrack, index)
                            self.ColT[m].KnobEventID = self.ColT[m].CurID + \
                                midi.REC_Plug_MixLevel
                            s = mixer.getEventIDName(self.ColT[m].KnobEventID)
                            self.ColT[m].KnobName = s
                            self.ColT[m].KnobResetValue = midi.FromMIDI_Max

                            IsValid = mixer.isTrackPluginValid(
                                self.PluginTrack, index)
                            IsEnabledAuto = mixer.isTrackAutomationEnabled(
                                self.PluginTrack, index)
                            if IsValid:
                                self.PluginTrack = self.PluginTrack
                                self.ColT[m].KnobMode = 2
                                self.ColT[m].KnobPressEventID = self.ColT[m].CurID + \
                                    midi.REC_Plug_Mute

                                self.ColT[m].TrackName = plugins.getPluginName(
                                    self.PluginTrack, index)
                            else:
                                self.ColT[m].KnobMode = 4
                            self.ColT[m].KnobCenter = int(
                                IsValid & IsEnabledAuto)
                    else:  # Plugin selected
                        pluginIndex = self.CurPluginID + self.CurPluginOffset
                        self.ColT[m].CurID = mixer.getTrackPluginId(
                            self.PluginTrack, pluginIndex)
                        if (plugins.isValid(self.PluginTrack, pluginIndex)):
                            paramIndex = m + self.PluginParamOffset + (8 if self.isExtension else 0)
                            if paramIndex < plugins.getParamCount(self.PluginTrack, pluginIndex):
                                self.ColT[m].TrackName = plugins.getParamName(
                                    paramIndex, self.PluginTrack, pluginIndex)
                            self.ColT[m].KnobMode = 2
                            self.ColT[m].KnobEventID = self.ColT[m].CurID + \
                                midi.REC_PlugReserved
                elif self.Page == MackieCUPage_EQ:
                    if m < 3:
                        # gain & freq
                        self.ColT[m].SliderEventID = CurID + \
                            midi.REC_Mixer_EQ_Gain + m
                        self.ColT[m].KnobResetEventID = self.ColT[m].SliderEventID
                        s = mixer.getEventIDName(
                            self.ColT[m].SliderEventID)
                        self.ColT[m].SliderName = s
                        self.ColT[m].KnobEventID = CurID + \
                            midi.REC_Mixer_EQ_Freq + m
                        s = mixer.getEventIDName(self.ColT[m].KnobEventID)
                        self.ColT[m].KnobName = s
                        self.ColT[m].KnobResetValue = midi.FromMIDI_Max >> 1
                        self.ColT[m].KnobCenter = -2
                        self.ColT[m].KnobMode = 0
                    else:
                        if m < 6:
                            # Q
                            self.ColT[m].SliderEventID = CurID + \
                                midi.REC_Mixer_EQ_Q + m - 3
                            self.ColT[m].KnobResetEventID = self.ColT[m].SliderEventID
                            s = mixer.getEventIDName(
                                self.ColT[m].SliderEventID)
                            self.ColT[m].SliderName = s
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
                if self.Flip:
                    self.ColT[m].KnobEventID, self.ColT[m].SliderEventID = utils.SwapInt(
                        self.ColT[m].KnobEventID, self.ColT[m].SliderEventID)
                    s = self.ColT[m].SliderName
                    self.ColT[m].SliderName = self.ColT[m].KnobName
                    self.ColT[m].KnobName = s
                    self.ColT[m].KnobMode = 2
                    if not (self.Page in [MackieCUPage_Pan, MackieCUPage_FX, MackieCUPage_EQ]):
                        self.ColT[m].KnobCenter = -1
                        self.ColT[m].KnobResetValue = round(
                            12800 * midi.FromMIDI_Max / 16000)
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

        if device.isAssigned():
            # clear peak indicators
            for m in range(0, len(self.ColT) - 1):
                device.midiOutMsg(midi.MIDI_CHANAFTERTOUCH +
                                  (0xF << 8) + (m << 12))
            # disable all meters
            for m in range(0, 8):
                device.midiOutSysex(
                    bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x20, m, 0, 0xF7]))

        if self.CurMeterMode > 0:
            self.TempMsgCount = -1
        else:
            self.TempMsgCount = 500 // 48 + 1

        # $D for horizontal, $E for vertical meters
        self.MeterMax = 0xD + int(self.CurMeterMode == 1)
        self.ActivityMax = 0xD - int(self.CurMeterMode == 1) * 6

        if device.isAssigned():
            # device.midiOutSysex(bytes(bytearray([0xd1, 0xD, 0xF7])))
            # device.midiOutSysex(bytes(bytearray([0xd1, 0xD+16, 0xF7])))
            # horizontal/vertical meter mode
            device.midiOutSysex(
                bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x21, int(self.CurMeterMode > 0), 0xF7]))

            # enable all meters
            if self.CurMeterMode == 2:
                n = 1
            else:
                n = 1 + 2
            for m in range(0, 8):
                device.midiOutSysex(
                    bytes([0xF0, 0x00, 0x00, 0x66, 0x15 if self.isExtension else 0x14, 0x20, m, n, 0xF7]))



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
                and (not eventInfo.data1 or event.data1 == eventInfo.data1) \
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
        
        for key in Faders:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, key, True), self.sliderHold)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x90, True), self.pianoRoll)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x91, True), self.hideWindows)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x92, True), self.handlePlaylist)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x3f, True), self.handleMixer)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x40, True), self.handleChannelRack)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x41, True), self.handleTempo)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, None, 0x4c, True), self.handleWindow)

        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x34, True), self.handleMode)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x2e, True), self.handleBankChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x2f, True), self.handleBankChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x30, True), self.handleTrackChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x31, True), self.handleTrackChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x32, True), self.handleFlip)
        for key in PageSelectors:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handlePageChange)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x53, True), self.user1)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x52, True), self.user2)
        for key in SelectButtonsEX:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleSelectButtonsEX)
        for key in SelectButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, False), self.handleSelectButtons)
        for key in SoloButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, False), self.handleSolo)
        for key in MuteButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, key, False), self.handleMute)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, 0x50, False), self.handleSave)

    #############################################################################################################################
    #                                                                                                                           #
    #   PITCH BEND (FADERS)                                                                                                     #
    #                                                                                                                           #
    #############################################################################################################################
    
    def checkFaderLink(self, midiChan):
        return device.getLinkedValue(device.findEventID(midi.EncodeRemoteControlID(device.getPortNumber(), midiChan, 255), 1))
    
    def handleFaders(self, event):
        index = event.midiChan % 8
        
        # AP: Check if the fader is linked to a param, and if so - unlink it from vol/pan
        if (self.checkFaderLink(index) > -1 and self.Page == MackieCUPage_Pan):
            self.UpdateColT()
            # The event will continue to the linked parameter
            event.handled = False
            return

        if event.midiChan <= 8:
            event.inEv = event.data1 + (event.data2 << 7)
            event.outEv = (event.inEv << 16) // 16383
            event.inEv -= 0x2000

        if self.Page == MackieCUPage_FX and self.CurPluginID >= 0:
            if (plugins.isValid(self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))):
                index = self.ColT[event.midiChan].TrackNum - 1
                count = plugins.getParamCount(self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))
                if index < count:
                    level = self.AlphaTrack_SliderToLevel(event.inEv + 0x2000) / midi.FromMIDI_Max
                    plugins.setParamValue(level, index, self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))
                    event.handled = True
                    self.UpdateColT()
                    # hint
                    self.SendMsg2(
                        plugins.getParamName((self.ColT[event.midiChan].TrackNum - 1) % 8, self.PluginTrack, int(self.CurPluginID + self.CurPluginOffset))
                        + ': '
                        + str(round(level, 2)))
        elif self.ColT[event.midiChan].SliderEventID >= 0:
            # slider (mixer track volume)
            if self.ColT[event.midiChan].TrackNum >= 0:
                if (self.Page != MackieCUPage_EQ) and (self.Page != MackieCUPage_FX):
                    if (TouchFaderToSelect):                       
                        if mixer.trackNumber != self.ColT[event.midiChan].TrackNum:
                            mixer.setTrackNumber(self.ColT[event.midiChan].TrackNum)
            event.handled = True
            mixer.automateEvent(self.ColT[event.midiChan].SliderEventID, self.AlphaTrack_SliderToLevel(
                event.inEv + 0x2000), midi.REC_MIDIController, self.SmoothSpeed)
            # hint
            n = mixer.getAutoSmoothEventValue(
                self.ColT[event.midiChan].SliderEventID)
            s = mixer.getEventIDValueString(
                self.ColT[event.midiChan].SliderEventID, n)
            if s != '':
                s = ': ' + s
            self.SendMsg2(self.ColT[event.midiChan].SliderName + s)

    #############################################################################################################################
    #                                                                                                                           #
    #   CONTROL CHANGE                                                                                                          #
    #                                                                                                                           #
    #############################################################################################################################
    def handleControlChange(self, event):
        if (event.midiChan == 0):
            event.inEv = event.data2
            if event.inEv >= 0x40:
                event.outEv = -(event.inEv - 0x40)
            else:
                event.outEv = event.inEv
                
            if event.data1 == 0x3C:
                if not self.isExtension:
                    self.Jog(event)
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
    #   MIDI NOTEON/OFF                                                                                                         #
    #                                                                                                                           #
    #############################################################################################################################
        
    # -----------
    # Slider hold
    # -----------
    def sliderHold(self, event):
        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)

    # -----------
    # Piano Roll
    # -----------
    def pianoRoll(self, event):
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
    def hideWindows(self, event):
        for x in range(0, 5):
            ui.hideWindow(x)


    # --------------
    # Playlist
    # --------------
    def handlePlaylist(self, event):
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
    def handleMixer(self, event):
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
    def handleChannelRack(self, event):
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
    def handleTempo(self, event):
        transport.globalTransport(midi.FPT_TapTempo, 1)
        s = str(mixer.getCurrentTempo(True))[:-2]
        self.SendMsg2("Tempo: "+s)
    # --------
    # WINDOW
    # --------
    def handleWindow(self, event):
        ui.nextWindow()
        s = ui.getFocusedFormCaption()
        if s != "":
            self.SendMsg2('Current window: ' + s)
    # ---------------
    # MODE (METERS)
    # ---------------
    def handleMode(self, event):
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
            if not self.isExtension:
                device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
            device.midiOutSysex(bytes(bytearray([0xd1, 0, 0xF7])))
            device.midiOutSysex(bytes(bytearray([0xd1, 16, 0xF7])))
    # -------------------------------
    # BANK UP / DOWN (8/16 - 24 tracks is static?)
    # -------------------------------
    def handleBankChange(self, event):
        self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
        if not self.isExtension:
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
        for m in range(0,  0 if self.isExtension else 1):
            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
            if not self.isExtension:
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
    def handleTrackChange(self, event):
        self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 1 + int(event.data1 == 0x31) * 2)
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
        n = event.data1 - 0x28
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
    # ------------
    # SELECT BUTTONS (EX)
    # ------------
    def handleSelectButtonsEX(self, event):
        isReceiver = event.data2 == 0x7e
        selectIndex = event.data1 - 0x20
        selectIndex += 8 if (self.isExtension != isReceiver) else 0
        if self.Page == MackieCUPage_EQ:
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
                self.SetKnobValue(selectIndex, midi.MaxInt)
                if not isReceiver:
                    device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (0x7e << 16))
            else:
                # AP: Ignore button presses, there's no functionality that makes sense in this case
                pass
        elif self.Page == MackieCUPage_Sends:
            mixer.setRouteTo(
                mixer.trackNumber(),
                selectIndex + 1,
                not mixer.getRouteSendActive(mixer.trackNumber(), selectIndex + 1)
            )
        else:
            self.SetKnobValue(selectIndex, midi.MaxInt)

    # --------
    # SELECT
    # --------
    def handleSelectButtons(self, event):
        i = event.data1 - 0x18

        ui.showWindow(midi.widMixer)
        ui.setFocused(midi.widMixer)
        self.UpdateCommonLEDs()
        mixer.setTrackNumber(
            self.ColT[i].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

        if self.Control:  # Link channel to track
            mixer.linkTrackToChannel(midi.ROUTE_ToThis)
        # Show Full Trackname on second display:
        # EXPAND WITH CONTEXT?
        self.SendMsg2(mixer.getTrackName(self.ColT[i].TrackNum))

    # ------
    # SOLO
    # ------
    def handleSolo(self, event):
        if (self.Page == MackieCUPage_Pan):
            i = event.data1 - 0x8
            self.ColT[i].solomode = midi.fxSoloModeWithDestTracks
            if self.Shift:
                Include(self.ColT[i].solomode,midi.fxSoloModeWithSourceTracks)
            mixer.soloTrack(self.ColT[i].TrackNum,
                midi.fxSoloToggle, self.ColT[i].solomode)

    # ------
    # MUTE
    # ------
    def handleMute(self, event):
        if (self.Page == MackieCUPage_Pan):
            mixer.enableTrack(
                self.ColT[event.data1 - 0x10].TrackNum)

    # ------
    # ARM
    # ------
    def handleArm(self, event):
        if (self.Page == MackieCUPage_Pan):
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


