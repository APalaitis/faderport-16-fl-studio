###########################################################
# name=MCUE Presonus FaderPort 16
# receiveFrom=MCUE Presonus FaderPort 16 Extender
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

class TMackieCU(common.TMackieCU_Base):
    def __init__(self):
        common.TMackieCU_Base.__init__(self, False)

    def OnInit(self):
        common.TMackieCU_Base.OnInit(self)

        for key in common.FunctionButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleFunctionButtons)
        for key in common.ArrowButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleArrowButtons)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x5B, True), self.handleArrowKeyLeft)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, 0x5C, True), self.handleArrowKeyRight)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Stop, True), self.handleStop)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Play, True), self.handlePlay)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Record, True), self.handleRecord)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Loop, True), self.handleLoop)
        for key in common.JogSourceButtons:
            self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handleJogSources)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_LShift, False), self.handleShift)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Metronome, True), self.handleMetronome)
        self.RegisterMidiListener(self.EventInfo(midi.MIDI_NOTEON, midi.PME_System, common.B_Clear, False), self.handleSoloMuteClear)

    def handleFunctionButtons(self, event):
        return
    
    def handleArrowButtons(self, event):
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

    def handleArrowKeyLeft(self, event):
        if (event.data1 == 0x5B):
            arrangement.jumpToMarker(-1, False)

    def handleArrowKeyRight(self, event):
        if (event.data1 == 0x5C):
            arrangement.jumpToMarker(1, False)

    def handleStop(self, event):
        transport.globalTransport(midi.FPT_Stop, int(
            event.data2 > 0) * 2, event.pmeFlags)

    def handlePlay(self, event):
        transport.globalTransport(midi.FPT_Play, int(
            event.data2 > 0) * 2, event.pmeFlags)

    def handleRecord(self, event):
        transport.globalTransport(midi.FPT_Record, int(
            event.data2 > 0) * 2, event.pmeFlags)

    def handleLoop(self, event):
        transport.globalTransport(midi.FPT_Loop, int(
            event.data2 > 0) * 2, event.pmeFlags)
        
    def handleJogSources(self, event):
        self.SetJogSource(event.data1)
        self.Jog(event)  # for visual feedback

    def handleShift(self, event):
        self.Shift = event.data2 > 0

    def handleMetronome(self, event):
        transport.globalTransport(
            midi.FPT_Metronome, 1, event.pmeFlags)
        if (ui.isMetronomeEnabled):
            self.SendMsg2("Metronome is Enabled")
        else:
            self.SendMsg2("Metronome is Disabled")

    def handleSoloMuteClear(self, event):
        self.soloMuteClear = event.data2 > 0

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