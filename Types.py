# CLASS FOR COLUMN RELATED ITEMS
class FaderColumn:
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

# Used to register MIDI events
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