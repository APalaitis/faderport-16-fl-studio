###########################################################
# name=MCUE Presonus FaderPort 16
# supportedDevices=PreSonus FP16
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

class TMackieCU(common.Faderport16):
    def __init__(self):
        common.Faderport16.__init__(self, False)

    def OnInit(self):
        common.Faderport16.OnInit(self)

        for key in common.FunctionButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleFunctionButtons)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Stop, True), self.handleStop)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Play, True), self.handlePlay)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Record, True), self.handleRecord)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Loop, True), self.handleLoop)
        for key in common.JogSourceButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleJogSources)
        for key in common.ShiftButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, False), self.handleShift)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Metronome, True), self.handleMetronome)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_ClearSolo, True), self.handleSoloClear)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_ClearMute, True), self.handleMuteClear)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, common.B_PanParam, True), self.handlePanParam)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, common.B_RotaryEncoder, True), self.handleRotaryEncoder)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System_Safe, common.B_Bypass, True), self.handleBypass)

    def handleFunctionButtons(self, event):
        return
    
    def handleStop(self, event):
        transport.globalTransport(midi.FPT_Stop, 1, event.pmeFlags)

    def handlePlay(self, event):
        transport.globalTransport(midi.FPT_Play, 1, event.pmeFlags)

    def handleRecord(self, event):
        transport.globalTransport(midi.FPT_Record, 1, event.pmeFlags)

    def handleLoop(self, event):
        transport.globalTransport(midi.FPT_Loop, 1, event.pmeFlags)
        
    def handleJogSources(self, event):
        self.SetJogSource(event.data1)

    def handleShift(self, event):
        self.Shift = event.data2 > 0
        self.UpdateCommonLEDs()
        self.UpdateMixer_Sel()

    def handleMetronome(self, event):
        transport.globalTransport(
            midi.FPT_Metronome, 1, event.pmeFlags)
        if (ui.isMetronomeEnabled):
            self.SendMsg2("Metronome is Enabled")
        else:
            self.SendMsg2("Metronome is Disabled")

    def handleSoloClear(self, event):
        for track in range(0, mixer.trackCount()):
            mixer.soloTrack(track, 0)

    def handleMuteClear(self, event):
        for track in range(0, mixer.trackCount()):
            mixer.muteTrack(track, 0)
    
    def handlePanParam(self, event):
        if self.Page == common.Page_Volume:
            eventId = midi.REC_Mixer_Pan + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            mixer.automateEvent(eventId, int(midi.MaxInt / 2 * 0.5), midi.REC_MIDIController, self.SmoothSpeed)
        elif self.Page == common.Page_Pan:
            eventId = midi.REC_Mixer_Vol + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            mixer.automateEvent(eventId, int(midi.MaxInt / 2 * 0.8), midi.REC_MIDIController, self.SmoothSpeed)

    def handleRotaryEncoder(self, event):
        if self.JogSource == common.Jog_Master:
            mixer.automateEvent(midi.REC_MainVol, int(midi.MaxInt / 2 * 0.8), midi.REC_MIDIController, self.SmoothSpeed)
        elif self.JogSource == common.Jog_Marker:
            arrangement.addAutoTimeMarker(arrangement.currentTime(False), "New marker")

    def handleBypass(self, event):
        mixer.enableTrackSlots(mixer.trackNumber(), not mixer.isTrackSlotsEnabled(mixer.trackNumber()))



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