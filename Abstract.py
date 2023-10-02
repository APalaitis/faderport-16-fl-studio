import midi
import device

from Types import *
from Constants import *

class Abstract():
    midiListeners = []
    ledUpdates = []
    isExtension = False
    SliderHoldCount = 0
    TrackCount = 16
    JogSource = Jog_Master
    Shift = False
    TempMsgCount = 0
    FirstTrackT = [0, 0]
    ColT = [0 for x in range(TrackCount)]
    CurPluginID = -1
    PluginTrack = 0
    linkMode = False
    Page = Page_Volume
    SmoothSpeed = 0
    MeterMax = 0

    def RegisterMidiListener(self, eventInfo: EventInfo, callback):
        self.midiListeners.append([eventInfo, callback])

    def RegisterLEDUpdate(self, callback):
        self.ledUpdates.append(callback)

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
