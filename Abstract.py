import midi
import device

from Types import *
from Constants import *

class Abstract():
    midiListeners = []
    ledUpdates = []
    isFP8 = False
    isExtension = False
    SliderHoldCount = 0
    TrackCount = 16
    JogSource = Jog_Channel
    Shift = False
    TempMsgCount = 0
    FirstTrackT = [0, 0]
    ColT = [0] * TrackCount
    CurPluginID = -1
    PluginTrack = 0
    linkMode = False
    armMode = False
    Page = Page_Volume
    SmoothSpeed = 0
    MeterMax = 0
    lastSoloTrack = -1

    def SendMsgToFL(msg): return
    def UpdateColT(): return
    def UpdateTextDisplay(): return
    def OnMidiMsg(self, event): return
    def handleResponsiveButtonLED(self, event): return
    def automateEvent(self, eventId, value, smoothSpeed): return

    def noop(*args): return

    def RegisterMidiListener(self, eventInfo: EventInfo, callback, setEventHandled = True):
        self.midiListeners.append([eventInfo, callback, setEventHandled])

    def RegisterLEDUpdate(self, callback):
        self.ledUpdates.append(callback)

    def UpdateLEDs(self):
        for update in self.ledUpdates:
            if device.isAssigned() and callable(update):
                update()


    #############################################################################################################################
    #                                                                                                                           #
    #  CALLED FROM UPDATECOL TO RETURN SLIDER / LEVEL VALUEDS                                                                   #
    #                                                                                                                           #
    #############################################################################################################################
    def AlphaTrack_LevelToSlider(self, Value, Max=midi.FromMIDI_Max):
        return round(Value / Max * AlphaTrack_SliderMax)

    #############################################################################################################################
    #                                                                                                                           #
    #  CALLED FROM UPDATECOL TO RETURN SLIDER / LEVEL VALUEDS                                                                   #
    #                                                                                                                           #
    #############################################################################################################################
    def AlphaTrack_SliderToLevel(self, Value, Max=midi.FromMIDI_Max):
        return min(round(Value / AlphaTrack_SliderMax * Max), Max)
