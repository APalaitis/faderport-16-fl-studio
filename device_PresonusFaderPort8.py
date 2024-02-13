###########################################################
# name=Presonus FaderPort 8
# supportedDevices=PreSonus FP8
# url=https://forum.image-line.com/viewtopic.php?t=322725
###########################################################
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

from Base import Base
from Types import *
from Constants import *

##################################
# CLASS FOR GENERAL FUNCTIONALITY
##################################

class Faderport8(Base):
    def __init__(self):
        Base.__init__(self, True)

Faderport8Impl = Faderport8()

#EOF
def OnInit():
    Faderport8Impl.OnInit()

def OnDeInit():
    Faderport8Impl.OnDeInit()

def OnDirtyMixerTrack(SetTrackNum):
    Faderport8Impl.OnDirtyMixerTrack(SetTrackNum)

def OnRefresh(Flags):
    Faderport8Impl.OnRefresh(Flags)

def OnMidiMsg(event):
    Faderport8Impl.OnMidiMsg(event)

def SendMsg2(Msg, Duration=1000):
    Faderport8Impl.SendMsgToFL(Msg, Duration)

def OnUpdateBeatIndicator(Value):
    Faderport8Impl.OnUpdateBeatIndicator(Value)

def OnIdle():
    Faderport8Impl.OnIdle()
