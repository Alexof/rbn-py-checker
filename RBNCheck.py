# PYTHON REAPER SCRIPT FOR RBN ERROR CHECKING
# Version 1.00
# Alex - 2012-10-30
# This script is inspired on Casto's RBN Script
# This is a porting to Python as Perl support was removed after REAPER 4.13
#
#GUITAR/BASS
#- Expert
#--- LEGACY: No three note chords containing both green and orange (Pending)
#--- LEGACY: No four or more note chords (Pending)
#- Hard
#--- LEGACY: No three note chords (Pending)
#--- LEGACY: No green + orange chords (Pending)
#--- LEGACY: If chord on Expert then chord here (Pending)
#- Medium
#--- LEGACY: No green+blue / green+orange / red+orange chords (Pending)
#--- LEGACY: No forced HOPOs (Pending)
#--- LEGACY: If chord on Expert then chord here (Pending)
#- Easy
#--- LEGACY: No chords (Pending)
#- General
#--- LEGACY: If a color is used on expert, then it must be used on all difficulties (Pending)
#
#DRUMS
#- General
#--- LEGACY: No OD or Rolls in or overlapping drum fills (Pending)
#--- LEGACY: OD starts at end of Fill (Warning) (Pending)
#--- LEGACY: Error if Drum Animation for Toms exist without Pro Markers for them
#--- NEW: Error Non existent gems on expert but in lower difficulties
#- Medium
#--- LEGACY: No kicks with 2 Gems
#- Easy
#--- LEGACY: No Kicks with Gems
#
#VOCALS
#--- LEGACY: Must be space between each note 
#--- LEGACY: Illegal character check: comma, quotation marks
#--- LEGACY: Possible bad character warning: period
#--- LEGACY: First character of phrase capitalization check
#--- LEGACY: Check word after ! or ? is capitalized
#--- LEGACY: Check all mid-phrase capitalization
#
#KEYS (5 Lane)
#- Expert
#--- LEGACY: No four or more note chords
#- Hard
#--- LEGACY: No four or more note chords
#- Medium
#--- LEGACY: No three note chords
#- Easy
#--- LEGACY: No chords
#- General
#--- LEGACY: If a color is used on expert, then it must be used on all difficulties
#
#PRO KEYS 
#- Hard
#--- LEGACY: No four note chords
#- Medium
#--- LEGACY: No three note chords
#- Easy
#--- LEGACY: No chords
#
#EVENTS
#--- LEGACY: Error if not a Text Event or Track Name type
#
#GENERAL
#--- LEGACY: Overdrive unison chart
#--- LEGACY: Error if Keys and Pro Keys ODs aren't exact same
#--- LEGACY: Error if Vocals and Harmony1 ODs aren't exact same.
#

import re
from collections import Counter

# (start) Config section
#CONFIG_FILE = "rbn_config.ini"
#cp = ConfigParser()
#cp.read(CONFIG_FILE)
#OUTPUT_FILE = cp.get("GENERAL", "output_file")
OUTPUT_FILE = 'C:\Users\Alexander\Desktop\myfile.txt'
# (end) Config section

# (start) Class Notas

class Nota(object):
	def __init__(self, valor, pos):
		self.pos = pos
		self.valor = valor

# (end) Class Notas

# (start) Template Dictionary
dTmpl = {}
# (end) Template Dictionary

#These variables control if we have a certain instrument or track
has_drums, has_bass, has_guitar, has_vocals, has_harm1, has_harm2, has_harm3, has_keys = (False, False, False, False, False, False, False, False)
granDICT = {}

