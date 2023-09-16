###########################################################
# name=MCUE Presonus FaderPort 16 Extender
# receiveFrom=MCUE Presonus FaderPort 16
# supportedDevices=MIDIIN2 (PreSonus FP16)
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=254916#p1607888
###########################################################

import common

##################################
# CLASS FOR GENERAL FUNCTIONALITY
##################################

class TMackieCU(common.TMackieCU_Base):
    def __init__(self):
        common.TMackieCU_Base.__init__(self, True)

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
