###########################################################
# name=Presonus FaderPort 16
# supportedDevices=PreSonus FP16
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=254916#p1607888
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

class Faderport16(Base):
    def __init__(self):
        Base.__init__(self, False)

Faderport16Impl = Faderport16()

#EOF
def OnInit():
    Faderport16Impl.OnInit()

def OnDeInit():
    Faderport16Impl.OnDeInit()

def OnDirtyMixerTrack(SetTrackNum):
    Faderport16Impl.OnDirtyMixerTrack(SetTrackNum)

def OnRefresh(Flags):
    Faderport16Impl.OnRefresh(Flags)

def OnMidiMsg(event):
    Faderport16Impl.OnMidiMsg(event)

def SendMsg2(Msg, Duration=1000):
    Faderport16Impl.SendMsg2(Msg, Duration)

def OnUpdateBeatIndicator(Value):
    Faderport16Impl.OnUpdateBeatIndicator(Value)

def OnIdle():
    Faderport16Impl.OnIdle()
