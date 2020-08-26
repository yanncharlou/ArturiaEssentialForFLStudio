# name=Arturia Essential Controller

# Doc officielle FL-Studio : https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm#startStopConst
# Arturia Sysex : https://forum.arturia.com/index.php?topic=90496.0
# Exemple intéressant : https://github.com/soundwrightpro/FLNI_KK/blob/master/Native%20Instruments/device_Komplete_Kontrol_DAW.py

import transport
import mixer
import ui
import midi
import general
import device

button_pressed = 127;
button_released = 0;

buttons = {
    "SAVE": 80,
	"UNDO": 81,
	"PUNCH": 87, #88 too
	"METRO": 89, 
	"LOOP": 86,
	"REW": 91,
	"FFW": 92,
	"STOP" : 93,
	"PLAY_PAUSE": 94,
	"REC": 95,
}

leds = {
	"LOOP": 0x5A,
	
}

#TODO
"""
self.UpdateLEDs()
ui.setHintMsg("Song / pattern mode")
"""

class TSimple():

	def OnMidiSysEx(self, event):
		print('SysEx:', event.data1, event.data2)

	def OnMidiMsg(self, event):
		#This only controller msg. Don't pass anything if not handled.
		event.handled = True;
		
		#save pressed (pressed 0 / released 127)
		#if event.data1 == buttons['SAVE'] and event.data2 == button_pressed :
		if self.pressed(event,'SAVE') :
			transport.globalTransport(midi.FPT_Save, 92);
			print('SAVE !');
		
		elif self.pressed(event,'UNDO') :
			general.undoUp();
		
		elif self.pressed(event,'PUNCH') :
			event.handled = True
			#TODO
			#TEST
			#self.setLed('LOOP', True);
			#transport.globalTransport(midi.FPT_Punch, 30)
			
			print('PUNCH !');
		
		elif self.pressed(event,'METRO') :
			transport.globalTransport(midi.FPT_Metronome, 110)
			#self.UpdateLEDs()
			ui.setHintMsg("Metronome")
		
		elif self.pressed(event,'LOOP') :
			transport.setLoopMode();
		
		elif event.data1 == buttons['REW'] :
			if event.data2 == button_pressed :
				transport.rewind(2); #SS_Start	
				self.setLed('LOOP', True);				
			else :
				transport.rewind(0); #SS_Stop
				self.setLed('LOOP', False);
				
		elif event.data1 == buttons['FFW'] :
			if event.data2 == button_pressed :
				transport.fastForward(2); #SS_Start
			else :
				transport.fastForward(0); #SS_Stop				


		elif self.pressed(event,'STOP') :
			transport.stop();
		
		elif self.pressed(event,'PLAY_PAUSE') :
			transport.globalTransport(midi.FPT_Play, 10)

		elif self.pressed(event,'REC') :
			transport.globalTransport(midi.FPT_Record, 12)
		
		else :
			#event.handled = False
			print('MSG:', event.data1, event.data2)

	def pressed(self, event, buttonName) :
		return event.data1 ==  buttons[buttonName] and event.data2 == button_pressed
	
	#def updateLeds(self) :
		#TODO
		#debice.midiOutSysex(

	def sendPayload(self, payload) :
		#F0 00 20 6B 7F 42 PAYLOAD F7
		device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]) + payload + bytes([0xF7]))
		#print("Payload:", bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42, payload, 0xF7]))

	def setLed(self, ctrlName, on) :
		#record : 0x5A
		ctrlId = leds[ctrlName]
		if on :
			onOffCode = 0x7F
		else :
			onOffCode = 0x00
		
		self.sendPayload(bytes([ 0x02, 0x00, 0x10, 0x00, 0x00, ctrlId, onOffCode]))

Simple = TSimple()

def OnMidiMsg(event):
	Simple.OnMidiMsg(event)

def OnMidiSysEx(event):
	Simple.OnMidiSysEx(event)
