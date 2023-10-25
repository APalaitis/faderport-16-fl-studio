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

from Types import *
from Constants import *
from Abstract import Abstract

class Pages(Abstract):
    def __init__(self):
        for key in PageSelectors:
            self.RegisterMidiListener(EventInfo(midi.MIDI_NOTEON, midi.PME_System, key, True), self.handlePageChange)

        self.RegisterLEDUpdate(self.UpdatePageLEDs)
    
    def handlePageChange(self, event):
        self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)
        pageIndex = PageSelectors.index(event.data1)
        self.SetPage(pageIndex)
        if not self.isExtension:
            device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))

    def SetPage(self, Value):
        # AP: Close the last known plugin window when moving out of the FX page.
        if self.Page == Page_FX and self.CurPluginID > -1:
            mixer.focusEditor(self.PluginTrack, self.CurPluginID)
            transport.globalTransport(midi.FPT_Escape, 1)

        self.Page = Value
        self.SendMsgToFL(f"Page: {PageNames[Value]}")

        self.FirstTrack = False
        receiverCount = device.dispatchReceiverCount()
        if receiverCount == 0:
            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack])

        self.CurPluginID = -1
        self.CurPluginOffset = 0

        self.UpdateColT()
        self.UpdateLEDs()
        self.UpdateTextDisplay()

    def UpdatePageLEDs(self):
        for m in range(0, 6):
            device.midiOutNewMsg(((PageSelectors[0] + m) << 8) + midi.TranzPort_OffOnT[m == self.Page], 5 + m)

