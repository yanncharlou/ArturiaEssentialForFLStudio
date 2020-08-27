# name=Arturia Essential Controller

# FL-Studio official documentation : https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm#startStopConst
# Thread about Arturia Sysex : https://forum.arturia.com/index.php?topic=90496.0

# Work when Arturia Keyboard is set on DAW Map.

#TODO
"""
Some things to check in future :
use all buttons
ui.setHintMsg("Message")
showing messages on arturia led screen ?
"""

import transport
import mixer
import ui
import midi
import general
import device

button_pressed = 127
button_released = 0

#buttons msg codes
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
	"LEFT": 98,
	"RIGHT" : 99,
}

#leds codes (0 -> 127)
leds = {

	"CAT_CHAR": 22,
	"PRESET": 23,

	"LEFT": 24,
	"RIGHT": 25,

	"NEXT": 26,
	"PREV": 27,
	"BANK": 28,

	"PAD1_BLUE": 32, #or 112, 120
	"PAD1_GREEN": 33, 
	"PAD1_RED": 34,

	"PAD2_BLUE": 35, #or 113, 121
	"PAD2_GREEN": 36,
	"PAD2_RED": 37,

	"PAD3_BLUE": 38, #or 114, 122
	"PAD3_GREEN": 39, 
	"PAD3_RED": 40,

	"PAD4_BLUE": 41, #or 115, 123
	"PAD4_GREEN": 42,
	"PAD4_RED": 43,

	"PAD5_BLUE": 44, #or 116, 124
	"PAD5_GREEN": 45,
	"PAD5_RED": 46,

	"PAD6_BLUE": 47, #or 117, 125
	"PAD6_GREEN": 48,
	"PAD6_RED": 49,

	"PAD7_BLUE": 50, #or 117, 126
	"PAD7_GREEN": 51,
	"PAD7_RED": 52,

	"PAD8_BLUE": 53, #or 118, 127
	"PAD8_GREEN": 54,
	"PAD8_RED": 55,

	"CHORD" : 56, #or 18
	"TRANS" : 57, #or 19
	"OCT-" : 58, #or 16
	"OCT+" : 59, #or 17
	"MAP_SELECT" : 60, #or 21
	"MIDI_CHANNEL" : 61, #or 20

	"SAVE": 86, #or 62
	"UNDO": 87, #or 63
	"PUNCH": 88,
	"METRO": 89, #or 29
	"LOOP": 90,
	"REW": 91,
	"FFW": 92, #or 30
	"STOP" : 93,
	"PLAY_PAUSE": 94,
	"REC": 95, #or 31
}


class ArturiaKeylabEssentialCtrl():

	currentTestedLed = 0

	def OnMidiSysEx(self, event):
		print('SysEx:', event.data1, event.data2)

	def OnMidiMsg(self, event):

		#Don't pass anything even if not handled.
		event.handled = True 
		
		if self.pressed(event,'SAVE') :
			transport.globalTransport(midi.FPT_Save, 92)
		
		elif self.pressed(event,'UNDO') :
			general.undoUp()
		
		elif self.pressed(event,'PUNCH') :
			event.handled = True
			#TODO
			transport.globalTransport(midi.FPT_PunchIn, 31)
			print('PUNCH !')
		
		elif self.pressed(event,'METRO') :
			transport.globalTransport(midi.FPT_Metronome, 110)
			
		elif self.pressed(event,'LOOP') :
			transport.setLoopMode()
		
		elif event.data1 == buttons['REW'] :
			if event.data2 == button_pressed :
				transport.rewind(2); #SS_Start	
				self.setLed('LOOP', True);				
			else :
				transport.rewind(0); #SS_Stop
				self.setLed('LOOP', False)
				
		elif event.data1 == buttons['FFW'] :
			if event.data2 == button_pressed :
				transport.fastForward(2); #SS_Start
			else :
				transport.fastForward(0); #SS_Stop				


		elif self.pressed(event,'STOP') :
			transport.stop()
		
		elif self.pressed(event,'PLAY_PAUSE') :
			transport.globalTransport(midi.FPT_Play, 10)

		elif self.pressed(event,'REC') :
			transport.globalTransport(midi.FPT_Record, 12)


	def pressed(self, event, buttonName) :
		return event.data1 ==  buttons[buttonName] and event.data2 == button_pressed

	def sendPayload(self, payload) :
		#ARTURIA SysEX format :
		#F0 00 20 6B 7F 42 PAYLOAD F7
		device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]) + payload + bytes([0xF7]))

	#Simple set led on / off by ledname
	def setLed(self, ledName, on) :
		if on :
			self.setLedValByID(leds[ledName], 127)
		else :
			self.setLedValByID(leds[ledName], 0)

	#Simple set led value by ledname
	def setLedVal(self, ledName, value) :
		self.setLedValByID(leds[ledName], value)

	def setLedValByID(self, ctrlId, value) :		
		self.sendPayload(bytes([ 0x02, 0x00, 0x10, 0x00, 0x00, ctrlId, value]))

	def OnUpdateBeatIndicator(self, val):
		#off = 0, bar = 1 (on), beat = 2 (on)
		if general.getUseMetronome() :
			if val == 0 :
				arturiaCtrl.setLedVal('METRO',0)
			elif val == 1 :
				arturiaCtrl.setLedVal('METRO',60)
			elif val == 2 :
				arturiaCtrl.setLedVal('METRO',10)

	#Used to check msgs received
	def OnMidiMsgShowCode(self, event) :
		print('MSG:', event.data1, event.data2)

	#Use to check Led codes.
	# <- and -> button to try each codes between 0 and 127
	def OnMidiMsgLedTest(self, event) :

		global currentTestedLed 

		if self.pressed(event,'LEFT') :
			self.setLedValByID(self.currentTestedLed, 0)
			self.currentTestedLed = self.currentTestedLed - 1
			self.setLedValByID(self.currentTestedLed, 127)
			print('LED:', self.currentTestedLed)

		elif self.pressed(event,'RIGHT') :
			self.setLedValByID(self.currentTestedLed, 0)
			self.currentTestedLed = self.currentTestedLed + 1
			self.setLedValByID(self.currentTestedLed, 127)
			print('LED:', self.currentTestedLed)

	def refreshStatusLeds(self):
		self.setLed('PLAY_PAUSE', transport.isPlaying())
		self.setLed('LOOP', transport.getLoopMode())
		self.setLed('REC', transport.isRecording())
		

arturiaCtrl = ArturiaKeylabEssentialCtrl()

def OnMidiMsg(event):
	arturiaCtrl.OnMidiMsg(event) #normal mode
	#arturiaCtrl.OnMidiMsgShowCode(event) #msg test mode
	#arturiaCtrl.OnMidiMsgLedTest(event) #led test mode

def OnMidiSysEx(event):
	arturiaCtrl.OnMidiSysEx(event)

def OnProgramChange(event):
	print('PROGRAM CHANGE:', event.data1, event.data2)

def OnRefresh(val):
	arturiaCtrl.refreshStatusLeds()

def OnUpdateBeatIndicator(val):
	arturiaCtrl.OnUpdateBeatIndicator(val)
