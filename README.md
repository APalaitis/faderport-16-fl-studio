# faderport-16-fl-studio
## PreSonus Faderport 16 script for FL Studio integration script

* Script version: 0.3.0
* Faderport 16 firmware version: 3.74

Designed to be used with the **Studio One mode** in Faderport. You can switch modes by holding the Select buttons of the first two fader strips while powering on.

# Button list

## Left side strip
* ARM - Toggles the arming mode. Track strip *Select* buttons are red when the arming mode is on. Click on individual *Select* buttons to arm those tracks for recording.
* Solo Clear - Removes solo from all the mixer tracks.
* Mute Clear - Unmutes all the mixer tracks.
* Bypass/All - Turn off effects on the current mixer track.
* Macro/Open - N/A
* Link/Lock - Toggle link mode. While in link mode, move any fader to assign the last tweaked control to that fader (Note: only works in the **User Links Page**). Pressing while holding shift will unlink last tweaked control.

## Mixer track strips
* Select - Selects/focuses a mixer track. Some pages may assign other functionality to this button. *Shift*+*Select* will reset the fader to the default value (where applicable).
* **M**ute - Toggles mute on a mixer track.
* **S**olo - Toggles solo on a mixer track.

## Right side strip
* Track/Timecode - Switch to the **Volume Page** (default). Faders control mixer track volume.
* Edit Plugins - Switch to the **FX Page**. Faders control dry/wet mix on a selected track's effect slots. Clicking *Select* will allow controlling parameters of the selected plugin with the faders.
* Sends - Switch to the **Sends Page**. Faders control send volume from the currently selected mixer track. Clicking *Select* toggles sending to a particular track.
* Pan - Switch to the **Panning Page**. Faders control mixer track panning.
* Audio/Inputs - Toggle/focus the mixer.
* VI/MIDI - Toggle/focus the channel rack.
* Bus/Outputs - Toogle/focus the playlist.
* VCA/FX - Toggle/focus the piano roll.
* All/User - Toggle/focus the browser.

## Top right
* Latch/Save - Save the project.
* Trim/Redo - Redo.
* Off/Undo - Undo.
* Touch/User 1 - Switch to the **Stereo Width Page**. Faders control mixer track stereo width.
* Write/User 2 - Switch to the **EQ Page**. Faders control mixer track EQ bands.
* Read/User 3 - Switch to the **User Links Page**. Faders can be linked to any parameters by the user.

## Encoder modes
* Channel/F1 - Encoder controls individual channel scrolling. Navigation buttons adjust the currently visible fader bank on the FaderPort by one bank of sixteen channels.
* Zoom/F2 - Encoder controls horizontal zooming. Navigation buttons control vertical zooming.
* Scroll/F3 - N/A
* Bank/F4 - N/A
* Master/F5 - Encoder controls the Master level. Push the encoder to reset the Master level to 0 dB. While in this mode, the navigation buttons will control banking.
* Click/F6 - Toggles the metronome.
* Section/F7 - N/A
* Marker/F8 - Encoder moves the playback position marker in the timeline. Use the navigation buttons to scroll through markers. Press the encoder to drop a marker.

## Transport controls
* Loop mode - Toggles between song mode and pattern mode.
* Rewind & fast-forward - Jogs the play position marker left or right a bar.
* Stop - Stops playback.
* Play - Starts playback.
* Record - Toggles record mode.

# To Do

## Bugs
* Sends page - if send to # is not active, set the fader to 0.
* EQ page - the middle band controls are missing.

## Features
* Find use for unused buttons.
* Utilize SHIFT for extra features.
* Possibility to enable some sort of control of the playlist and channel rack? Need investigating.