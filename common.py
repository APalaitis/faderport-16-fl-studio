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

class TMackieCU_Base():
    #############################################################################################################################
    #                                                                                                                           #
    # Display shortened name to fit to 7 characters (e.g., Fruity Chorus = FChorus, EQ Enhancer = EQEnhan)                      #
    #                                                                                                                           #
    #############################################################################################################################

    def DisplayName(self,name):
        print('DisplayName')

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
    #  UPDATE BUTTON LEDS                                                                                                       #
    #                                                                                                                           #
    #############################################################################################################################

    def UpdateLEDs(self):
        print('UpdateLEDs')


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