# (start) Funciones de manejo de instrumentos
def handle_drums(content):
		drumTmpl = {}
		l_gems = []
		r_gems = []
		has_drums = True
		num_to_text = {
			127 : "Cymbal Sweell", 
      126 : "Drum Roll",
			124 : "Drum Fill Green", 
			123 : "Drum Fill Blue",
			122 : "Drum Fill Yellow",
			121 : "Drum Fill Red", 
			120 : "Drum Fill Orange",
			116 : "Overdrive",
			112 : "Toms Gems Green",
			111 : "Tom Gems Blue", 
			110 : "Toms Gems Yellow",
			103 : "Solo Marker", 
			100 : "Expert Green", 
			99 : "Expert Blue",
			98 : "Expert Yellow", 
			97 : "Expert Red",
			96 : "Expert Kick",
			88 : "Hard Green", 
			87 : "Hard Blue",
			86 : "Hard Yellow", 
			85 : "Hard Red",
			84 : "Hard Kick",
			76 : "Medium Green", 
			75 : "Medium Blue",
			74 : "Medium Yellow", 
			73 : "Medium Red",
			72 : "Medium Kick",
			64 : "Easy Green", 
			63 : "Easy Blue",
			62 : "Easy Yellow", 
			61 : "Easy Red",
			60 : "Easy Kick",
			51 : "Anim. Floort Tom RH", 
			50 : "Anim. Floor Tom LH",
			49 : "Anim. TOM2 RH", 
			48 : "Anim. TOM2 LH",
			47 : "Anim. TOM1 RH",
			46 : "Anim. TOM1 LH", 
			45 : "Anim. SOFT CRASH 2 LH",
			44 : "Anim. CRASH 2 LH", 
			43 : "Anim. RIDE LH",
			42 : "Anim. RIDE CYM RH",
			41 : "Anim. CRASH2 CHOKE", 
			40 : "Anim. CRASH1 CHOKE",
			39 : "Anim. CRASH2 SOFT RH", 
			38 : "Anim. CRASH2 HARD RH",
			37 : "Anim. CRASH1 SOFT RH",
			36 : "Anim. CRASH1 HARD RH", 
			35 : "Anim. CRASH1 SOFT LH",
			34 : "Anim. CRASH1 HARD LH", 
			33 : "Anim. ",
			32 : "Anim. PERCUSSION RH",
			31 : "Anim. HI-HAT RH", 
			30 : "Anim. HI-HAT LH",
			29 : "Anim. SOFT SNARE RH", 
			28 : "Anim. SOFT SNARE LH",
			27 : "Anim. SNARE RH",
			26 : "Anim. SNARE LH", 
			25 : "Anim. HI-HAT OPEN",
			24 : "Anim. KICK RF"
		}
		#debug (content, True)
		#
		all_e_notes = re.findall("^([E,e]\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+)$", content, re.MULTILINE)
		all_x_notes = re.findall("^<(X\s[a-f,0-9]+\s[a-f,0-9]+)$", content, re.I | re.MULTILINE)
		all_notes = all_x_notes + all_e_notes
		noteloc = 0;
		decval="";
		
		for elem in all_notes:
			decval = 0;
			midi_parts = elem.split()
			
			if( midi_parts[0].lower() == 'e' ):
				decval = int( midi_parts[3], 16 )
			
			noteloc = int( noteloc ) + int( midi_parts[1] );			

			#Just parse or debug those notes that are really in the chart
			#we can exclude notes off, text events, etc.
			if( midi_parts[0].lower() == 'e' and re.search("^9", midi_parts[2] ) ):
				l_gems.append( Nota(decval, noteloc) )
				debug("Starts with 9: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				debug( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			elif( midi_parts[0].lower() == 'e' and re.search("^8", midi_parts[2] ) ):			
				r_gems.append( Nota(decval, noteloc) )
				debug("Starts with 8: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				debug( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			else:
				#debug("Text Event: Midi # {}, MBT {}, Type {}, Extra {} ".format( str( decval ), str( noteloc ),str( midi_parts[1] ),str( midi_parts[2] ) ) )
				#debug( "{} at {}".format( "None", format_location( noteloc ) ), True )
				debug("",True)
		#Get all kicks in Easy and check for errors (K+GEM)
		#Also we check for non existent gems on expert
		debug( "", True )
		debug( "=================== EASY DRUMS: Error Kick + Gem ===================", True )
		for notas_item in filter(lambda x: x.valor == 60, l_gems):
			#We got all kicks positions, now we want to seearch if there is any other gem in the same position as the kick
			for notas_item_2 in filter(lambda x: x.pos == notas_item.pos and ( x.valor >=61 and  x.valor <=65) , l_gems):
				if( notas_item_2.valor > 0 ):
					debug( "Found Kick + Gem [ {} ] at {} - ( {},{} )".format( num_to_text[ notas_item_2.valor ], format_location( notas_item.pos ), notas_item_2.valor, notas_item.pos ), True )
					#Colocar aqui una variable o lista con la descripcion del error, 
					#el color / ubicacion midi de la nota y la posicion para asi devolverlo y parsearlo para mostrar HTML
					#debe ser usesr firendly data format para hacer un buen parsing y poder mostarrlo en una tabla,div, etc
		
		debug( "=================== ENDS EASY DRUMS: Error Kick + Gem ===================", True )
		
		#Get all kicks in Medium and check for errors (K + 2 GEM)
		debug( "", True )
		debug( "=================== MEDIUM DRUMS: Error Kick + 2 Gems ===================", True )
		counter_global = Counter()		
		extra_gems_m = Counter()		
		for notas_item in filter(lambda x: x.valor == 72, l_gems):
			#We got all kicks positions, now we want to seearch if there is any other gem in the same position as the kick
			for notas_item_2 in filter(lambda x: x.pos == notas_item.pos and ( x.valor >=73 and  x.valor <=76) , l_gems):
				counter_global[(notas_item.pos)] += 1
				extra_gems_m[ ( notas_item_2.valor, notas_item.pos ) ] += 1
				
			#Do we have more than one gem on top of kicks in this particular position?
			if( counter_global[notas_item.pos] > 1 ):
				gems = filter(lambda (x,y): y == notas_item.pos, extra_gems_m.keys() )
				debug( "Found Kick + 2 Gems [ {} + {} ] at {} - ( {} )".format( num_to_text[ gems[0][0] ], num_to_text[ gems[1][0] ], format_location( notas_item.pos ), notas_item.pos ), True ) 
					
		#debug(str(tempo), True)
		debug( "=================== ENDS MEDIUM DRUMS: Error Kick + 2 Gems ===================", True )
		
		#Get all the gems in expert to compare whats missing in lower difficulties
		all_o_expert = Counter()
		all_r_expert = Counter()
		all_y_expert = Counter()
		all_b_expert = Counter()
		all_g_expert = Counter()
		for notas_item in filter(lambda x: x.valor == 96, l_gems):
			all_o_expert[ notas_item.pos ] = 1
		for notas_item in filter(lambda x: x.valor == 97, l_gems):
			all_r_expert[ notas_item.pos ] = 1
		for notas_item in filter(lambda x: x.valor == 98, l_gems):
			all_y_expert[ notas_item.pos ] = 1
		for notas_item in filter(lambda x: x.valor == 99, l_gems):
			all_b_expert[ notas_item.pos ] = 1
		for notas_item in filter(lambda x: x.valor == 100, l_gems):
			all_g_expert[ notas_item.pos ] = 1
		
		debug( "", True )
		debug( "=================== MISSING GEMS LOWER DIFFICULTIES ===================", True )
		midi_notes = [ [60, 72, 84], [61, 73, 85], [62, 74, 86], [63, 75, 87], [64, 76, 88]]
		#Kicks
		for midi_note in midi_notes[0]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_o_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
		#Snares
		for midi_note in midi_notes[1]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_r_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
		#Yellow (Tom / Hat)
		for midi_note in midi_notes[2]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_y_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
		#Blue (Tom / Cymbal)
		for midi_note in midi_notes[3]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_b_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
		#Green (Tom / Cymbal)
		for midi_note in midi_notes[4]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_b_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
		debug( "=================== ENDS MISSING GEMS LOWER DIFFICULTIES===================", True )
		
		
		debug( "", True )
		debug( "=================== ANIMATION BUT NO PRO MARKER ===================", True )
		all_tom_anim = Counter()
		for notas_item in filter(lambda x: x.valor == 46 or x.valor == 47 or x.valor == 48 or x.valor == 49 or x.valor == 50 or x.valor == 51 , l_gems):
			all_tom_anim[ notas_item.pos ] = 1
			
		for midi_note_pos in all_tom_anim:
			if not( filter(lambda x: ( x.valor in [ 110, 111, 112 ] ) and x.pos == midi_note_pos, l_gems) ):			
				debug( "Tom Marker not found for Drum Animation at {}".format( format_location( midi_note_pos ) ) , True )
		debug( "=================== ENDS ANIMATION BUT NO PRO MARKER ===================", True )
		
		#Get all Drums fills
		debug( "", True )
		debug( "=================== GENERAL DRUMS: Drum Fills ===================", True )
		#c = Counter()		
		for notas_item in filter(lambda x: x.valor >= 120 and x.valor <= 124, l_gems):
			debug( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 		
		debug( "=================== ENDS GENERAL DRUMS: Drum Fills ===================", True )
		
		#Let's calculate some totals
		total_kicks_x = len( filter(lambda x: x.valor == 96, l_gems) )
		total_kicks_h = len( filter(lambda x: x.valor == 84, l_gems) )
		total_kicks_m = len( filter(lambda x: x.valor == 72, l_gems) )
		total_kicks_e = len( filter(lambda x: x.valor == 60, l_gems) )
		debug( "Kicks: X({}) H({}) M({}) E({})".format( total_kicks_x, total_kicks_h, total_kicks_m, total_kicks_e ), True )

		#Save all variable sin DICT for output
		drumTmpl["drums_total_kicks_x"] = total_kicks_x
		drumTmpl["drums_total_kicks_h"] = total_kicks_h
		drumTmpl["drums_total_kicks_m"] = total_kicks_m
		drumTmpl["drums_total_kicks_e"] = total_kicks_e
		
		return drumTmpl

def handle_guitar(content):
		l_gems = []
		r_gems = []
		guitarTmpl = {}
		has_guitar = True
		num_to_text = {
			127 : "TRILL MARKER", 
      126 : "TREMOLO MARKER",
			124 : "BRE", 
			123 : "BRE",
			122 : "BRE",
			121 : "BRE", 
			120 : "BRE",
			116 : "Overdrive",
			103 : "Solo Marker", 
			102 : "Expert Force HOPO Off", 
			101 : "Expert Force HOPO On", 
			100 : "Expert Orange", 
			99 : "Expert Blue",
			98 : "Expert Yellow", 
			97 : "Expert Red",
			96 : "Expert Green",
			90 : "Hard Green", 
			89 : "Force HOPO Off", 
			88 : "Hard Orange", 
			87 : "Hard Blue",
			86 : "Hard Yellow", 
			85 : "Hard Red",
			84 : "Hard Orange",
			76 : "Medium Green", 
			75 : "Medium Blue",
			74 : "Medium Yellow", 
			73 : "Medium Red",
			72 : "Medium Green",
			64 : "Easy Orange", 
			63 : "Easy Blue",
			62 : "Easy Yellow", 
			61 : "Easy Red",
			60 : "Easy Green",
			#40-59 Hand animations
		}
		return guitarTmpl

def handle_bass(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_vocals(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_harm1(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_harm2(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_harm3(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_keys(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_pro_keys_x(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_pro_keys_h(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_pro_keys_m(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_pro_keys_e(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_venue(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def handle_events(content):
		l_gems = []
		guitarTmpl = {}
		return guitarTmpl

def format_location( note_location ):
		return ("{}.{}".format( int ( note_location / 1920 ) + 1 , int (( note_location % 1920) / 480 ) + 1 ))
	
# [resto de las funciones]
# (end) Funciones de manejo de instrumentos

def console_msg(*msg):
  RPR_ShowConsoleMsg(str(msg) + '\n' + '\n')

def debug( output_content, add_new_line=False ):
	if add_new_line: 
		f.write( output_content + '\n')
	else:
		f.write( output_content )
		
	
#Map functions to handlers
switch_map = {"PART DRUMS" : handle_drums,
              "PART GUITAR" : handle_guitar,
							"PART BASS" : handle_bass,
							"PART VOCALS" : handle_vocals,
							"HARM1" : handle_harm1,
							"HARM2" : handle_harm2,
							"HARM3" : handle_harm3,
							"PART KEYS" : handle_keys,
							"PART REAL_KEYS_X" : handle_pro_keys_x,
							"PART REAL_KEYS_H" : handle_pro_keys_h,
							"PART REAL_KEYS_M" : handle_pro_keys_m,
							"PART REAL_KEYS_E" : handle_pro_keys_e,
							"VENUE" : handle_venue,
							"EVENTS" : handle_events}

#Variables 
num_media_items = RPR_CountMediaItems(0)
media_item = 0

#Debug
#console_msg(num_media_items) 
	
#bool = "";
track_content = "";
maxlen = 1048576;  # max num of chars to return
with open(OUTPUT_FILE, 'w') as f:
  for media_item in xrange(0, num_media_items):
		item = RPR_GetMediaItem(0, media_item);
		#bool, item, chunk, maxlen = RPR_GetSetItemState(item, chunk, maxlen);
		results = RPR_GetSetItemState(item, track_content, maxlen)
		#
		track_content = results[2]
		media_item = media_item + 1	
		
		#
		#debug( track_content )
		#
		part = re.findall("^NAME\s+\"(.*)\"$", track_content, re.MULTILINE)
		#part = re.findall("^NAME\s+\"PART\s+(.*)\"$", track_content, re.MULTILINE);
		if part:
			#console_msg( part[0] );			
			func = switch_map.get(part[0], None)
			if func:
				#console_msg("Executing function to handle %s" % part[0])
				fTmpl = func(track_content)
				dTmpl.update(fTmpl)
		
		track_content = ""
		#debug(str(dTmpl))
