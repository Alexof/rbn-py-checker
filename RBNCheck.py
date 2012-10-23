# PYTHON REAPER SCRIPT FOR RBN ERROR CHECKING
# Version 2.05
# Alex - 2012-10-30
# rbn@mirockband.com
# This script is inspired on Casto's RBN Script
# This is a porting to Python as Perl support was removed after REAPER 4.13
# Special thanks to neurogeek for helping with Python learning making all this possible!
# What's new
#--- Ported script to python to support REPAER 4.13+
#--- Improved layout
#--- More info messages
#--- No gems under solo marker (Guitar / Bass)
#--- Non existent gems on lower difficulties based on expert ( Drums)
#
#GUITAR/BASS
#- Expert
#--- LEGACY: No three note chords containing both green and orange
#--- LEGACY: No four or more note chords
#- Hard
#--- LEGACY: No three note chords
#--- LEGACY: No green + orange chords
#--- LEGACY: If chord on Expert then chord here
#- Medium
#--- LEGACY: No green+blue / green+orange / red+orange chords
#--- LEGACY: No forced HOPOs
#--- LEGACY: If chord on Expert then chord here
#- Easy
#--- LEGACY: No chords
#- General
#--- LEGACY: If a color is used on expert, then it must be used on all difficulties
#--- NEW: No gems under solo marker
#
#DRUMS
#- General
#--- LEGACY: No OD or Rolls in or overlapping drum fills
#--- LEGACY: OD starts at end of Fill (Warning)
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
#--- NEW: No gems under solo marker
#
#PRO KEYS 
#- Hard
#--- LEGACY: No four note chords (Pending)
#- Medium
#--- LEGACY: No three note chords (Pending)
#- Easy
#--- LEGACY: No chords (Pending)
#
#EVENTS
#--- LEGACY: Error if not a Text Event or Track Name type (Pending)
#
#GENERAL
#--- LEGACY: Overdrive unison chart (Pending)
#--- LEGACY: Error if Keys and Pro Keys ODs aren't exact same (Pending)
#--- LEGACY: Error if Vocals and Harmony1 ODs aren't exact same. (Pending)
#
import os,re,base64,string,webbrowser
from collections import Counter

# (start) Config section
#CONFIG_FILE = "rbn_config.ini"
#cp = ConfigParser()
#cp.read(CONFIG_FILE)
#OUTPUT_FILE = cp.get("GENERAL", "output_file")
OUTPUT_FILE = 'C:\\rbn-py-checker\\myfile.txt'
OUTPUT_HTML_FILE = 'C:\\rbn-py-checker\\RBN_Output.html'
CONST_DEBUG_EXTRA = False
CONST_DEBUG = False
global_harm2_phase_start = []
global_harm2_phase_end = []
#OUTPUT_FILE = os.path.abspath(os.path.dirname(__file__)) + "/myfile.txt"
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
def handle_drums( content, part_name ):
		drumTmpl = {}
		drumTmpl['drums_kick_gem'] = ''
		drumTmpl['drums_kick_gem_m'] = ''
		drumTmpl['drums_not_found_lower'] = ''
		drumTmpl['drums_tom_marker'] = ''
		drumTmpl['drums_fills_errors'] = ''
		drumTmpl['drums_error_icon'] = ''
		l_gems = []
		r_gems = []
		has_drums = True
		has_error = False
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
				debug("")		
		#Get all kicks in Easy and check for errors (K+GEM)
		#Also we check for non existent gems on expert
		debug( "", True )
		debug( "=================== EASY DRUMS: Error Kick + Gem ===================", True )
		for notas_item in filter(lambda x: x.valor == 60, l_gems):
			#We got all kicks positions, now we want to seearch if there is any other gem in the same position as the kick
			for notas_item_2 in filter(lambda x: x.pos == notas_item.pos and ( x.valor >=61 and  x.valor <=65) , l_gems):
				if( notas_item_2.valor > 0 ):
					debug( "Found Kick + Gem [ {} ] at {} - ( {},{} )".format( num_to_text[ notas_item_2.valor ], format_location( notas_item.pos ), notas_item_2.valor, notas_item.pos ), True )
					drumTmpl['drums_kick_gem'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> Kick + {}</span></div>'.format( format_location( notas_item.pos ), num_to_text[ notas_item_2.valor ] )
					has_error = True
		
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
				
				drumTmpl['drums_kick_gem_m'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> Kick + 2 Gems [ {} + {} ]</span></div>'.format( format_location( notas_item.pos ), num_to_text[ gems[0][0] ]	, num_to_text[ gems[1][0] ] )
				has_error = True
		#debug(str(tempo), True)
		debug( "=================== ENDS MEDIUM DRUMS: Error Kick + 2 Gems ===================", True )
		'''
		debug( "", True )
		debug( "=================== MISSING GEMS LOWER DIFFICULTIES ===================", True )		
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
						
					drumTmpl['drums_not_found_lower'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} not found on Expert</span></div>'.format( format_location( notas_item.pos ),num_to_text[ midi_note ] )
					has_error = True
		#Yellow (Tom / Hat)
		for midi_note in midi_notes[2]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_y_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
					
					drumTmpl['drums_not_found_lower'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} not found on Expert</span></div>'.format( format_location( notas_item.pos ),num_to_text[ midi_note ] )
					has_error = True
		#Blue (Tom / Cymbal)
		for midi_note in midi_notes[3]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_b_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
					
					drumTmpl['drums_not_found_lower'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} not found on Expert</span></div>'.format( format_location( notas_item.pos ),num_to_text[ midi_note ] )
					has_error = True
		#Green (Tom / Cymbal)
		for midi_note in midi_notes[4]:
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_g_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
					
					drumTmpl['drums_not_found_lower'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} not found on Expert</span></div>'.format( format_location( notas_item.pos ),num_to_text[ midi_note ] )
					has_error = True
		debug( "=================== ENDS MISSING GEMS LOWER DIFFICULTIES===================", True )
		'''
		'''
		debug( "", True )
		debug( "=================== ANIMATION BUT NO PRO MARKER ===================", True )
		all_tom_anim = Counter()
		for notas_item in filter(lambda x: x.valor == 46 or x.valor == 47 or x.valor == 48 or x.valor == 49 or x.valor == 50 or x.valor == 51 , l_gems):
			all_tom_anim[ notas_item.pos ] = 1
			
		for midi_note_pos in all_tom_anim:
			if not( filter(lambda x: ( x.valor in [ 110, 111, 112 ] ) and x.pos == midi_note_pos, l_gems) ):			
				debug( "Tom Marker not found for Drum Animation at {}".format( format_location( midi_note_pos ) ) , True )
					
				drumTmpl['drums_tom_marker'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> Tom Marker not found for Drum Animation</span></div>'.format( format_location( midi_note_pos ) )
				has_error = True
		debug( "=================== ENDS ANIMATION BUT NO PRO MARKER ===================", True )
		'''
		#Get all Drums fills
		#We only get orange marker drum fill assuming all five are set
		debug( "", True )
		debug( "=================== GENERAL DRUMS: Drum Fills (OD and Drum Roll Validation) ===================", True )
		fill_start = []
		fill_end = []
		overlap_fill_overdrive = []
		overlap_fill_overdrive_start = []
		overlap_fill_overdrive_end = []
		overlap_fill_drum_roll = []
		#Start notes
		for notas_item in filter(lambda x: x.valor == 120 , l_gems):
			fill_start.append( notas_item.pos )
			debug( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 
		#End notes
		for notas_item in filter(lambda x: x.valor == 120 , r_gems):
			fill_end.append( notas_item.pos )			
			debug( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 		
		#Check for OD and drum rolls inside any DRUM fills
		for midi_check in [116, 126]:
			for index, item in enumerate(fill_start):
				for od_midi_note in filter(lambda x: x.valor == midi_check and ( x.pos >= item and x.pos <= fill_end[index] ), ( r_gems + l_gems )):
					if( midi_check == 116 ):
						#If the od ends right before the drum fill give a warning
						if( od_midi_note.pos == item ):
							overlap_fill_overdrive_start.append( notas_item.pos )
							debug( "WARNING: Found {} ending right before Fill #{} at {} - [ {},{} ] )".format( num_to_text[ od_midi_note.valor ], index+1, format_location( od_midi_note.pos ), od_midi_note.valor, od_midi_note.pos ), True )
					
							drumTmpl['drums_fills_errors'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} ending right before Fill #{}</span></div>'.format( format_location( od_midi_note.pos ), num_to_text[ od_midi_note.valor ], index+1 )
							has_error = True
						#If the od starts right after the drum fill give a warning
						elif( od_midi_note.pos == fill_end[index] ):
							overlap_fill_overdrive_end.append( notas_item.pos )
							debug( "Found {} starting right after in Fill #{} at {} - [ {},{} ] )".format( num_to_text[ od_midi_note.valor ], index+1, format_location( od_midi_note.pos ), od_midi_note.valor, od_midi_note.pos ), True )
					
							drumTmpl['drums_fills_errors'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} starting right after Fill #{}</span></div>'.format( format_location( od_midi_note.pos ), num_to_text[ od_midi_note.valor ], index+1 )
							has_error = True
						#Is a regular overlpa so error message
						else:
							overlap_fill_overdrive.append( notas_item.pos )
							debug( "Found {} overlap in Fill #{} at {} - [ {},{} ] )".format( num_to_text[ od_midi_note.valor ], index+1, format_location( od_midi_note.pos ), od_midi_note.valor, od_midi_note.pos ), True )
					
							drumTmpl['drums_fills_errors'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} overlap in Fill #{}</span></div>'.format( format_location( od_midi_note.pos), num_to_text[ od_midi_note.valor ], index+1 )
							has_error = True
					if( midi_check == 126 ):
						overlap_fill_drum_roll.append( notas_item.pos )
						debug( "Found {} overlap in Fill #{} at {} - [ {},{} ] )".format( num_to_text[ od_midi_note.valor ], index+1, format_location( od_midi_note.pos ), od_midi_note.valor, od_midi_note.pos ), True )
					
						drumTmpl['drums_fills_errors'] += '<div class="row-fluid"><span class="span12"><strong>{}</strong> {} overlap in Fill #{}</span></div>'.format( format_location( od_midi_note.pos) , num_to_text[ od_midi_note.valor ], index+1 )
						has_error = True

				#We only need this to be printed once.. 
				if( midi_check == 116 ):
					debug( "Fill #{} starts at {} ends at {} - [ {},{} ]".format( index+1, format_location( item ), format_location( fill_end[index] ), item, fill_end[index] ) ,True )
		
		
		debug( "=================== ENDS GENERAL DRUMS: Drum Fills (OD and Drum Roll Validation) ===================", True )
		#
		total_kicks_x = len( filter(lambda x: x.valor == 96, l_gems) )
		total_kicks_h = len( filter(lambda x: x.valor == 84, l_gems) )
		total_kicks_m = len( filter(lambda x: x.valor == 72, l_gems) )
		total_kicks_e = len( filter(lambda x: x.valor == 60, l_gems) )
		total_ods 		= len( filter(lambda x: x.valor == 116, l_gems) )
		total_fills 	= len( fill_start )
		#
		debug( "", True )
		debug( "=================== TOTAL DRUMS: Some numbers and stats ===================", True )
		debug( "Kicks: X({}) H({}) M({}) E({})".format( total_kicks_x, total_kicks_h, total_kicks_m, total_kicks_e ), True )
		debug( "Total of Fills: {}".format( total_fills ), True )
		debug( "OD Starts at fill start: {}".format( len( overlap_fill_overdrive_start ) ), True )
		debug( "OD Starts at fill end: {}".format( len( overlap_fill_overdrive_end ) ), True )
		debug( "OD Overlap: {}".format( len( overlap_fill_overdrive ) ), True )
		debug( "Drum Roll Overlap: {}".format( len( overlap_fill_drum_roll ) ), True )
		debug( "Overdrives: {}".format( total_ods ), True )
		debug( "=================== ENDS TOTAL DRUMS: Some numbers and stats ===================", True )
		
		#Save all variable sin DICT for output
		drumTmpl["drums_total_kicks_x"] = total_kicks_x
		drumTmpl["drums_total_kicks_h"] = total_kicks_h
		drumTmpl["drums_total_kicks_m"] = total_kicks_m
		drumTmpl["drums_total_kicks_e"] = total_kicks_e
		drumTmpl["drums_total_fills"] = total_fills
		drumTmpl["drums_total_ods"] = total_ods
		if( has_error ):
			drumTmpl['drums_error_icon'] = '<i class="icon-exclamation-sign"></i>'
		
		return drumTmpl

def handle_guitar(content, part_name ):
		l_gems = []
		r_gems = []
		guitarTmpl, bassTmpl = ( {}, {} )
		if( part_name == "PART GUITAR" ):
			has_guitar = True
		elif( part_name == "PART BASS" ):
			has_bass = True
		output_part_var = part_name.lower().replace( 'part ','' )
		has_error = False
		
		guitarTmpl[ output_part_var + "_green_oranges_three"] = '';
		guitarTmpl[ output_part_var + "_chords_four_notes"] = '';
		guitarTmpl[ output_part_var + "_chords_three_notes"] = '';
		guitarTmpl[ output_part_var + "_chords_dont_exist"] = '';
		guitarTmpl[ output_part_var + "_chords_h_green_orange"] = '';
		guitarTmpl[ output_part_var + "_chords_m_chord_combos"] = '';
		guitarTmpl[ output_part_var + "_chords_m_hopos"] = '';
		guitarTmpl[ output_part_var + "_chords_easy"] = '';
		guitarTmpl[ output_part_var + "_general_issues"] = '';
		guitarTmpl[ output_part_var + "_error_icon"] = ''
			
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
			90 : "Force HOPO Off", 
			89 : "Force HOPO On", 
			88 : "Hard Orange", 
			87 : "Hard Blue",
			86 : "Hard Yellow", 
			85 : "Hard Red",
			84 : "Hard Green",
			78 : "Medium Force HOPO Off", 
			77 : "Medium Force HOPO On", 
			76 : "Medium Orange", 
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
				#debug("Starts with 9: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				#debug( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			elif( midi_parts[0].lower() == 'e' and re.search("^8", midi_parts[2] ) ):			
				r_gems.append( Nota(decval, noteloc) )
				#debug("Starts with 8: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				#debug( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			else:
				#debug("Text Event: Midi # {}, MBT {}, Type {}, Extra {} ".format( str( decval ), str( noteloc ),str( midi_parts[1] ),str( midi_parts[2] ) ) )
				#debug( "{} at {}".format( "None", format_location( noteloc ) ), True )
				debug("")
		#Get three chords containing B+O
		debug( "", True )
		debug( "=================== EXPERT " + part_name + ": 3 chords containing B+O ===================", True )
		counter_positions = Counter() #All positions with 3 gems chord having G+O		
		counter_global = Counter()				
		extra_gems_chords = Counter()
		for notas_item in filter(lambda x: ( x.valor == 97 or x.valor == 98 or x.valor == 99 ) , l_gems):
			#We got all red, yellow and blue notes positions, now we want to seearch if there is any other gem in the same position being ggreen AND orange
			#How many G+O we have?
			if( len( filter(lambda x: x.pos == notas_item.pos and ( x.valor == 96 or x.valor == 100) , l_gems) ) == 2 ):
				extra_gems_chords[ ( notas_item.pos, notas_item.valor ) ] += 1
				if( counter_positions[ notas_item.pos ] < 1 ):
					counter_positions[notas_item.pos] += 1
				debug( "ERROR: Found {} paired with Green and Orange gems at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ), notas_item.valor , notas_item.pos ), True ) 
				
				guitarTmpl[ output_part_var + "_green_oranges_three"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} paired with Green and Orange gems</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ notas_item.valor ])
				has_error = True
		
		#debug(str(extra_gems_chords), True)
		debug( "=================== ENDS " + part_name + ": 3 chords containing B+O ===================", True )
		
		#Get all chords in expert with 4 or more gems
		counter = Counter() #
		counter_4_notes = Counter() #
		counter_internal = 0		
		counter_chord_expert = Counter() #Holds all chords in the expert chart to compare later on		
		debug( "", True )
		debug( "=================== EXPERT " + part_name + ": 4 notes Chords ===================", True )		
		for index, item in enumerate(l_gems):
			if( counter[ item.pos ] < 1 ):
				for midi_note in filter(lambda x: x.pos == item.pos and ( x.valor >= 96 and x.valor <= 100 ), l_gems ):
					debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ midi_note.valor ], format_location( midi_note.pos ), midi_note.valor , midi_note.pos ), True ) 
					counter_internal += 1
				if( counter_internal >=4 ):
					debug( "ERROR: Found 4 notes chord at {} - ( {} )".format( format_location( item.pos ), item.pos ), True )  
				
					guitarTmpl[ output_part_var + "_chords_four_notes"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Found 4 notes chord</span> </span></div>'.format( format_location( item.pos ), num_to_text[ item.valor ])
					has_error = True
				elif(counter_internal >=2):
					counter_chord_expert[ item.pos ] = 1
					debug_extra( "This is a valid chord with {} notes".format(counter_internal), True ) 
				
				counter_internal = 0			
			counter[ item.pos ] = 1
		debug( "=================== EXPERT " + part_name + ": 4 notes Chords ===================", True )
		
		#Get all chords in hard with 3 or more gems
		counter = Counter() #
		counter_internal = 0	
		debug( "", True )
		debug( "=================== HARD " + part_name + ": 3 notes Chords ===================", True )			
		for index, item in enumerate(filter(lambda x: x.valor >= 84 and x.valor <= 88 , l_gems )):
			if( counter[ item.pos ] < 1 ):
				for midi_note in filter(lambda x: x.pos == item.pos and ( x.valor >= 84 and x.valor <= 88 ), l_gems ):
					debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ midi_note.valor ], format_location( midi_note.pos ), midi_note.valor , midi_note.pos ), True ) 
					counter_internal += 1
				if( counter_internal >=3 ):
					debug( "ERROR: Found 3 notes chord at {} - ( {} )".format( format_location( item.pos ), item.pos ), True ) 
				
					guitarTmpl[ output_part_var + "_chords_three_notes"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Found 3 notes chord</span> </span></div>'.format( format_location( item.pos ), num_to_text[ item.valor ])
					has_error = True
				elif(counter_internal <=1):
					debug_extra("Single {} note found at {} - ( {},{} )".format(num_to_text[ item.valor ], format_location( item.pos ), item.valor , item.pos), True)
					if( counter_chord_expert[ item.pos ] > 0 ):
						debug("ERROR: Expert chord not found here at {} - ( {} )".format( format_location( item.pos ), item.pos), True)
				
						guitarTmpl[ output_part_var + "_chords_dont_exist"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Expert chord not found on hard</span> </span></div>'.format( format_location( item.pos ), num_to_text[ item.valor ])
						has_error = True
					
				counter_internal = 0			
			counter[ item.pos ] = 1
		debug( "=================== ENDS HARD " + part_name + ": 3 notes Chords ===================", True )
		
		#No green + orange chords
		counter = Counter() #
		counter_internal = 0	
		debug( "", True )
		debug( "=================== HARD " + part_name + ": Green + Orange chords ===================", True )			
		for index, item in enumerate(l_gems):
			if( counter[ item.pos ] < 1 ):
				for midi_note in filter(lambda x: x.pos == item.pos and ( x.valor == 84 or x.valor == 88 ), l_gems ):
					debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ midi_note.valor ], format_location( midi_note.pos ), midi_note.valor , midi_note.pos ), True ) 
					counter_internal += 1
				if( counter_internal >=2 ):
					debug( "ERROR: Found Green and Orange chord at {} - ( {} )".format( format_location( item.pos ), item.pos ), True )
				
					guitarTmpl[ output_part_var + "_chords_h_green_orange"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Green and Orange chord not allowed</span> </span></div>'.format( format_location( item.pos ))
					has_error = True 
				
				counter_internal = 0			
			counter[ item.pos ] = 1
		debug( "=================== ENDS HARD " + part_name + ": Green + Orange chords ===================", True )
		
		#No green+blue / green+orange / red+orange chords
		midi_notes = [ [72, 75], [72, 76], [73, 76] ]
		chord_combination = [ 'Green + Blue','Green + Orange','Red + Orange' ]
		debug( "", True )
		debug( "=================== MEDIUM " + part_name + ": green+blue / green+orange / red+orange chords ===================", True )		
		for idx_notes, item_note in enumerate(midi_notes):
			counter = Counter() #
			counter_internal = 0			
			for index, item in enumerate(l_gems):
				if( counter[ item.pos ] < 1 ):
					for midi_note in filter(lambda x: x.pos == item.pos and ( x.valor == item_note[0] or x.valor == item_note[1] ), l_gems ):
						debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ midi_note.valor ], format_location( midi_note.pos ), midi_note.valor , midi_note.pos ), True ) 
						counter_internal += 1
					if( counter_internal >=2 ):
						debug( "ERROR: Found {} chord at {} - ( {} )".format( chord_combination[ idx_notes ], format_location( item.pos ), item.pos ), True ) 
				
						guitarTmpl[ output_part_var + "_chords_m_chord_combos"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} chord not allowed</span> </span></div>'.format( format_location( item.pos ),  chord_combination[ idx_notes ] ) 
						has_error = True
					
					counter_internal = 0			
				counter[ item.pos ] = 1
		debug( "=================== ENDS MEDIUM " + part_name + ": green+blue / green+orange / red+orange chords ===================", True )
		
		#No forced hopos
		counter = Counter() #
		counter_internal = 0	
		debug( "", True )
		debug( "=================== MEDIUM " + part_name + ": No Force hopos ===================", True )			
		#for index, item in enumerate(l_gems):
		for midi_note in filter(lambda x: x.valor == 77 or x.valor == 78 , l_gems ):
			debug( "ERROR: Found {} at {} - ( {} )".format( num_to_text[ midi_note.valor ], format_location( midi_note.pos ), midi_note.pos ), True ) 
				
			guitarTmpl[ output_part_var + "_chords_m_hopos"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Forced hopos not allowed</span> </span></div>'.format( format_location( item.pos ) )
			has_error = True
		debug( "=================== ENDS MEDIUM " + part_name + ": No Force hopos ===================", True )			
		
		#No expert chords in medium
		counter = Counter() #
		counter_internal = 0	
		debug( "", True )
		debug( "=================== MEDIUM " + part_name + ": No expert chords ===================", True )			
		for item in counter_chord_expert:
			if( len(filter(lambda x: x.pos == item and ( x.valor >= 72 and x.valor <= 76 ), l_gems )) == 1 ):
				debug("Expert chord not found here at {} - ( {} )".format( format_location( item ), item), True)
				
				guitarTmpl[ output_part_var + "_chords_dont_exist"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Expert chord not found on medium</span> </span></div>'.format( format_location( item ) )
				has_error = True
		debug( "=================== ENDS MEDIUM " + part_name + ": No expert chords ===================", True )				
		
		#No chords allowed in easy
		counter = Counter()
		gems_in_chord = Counter()
		debug( "", True )
		debug( "=================== EASY " + part_name + ": No Chords ===================", True )
		for notas_item in filter(lambda x: x.valor >= 60 and x.valor <= 64, l_gems):
			debug_extra( "Found {} at {} - ( {}, {}): ".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ), notas_item.valor , notas_item.pos ), True ) 
			counter_global[(notas_item.pos)] += 1
			gems_in_chord[ ( notas_item.pos, notas_item.valor ) ] += 1
		debug_extra("Validating chords....", True)
		#Do we have more than one gem on top of kicks in this particular position?
		for (a, b) in enumerate(counter_global):			
			if( counter_global[b]>1 ):
				gems_text = ''
				for x, v in filter(lambda (x,y): x == b, gems_in_chord.keys() ):
					gems_text = gems_text + num_to_text[ v ] + " + "
				debug( "ERROR: Found {} chord at {} - ( {} )".format( gems_text[:-3], format_location( b ), b ), True )
				
				guitarTmpl[ output_part_var + "_chords_easy"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} chord not allowed</span> </span></div>'.format( format_location( b ), gems_text[:-3] ) 	
				has_error = True
		counter_chord_easy = filter(lambda (x,y): y >= 2, counter_global.iteritems())

		debug( "=================== ENDS EASY " + part_name + ": No Chords ===================", True )
		
		#No gems under solo marker
		solo_start = []
		solo_end = []
		counter = Counter()
		gems_in_solo = Counter()
		debug( "", True )
		debug( "=================== GENERAL " + part_name + ": No gems under solo marker ===================", True )
		#Start notes
		for notas_item in filter(lambda x: x.valor == 103 , l_gems):
			solo_start.append( notas_item.pos )
			debug_extra( "Found start {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 
		#End notes
		for notas_item in filter(lambda x: x.valor == 103 , r_gems):
			solo_end.append( notas_item.pos )			
			debug_extra( "Found end {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True )		
		#Check for any gem under solo marker... we need at least one gem for the solo to be valid
		#for midi_check in [60,61,62,63,64,72,73,74,75,76,84,85,86,87,88,96,97,98,99,100]:			
		for index, item in enumerate(solo_start):
			gems_text = '';
			if ( filter(lambda x: x.valor >=60 and x.valor <=64 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Easy + '
			if ( filter(lambda x: x.valor >=72 and x.valor <=76 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Medium + '
			if ( filter(lambda x: x.valor >=84 and x.valor <=88 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Hard + '
			if ( filter(lambda x: x.valor >=96 and x.valor <=100 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Expert + '
			
			debug( "INFO: Solo Marker #{} starts at {} ends at {} - [ {},{} ]".format( index+1, format_location( item ), format_location( solo_end[index] ), item, solo_end[index] ) ,True )
			
			if( counter[ item ] < 4 ):
				debug( "ERROR: Gems are missing from at least one difficulty at Solo Marker #{}. Only found {} gems".format( index+1, gems_text[:-3] ) ,True )				
				guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>Gems are missing from at least one difficulty at Solo Marker #{}. Only found {} gems</span> </span></div>'.format( index+1, gems_text[:-3] )
				has_error = True
		debug( "=================== ENDS GENERAL " + part_name + ": No gems under solo marker ===================", True )
		
		debug( "", True )
		debug( "=================== GENERAL " + part_name + ": NO MATCHING GEMS ON EXPERT / ALL NODES BEING USED ===================", True )
		#Get all the gems in expert to compare whats missing in lower difficulties
		'''
		has_o, has_b, has_y, has_r, has_g = (False,False,False,False,False) 
		all_g_expert = Counter()
		all_r_expert = Counter()
		all_y_expert = Counter()
		all_b_expert = Counter()
		all_o_expert = Counter()
		for notas_item in filter(lambda x: x.valor == 96, l_gems):
			all_g_expert[ notas_item.pos ] = 1
			has_g = True
		for notas_item in filter(lambda x: x.valor == 97, l_gems):
			all_r_expert[ notas_item.pos ] = 1
			has_r = True
		for notas_item in filter(lambda x: x.valor == 98, l_gems):
			all_y_expert[ notas_item.pos ] = 1
			has_y = True
		for notas_item in filter(lambda x: x.valor == 99, l_gems):
			all_b_expert[ notas_item.pos ] = 1
			has_b = True
		for notas_item in filter(lambda x: x.valor == 100, l_gems):
			all_o_expert[ notas_item.pos ] = 1
			has_o = True		
		midi_notes = [ [60, 72, 84], [61, 73, 85], [62, 74, 86], [63, 75, 87], [64, 76, 88]]	
		#Green
		for midi_note in midi_notes[0]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				counter += 1
				if not ( all_g_expert[ notas_item.pos ] ):
					debug( "ERROR: {} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] ) 
					has_error = True
			if( counter < 1 and has_g):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Red
		for midi_note in midi_notes[1]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_r_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_r):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Yellow
		for midi_note in midi_notes[2]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_y_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_y):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Blue
		for midi_note in midi_notes[3]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_b_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_b):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Orange
		for midi_note in midi_notes[4]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_o_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_o):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				guitarTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		debug( "=================== ENDS GENERAL " + part_name + ": NO MATCHING GEMS ON EXPERT / ALL NODES BEING USED ===================", True )
		'''
		#Some totals
		total_ods = len( filter(lambda x: x.valor == 116, l_gems) )
		debug( "", True )
		debug( "=================== TOTAL " + part_name + ": Some numbers and stats ===================", True )
		debug( "Three notes including G+O gems: {}".format( len( counter_positions ) ), True )
		debug( "Expert Four notes chords: {}".format( len( counter_4_notes ) ), True )
		debug( "Four notes chords: {}".format( len( counter_4_notes ) ), True )
		debug( "Total Solo Markers: {}".format( len( solo_start ) ), True )
		debug( "Total ODs: {}".format( total_ods ), True )
		debug( "=================== ENDS TOTAL " + part_name + ": Some numbers and stats ===================", True )		
		
		guitarTmpl[ output_part_var + "_total_ods"] = total_ods
		if( has_error ):
			guitarTmpl[ output_part_var + '_error_icon'] = '<i class="icon-exclamation-sign"></i>'
		
		return guitarTmpl

def handle_vocals(content, part_name ):
		l_gems = []
		r_gems = []
		p_gems = []
		vocalsTmpl,harm1Tmpl,harm2vTmpl,harm3Tmpl  = ( {},{},{},{} )
		has_vocals = True
		has_error = False
		
		output_part_var = part_name.lower().replace( 'part ','' )		
		vocalsTmpl[ output_part_var + "_phrases" ] = ''
		vocalsTmpl[ output_part_var + "_general_issues" ] = ''
		vocalsTmpl[ output_part_var + "_error_icon"] = ''
		
		num_to_text = {
			116: "Overdrive",
			105: "Phrase Marker",
			97:	"Non-Displayed Percussion",
			96:	"Displayed Percussion",
			83:	"Highest Note B5",
			82:	"A#4",
			81:	"A4",
			80:	"G#4",
			79:	"G4",
			78:	"F#4",
			77:	"F4",
			76:	"E4",
			75:	"D#4",
			74:	"D4",
			73:	"C#4",
			72:	"C4",
			71:	"B3",
			70:	"A#3",
			69:	"A3",
			68:	"G#3",
			67:	"G3",
			66:	"F#3",
			65:	"F3",
			64:	"E3",
			63:	"D#3",
			62:	"D3",
			61:	"C#3",
			60:	"C3",
			59:	"B2",
			58:	"A#2",
			57:	"A2",
			56:	"G#2",
			55:	"G2",
			54:	"F#2",
			53:	"F2",
			52:	"E2",
			51:	"D#2",
			50:	"D2",
			49:	"C#2",
			48:	"C2",
			47:	"B1",
			46:	"A#1",
			45:	"A1",
			44:	"G#1",
			43:	"G1",
			42:	"F#1",
			41:	"F1",
			40:	"E1",
			39:	"D#1",
			38:	"D1",
			37:	"C#1",
			36:	"Lowest Note C1",
			1:	"Lyric Shift",
			0:	"Range Shift"
		}
		#debug (content, True)
		#
		#all_e_notes = re.findall("^([E,e]\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+)$", content, re.MULTILINE)
		#all_x_notes = re.findall("^<(X\s[a-f,0-9]+\s[a-f,0-9]+)$", content, re.I | re.MULTILINE)
		all_f_notes = content.split('\n')
		all_notes = []
		for elem in all_f_notes:		
			if( re.match("^([E,e]\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+)$", elem) or re.match("^<(X\s[a-f,0-9]+\s[a-f,0-9]+)$", elem) ):
				all_notes.append( elem )
		all_l_notes = re.findall("^\/(.*)$", content, re.I | re.MULTILINE)
		noteloc = 0;
		decval="";
		c = []
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
				debug_extra("Starts with 9: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				debug( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			elif( midi_parts[0].lower() == 'e' and re.search("^8", midi_parts[2] ) ):			
				r_gems.append( Nota(decval, noteloc) )
				c.append(noteloc)
				debug_extra("Starts with 8: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				debug( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			else:
				p_gems.append( Nota(decval, noteloc) )
				debug_extra("Text Event: Midi # {}, MBT {}, Type {}, Extra {} ".format( str( decval ), str( noteloc ),str( midi_parts[1] ),str( midi_parts[2] ) ) )
				debug( "Text Event found at {}".format( format_location( noteloc ) ), True )
				
		lyric_positions = Counter()
		for index, item in enumerate(all_l_notes):
			debug_extra("Index {}: Encoded: {} || Decoded: {} at {} ( {} )".format(index, item, base64.b64decode( '/' + item )[2:],format_location( p_gems[index].pos ), p_gems[index].pos ), True)
			lyric_positions[ p_gems[index].pos ] = base64.b64decode( '/' + item )[2:]
		#Get all Phrase Markers
		debug( "", True )
		debug( "=================== " + part_name + ": Phrase Markers and lyrics ===================", True )
		phrase_start = []
		phrase_end = []
		#Start notes
		for notas_item in filter(lambda x: x.valor == 105 , l_gems):
			phrase_start.append( notas_item.pos )
			#We need the global for harm2 so we can use for HARM3
			if( part_name == "HARM2" ):
				global_harm2_phase_start.append( notas_item.pos )
			debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 
		#End notes
		for notas_item in filter(lambda x: x.valor == 105 , r_gems):
			phrase_end.append( notas_item.pos )
			#We need the global for harm2 so we can use for HARM3
			if( part_name == "HARM2" ):
				global_harm2_phase_end.append( notas_item.pos )			
			debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 		
		#If we are looping HARM3 we assume we dont have any phrase marker, we take HARM2 markers as baaseline
		if( part_name == "HARM3" ):
			phrase_start = global_harm2_phase_start
			phrase_end = global_harm2_phase_end
		#
		reserved_words = ['[play]','[mellow]','[intense]','[idle]']
		punctuation = ['?','!']
		warning_characters = ['.']
		warning_characters_error = ['period/dot']
		special_characters = [',','�','’','"']
		special_characters_error = ['comma','smart apostrophe','smart apostrophe','quotes']
		remove_words = string.maketrans("#^","  ")
		check_caps = False
		last_note = 0
		#For each phrase marker we find the lyrics
		for index, item in enumerate(phrase_start):
			full_phrase = ''
			output_full_phrase = ''
			debug_extra( "Phrase Marker #{} starts at {} ends at {} - [ {},{} ]".format( index+1, format_location( item ), format_location( phrase_end[index] ), item, phrase_end[index] ) ,True )
			for od_midi_note in filter(lambda x: x.pos >= item and x.pos <= phrase_end[index] , p_gems):			
				
				if lyric_positions[ od_midi_note.pos ] not in reserved_words:
					if( last_note == od_midi_note.pos ):
						debug_extra("Here {} {}".format(last_note, item), True)					
					
					debug_extra("Syllable {} found at {}".format(lyric_positions[ od_midi_note.pos ], od_midi_note.pos), True)
					debug_extra("Last characeter is {}".format(lyric_positions[ od_midi_note.pos ][-1:] ), True)
					if lyric_positions[ od_midi_note.pos ] != '+':
						syllable = lyric_positions[ od_midi_note.pos ] + ' '
						if( lyric_positions[ od_midi_note.pos ][-1:] == '-' ):
							syllable = lyric_positions[ od_midi_note.pos ][:-1] + ''
						if( lyric_positions[ od_midi_note.pos ][-1:] == '=' ):
							syllable = lyric_positions[ od_midi_note.pos ][:-1] + '- '
						
						#At this stage the output is the same as the syllable
						output_syllable = syllable
						
						#Check syllable for special characters
						for index_char, special_char in enumerate(special_characters):
							if( syllable.find( special_char )!=-1 ):
								debug("ERROR: Found {} in syllable {} at {}".format( special_characters_error[ index_char ], syllable.strip(), format_location( od_midi_note.pos ) ), True)
								output_syllable = '<span class="alert-error" title="Found {} in syllable"><strong>{}</strong></span>'.format( special_characters_error[ index_char ], syllable.strip() )
								has_error = True
						#Check syllable for warning characaters
						for index_char, special_char in enumerate(warning_characters):
							if( syllable.find( special_char )!=-1 ):
								debug("WARNING: Found {} in syllable {} at {}".format( warning_characters_error[ index_char ], syllable.strip(), format_location( od_midi_note.pos ) ), True)
								output_syllable = '<span class="alert-error" title="{} in syllable"><strong>{}</strong></span>'.format( warning_characters_error[ index_char ], syllable.strip() )
								has_error = True
						#Is the syllable upper case? This is not valid!	
						if( full_phrase != '' and syllable[0].isupper() ):
							debug("ERROR: syllable \"{}\" should not be uppercase at {} - [{}, {}]".format(syllable.translate( remove_words ).strip(),  format_location( od_midi_note.pos ),  item,  od_midi_note.pos ), True)						
							output_syllable = '<span class="alert-info" title="Should not be uppercase"><strong>{}</strong></span>'.format( syllable.translate( remove_words ).strip() )
							has_error = True
						elif( ( full_phrase == '' or check_caps == True ) and not syllable[0].isupper() ):
							check_caps = False
							debug("ERROR: syllable \"{}\" should be uppercase at {} - [{}, {}]".format(syllable.translate( remove_words ).strip(),  format_location( od_midi_note.pos ),  item,  od_midi_note.pos ), True)							
							output_syllable = '<span class="alert-error" title="Should be uppercase"><strong>{}</strong></span>'.format( syllable.translate( remove_words ).strip() )
							has_error = True
						full_phrase += syllable + ''
						output_full_phrase += output_syllable + ''
					
					if lyric_positions[ od_midi_note.pos ][-1:] in punctuation:
						debug_extra("Word after \"{}\" needs to be checked for uppercase letter".format( syllable.strip() ), True)
						check_caps = True
					last_note = item
			#Print full phrase
			debug("INFO: Phrase #{} from {} to {}: {}".format(index+1, format_location( item ),format_location( phrase_end[index] ), re.sub(r'\s+', ' ', full_phrase.translate( remove_words )) ), True)
			vocalsTmpl[ output_part_var + "_phrases"] += '<div class="row-fluid"><strong class="">{}</strong>: {} </div>'.format( format_location( item ), output_full_phrase.translate( remove_words ) )
		debug( "=================== ENDS " + part_name + ": Phrase markers and lyrics ===================", True )
		
		#Get all ODs
		debug( "", True )
		debug( "=================== " + part_name + ": ODs ===================", True )
		od_start = []
		od_end = []
		#Start notes
		for notas_item in filter(lambda x: x.valor == 116 , l_gems):
			od_start.append( notas_item.pos )
			debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 
		#End notes
		for notas_item in filter(lambda x: x.valor == 116 , r_gems):
			od_end.append( notas_item.pos )			
			debug_extra( "Found {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 
		#For od marker we do ....
		for index, item in enumerate(od_start):
			#Print
			debug("INFO: Overdrive #{} from {} to {}".format(index+1, format_location( item ),format_location( od_end[index] ) ), True)
		debug( "=================== ENDS " + part_name + ": ODs ===================", True )
		
		#Get notes without space
		debug( "", True )
		debug( "=================== " + part_name + ": Notes without space ===================", True )
		#Start notes
		for notas_item in l_gems:
			for notas_item_2 in filter(lambda x: x.pos == notas_item.pos , r_gems):
				debug("ERROR: Note {} starting at {} needs at least 2 64ths note gap between notes".format( num_to_text[ notas_item_2.valor ], format_location( notas_item_2.pos ) ), True)
				
				vocalsTmpl[ output_part_var + "_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Note {} needs at least 2 64ths note gap between notes</span> </span></div>'.format( format_location( notas_item_2.pos ), num_to_text[ notas_item_2.valor ] )
				
				has_error = True
			
		debug( "=================== ENDS " + part_name + ": Notes without space ===================", True )
		
		#Save all variable sin DICT for output
		vocalsTmpl[ output_part_var + "_od_start"] = od_start
		vocalsTmpl[ output_part_var + "_od_end"] = od_end
		if( has_error ):
			vocalsTmpl[ output_part_var + '_error_icon'] = '<i class="icon-exclamation-sign"></i>'
		
		return vocalsTmpl

def handle_keys(content, part_name ):
		l_gems = []
		r_gems = []
		localTmpl = {}
		has_keys = True
		has_error = False
		localTmpl["keys_error_icon"] = ''		
		localTmpl[ "keys_general_issues"] = '';
		localTmpl[ "keys_chords_four_notes"] = '';
		localTmpl[ "keys_chords_three_notes"] = '';
		localTmpl[ "keys_chords_easy"] = '';
		localTmpl[ "keys_gems_not_found"] = '';
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
			90 : "Force HOPO Off", 
			89 : "Force HOPO On", 
			88 : "Hard Orange", 
			87 : "Hard Blue",
			86 : "Hard Yellow", 
			85 : "Hard Red",
			84 : "Hard Green",
			78 : "Medium Force HOPO Off", 
			77 : "Medium Force HOPO On", 
			76 : "Medium Orange", 
			75 : "Medium Blue",
			74 : "Medium Yellow", 
			73 : "Medium Red",
			72 : "Medium Green",
			64 : "Easy Orange", 
			63 : "Easy Blue",
			62 : "Easy Yellow", 
			61 : "Easy Red",
			60 : "Easy Green"
		}
		#debug (content, True)
		#
		all_e_notes = re.findall("^([E,e]\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+)$", content, re.MULTILINE)
		all_x_notes = re.findall("^<(X\s[a-f,0-9]+\s[a-f,0-9]+)$", content, re.I | re.MULTILINE)
				
		#all_notes = all_x_notes + all_e_notes
		all_notes = re.findall("(?:^<(X\\s[a-f,0-9]+\\s[a-f,0-9]+)$|^([E,e]\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+\s[a-f,0-9]+)$)", content, re.MULTILINE)
		noteloc = 0;
		decval="";
		
		for note in all_notes:
			decval = 0;
			
			x, e = note			
			if x:
				elem = x
			elif e:
				elem = e
				
			midi_parts = elem.split()
			
			if( midi_parts[0].lower() == 'e' ):
				decval = int( midi_parts[3], 16 )
			
			noteloc = int( noteloc ) + int( midi_parts[1] );			

			#Just parse or debug those notes that are really in the chart
			#we can exclude notes off, text events, etc.
			if( midi_parts[0].lower() == 'e' and re.search("^9", midi_parts[2] ) ):
				l_gems.append( Nota(decval, noteloc) )
				debug_extra("Starts with 9: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				debug_extra( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			elif( midi_parts[0].lower() == 'e' and re.search("^8", midi_parts[2] ) ):			
				r_gems.append( Nota(decval, noteloc) )
				debug_extra("Starts with 8: Midi # {}, MBT {}, Type {} ".format( str( decval ), str( noteloc ),str( midi_parts[2] ) ) )
				debug_extra( "{} at {}".format( num_to_text[decval], format_location( noteloc ) ), True )
			else:
				debug_extra("Text Event: Midi # {}, MBT {}, Type {}, Extra {} ".format( str( decval ), str( noteloc ),str( midi_parts[1] ),str( midi_parts[2] ) ) )
				debug_extra( "{} at {}".format( "None", format_location( noteloc ) ), True )
				debug_extra("")
		
		# Get all valid number of chords per track
		midi_notes = [ [96, 100], [84, 88], [72, 76], [60, 64] ]
		midi_notes_text = [ 'EXPERT', 'HARD', 'MEDIUM', 'EASY' ]
		midi_notes_max = [ 3, 3, 2, 1 ]
		midi_notes_output_var = [ 'keys_chords_four_notes', 'keys_chords_four_notes', 'keys_chords_four_notes', 'keys_chords_easy' ]
		for idx_notes, item_note in enumerate(midi_notes):
			debug( "", True )
			debug( "=================== " + midi_notes_text[ idx_notes ] + " KEYS: " + str( midi_notes_max[ idx_notes ] ) + " notes Chords ===================", True )
			counter = Counter() #
			counter_internal = 0	
			counter_global = Counter()
			gems_in_chord = Counter()
			for notas_item in filter(lambda x: x.valor >= item_note[0] and x.valor <= item_note[1], l_gems):
				debug_extra( "Found {} at {} - ( {}, {}): ".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ), notas_item.valor , notas_item.pos ), True ) 
				counter_global[(notas_item.pos)] += 1
				gems_in_chord[ ( notas_item.pos, notas_item.valor ) ] += 1
			debug_extra("Validating chords....", True)
			#Do we have chords?
			for (a, b) in enumerate(counter_global):			
				if( counter_global[b]>midi_notes_max[ idx_notes ] ):
					gems_text = ''
					for x, v in filter(lambda (x,y): x == b, gems_in_chord.keys() ):
						gems_text = gems_text + num_to_text[ v ] + " + "
					debug( "ERROR: Found {} chord at {} - ( {} )".format( gems_text[:-3], format_location( b ), b ), True )
					
					localTmpl[ midi_notes_output_var[ idx_notes ] ] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} chord not allowed</span> </span></div>'.format( format_location( b ), gems_text[:-3] )
					has_error = True
			counter_chord_easy = filter(lambda (x,y): y >= 2, counter_global.iteritems())
			debug( "=================== ENDS " + midi_notes_text[ idx_notes ] + " KEYS: " + str( midi_notes_max[ idx_notes ] ) + " notes Chords ===================", True )
		
		#No gems under solo marker
		solo_start = []
		solo_end = []
		counter = Counter()
		gems_in_solo = Counter()
		debug( "", True )
		debug( "=================== GENERAL KEYS: No gems under solo marker ===================", True )
		#Start notes
		for notas_item in filter(lambda x: x.valor == 103 , l_gems):
			solo_start.append( notas_item.pos )
			debug_extra( "Found start {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True ) 
		#End notes
		for notas_item in filter(lambda x: x.valor == 103 , r_gems):
			solo_end.append( notas_item.pos )			
			debug_extra( "Found end {} at {} - ( {}, {} )".format( num_to_text[ notas_item.valor ], format_location( notas_item.pos ),notas_item.valor, notas_item.pos ), True )		
		#Check for any gem under solo marker... we need at least one gem for the solo to be valid
		#for midi_check in [60,61,62,63,64,72,73,74,75,76,84,85,86,87,88,96,97,98,99,100]:			
		for index, item in enumerate(solo_start):
			gems_text = '';
			if ( filter(lambda x: x.valor >=60 and x.valor <=64 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Easy + '
			if ( filter(lambda x: x.valor >=72 and x.valor <=76 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Medium + '
			if ( filter(lambda x: x.valor >=84 and x.valor <=88 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Hard + '
			if ( filter(lambda x: x.valor >=96 and x.valor <=100 and x.pos >= item and x.pos <= solo_end[index], l_gems) ):
				counter[ item ] += 1
				gems_text += 'Expert + '
			
			debug( "INFO: Solo Marker #{} starts at {} ends at {} - [ {},{} ]".format( index+1, format_location( item ), format_location( solo_end[index] ), item, solo_end[index] ) ,True )
			
			if( counter[ item ] < 4 ):
				debug( "ERROR: Gems are missing from at least one difficulty at Solo Marker #{}. Only found {} gems".format( index+1, gems_text[:-3] ) ,True )				
				localTmpl[ "keys_general_issues"] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>Gems are missing from at least one difficulty at Solo Marker #{}. Only found {} gems</span> </span></div>'.format( format_location( item ), index+1, gems_text[:-3] )
				has_error = True
		debug( "=================== ENDS GENERAL KEYS: No gems under solo marker ===================", True )
		'''
		debug( "", True )
		debug( "=================== GENERAL KEYS: NO MATCHING GEMS ON EXPERT / ALL NODES BEING USED ===================", True )
		#Get all the gems in expert to compare whats missing in lower difficulties
		has_o, has_b, has_y, has_r, has_g = (False,False,False,False,False) 
		all_g_expert = Counter()
		all_r_expert = Counter()
		all_y_expert = Counter()
		all_b_expert = Counter()
		all_o_expert = Counter()
		for notas_item in filter(lambda x: x.valor == 96, l_gems):
			all_g_expert[ notas_item.pos ] = 1
			has_g = True
		for notas_item in filter(lambda x: x.valor == 97, l_gems):
			all_r_expert[ notas_item.pos ] = 1
			has_r = True
		for notas_item in filter(lambda x: x.valor == 98, l_gems):
			all_y_expert[ notas_item.pos ] = 1
			has_y = True
		for notas_item in filter(lambda x: x.valor == 99, l_gems):
			all_b_expert[ notas_item.pos ] = 1
			has_b = True
		for notas_item in filter(lambda x: x.valor == 100, l_gems):
			all_o_expert[ notas_item.pos ] = 1
			has_o = True		
		midi_notes = [ [60, 72, 84], [61, 73, 85], [62, 74, 86], [63, 75, 87], [64, 76, 88]]	
		#Green
		for midi_note in midi_notes[0]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				counter += 1
				if not ( all_g_expert[ notas_item.pos ] ):
					debug( "ERROR: {} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					localTmpl[ "keys_gems_not_found" ] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] ) 
					has_error = True
			if( counter < 1 and has_g):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				localTmpl[ "keys_general_issues" ] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Red
		for midi_note in midi_notes[1]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_r_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					localTmpl[ "keys_gems_not_found" ] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_r):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				localTmpl[ "keys_general_issues" ] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Yellow
		for midi_note in midi_notes[2]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_y_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					localTmpl[ "keys_gems_not_found" ] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_y):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				localTmpl[ "keys_general_issues" ] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Blue
		for midi_note in midi_notes[3]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_b_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					localTmpl[  "keys_gems_not_found" ] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_b):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				localTmpl[  "keys_general_issues" ] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		#Orange
		for midi_note in midi_notes[4]:
			counter = 0		
			for notas_item in filter(lambda x: x.valor == midi_note, l_gems):
				if not ( all_o_expert[ notas_item.pos ] ):
					debug( "{} not found on Expert at {}".format( num_to_text[ midi_note ], format_location( notas_item.pos ) ) , True )
				
					localTmpl[  "keys_gems_not_found" ] += '<div class="row-fluid"><span class="span12"><strong class="">{}</strong> <span>{} not found on Expert</span> </span></div>'.format( format_location( notas_item.pos ), num_to_text[ midi_note ] )
			if( counter < 1 and has_o):
				debug( "ERROR: No {} gems not found, must use all nodes used in expert".format( num_to_text[ midi_note ] ) , True )
				
				localTmpl[ "keys_general_issues" ] += '<div class="row-fluid"><span class="span12"><strong class="">0.0</strong> <span>{} gems not found, must use all nodes used in expert</span> </span></div>'.format( num_to_text[ midi_note ] )
				has_error = True
		debug( "=================== ENDS GENERAL KEYS: NO MATCHING GEMS ON EXPERT / ALL NODES BEING USED ===================", True )
		'''
		#Some totals
		total_ods = len( filter(lambda x: x.valor == 116, l_gems) )
		debug( "", True )
		debug( "=================== TOTAL KEYS: Some numbers and stats ===================", True )
		debug( "Total Solo Markers: {}".format( len( solo_start ) ), True )
		debug( "Total ODs: {}".format( total_ods ), True )
		debug( "=================== ENDS TOTAL KEYS: Some numbers and stats ===================", True )		
		
		localTmpl[ "keys_total_ods"] = total_ods
		if( has_error ):
			localTmpl[ 'keys_error_icon'] = '<i class="icon-exclamation-sign"></i>'
		
		return localTmpl

def handle_pro_keys_x(content, part_name ):
		l_gems = []
		localTmpl = {}
		has_error = False
		localTmpl["pro_error_icon"] = ''
		return localTmpl

def handle_pro_keys_h(content, part_name ):
		l_gems = []
		localTmpl = {}
		has_error = False
		localTmpl["pro_error_icon"] = ''
		return localTmpl

def handle_pro_keys_m(content, part_name ):
		l_gems = []
		localTmpl = {}
		has_error = False
		localTmpl["pro_error_icon"] = ''
		return localTmpl

def handle_pro_keys_e(content, part_name ):
		l_gems = []
		localTmpl = {}
		has_error = False
		localTmpl["pro_error_icon"] = ''
		return localTmpl

def handle_venue(content, part_name ):
		l_gems = []
		localTmpl = {}
		has_error = False
		localTmpl["venue_error_icon"] = ''
		return localTmpl

def handle_events(content, part_name ):
		l_gems = []
		localTmpl = {}
		has_error = False
		localTmpl["events_error_icon"] = ''
		return localTmpl

def format_location( note_location ):
		return ("{}.{}".format( int ( note_location / 1920 ) + 1 , int (( note_location % 1920) / 480 ) + 1 ))
	
# [resto de las funciones]
# (end) Funciones de manejo de instrumentos

def console_msg(*msg):
  RPR_ShowConsoleMsg(str(msg) + '\n' + '\n')

def debug( output_content, add_new_line=False ):
	global CONST_DEBUG
	if( CONST_DEBUG_EXTRA ):
		if add_new_line: 
			f.write( output_content + '\n')
		else:
			f.write( output_content )

def debug_extra( output_content, add_new_line=False ):
	global CONST_DEBUG_EXTRA
	if( CONST_DEBUG_EXTRA ):
		if add_new_line: 
			f.write( "DEBUG: " + output_content + '\n')
		else:
			f.write( "DEBUG: " + output_content )

def debug_html( output_content, add_new_line=False ):		
	f.write( output_content )
#Map functions to handlers
switch_map = {"PART DRUMS" : handle_drums,
              "PART GUITAR" : handle_guitar,
							"PART BASS" : handle_guitar,
							"PART VOCALS" : handle_vocals,
							"HARM1" : handle_vocals,
							"HARM2" : handle_vocals,
							"HARM3" : handle_vocals,
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
				debug("########################### Executing function to handle %s #################################" % part[0] , True)
				fTmpl = func( track_content, part[0] )
				dTmpl.update(fTmpl)
		
		track_content = ""
		
with open(OUTPUT_HTML_FILE, 'w') as f:
	
	var_html = '''
<!DOCTYPE html>
<html lang="en">
<HEAD>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<!-- Le styles -->
	<link href="css/bootstrap.css" rel="stylesheet">
	<style type="text/css">
		body {
			padding-top: 60px;
			padding-bottom: 40px;
		}
		.sidebar-nav {
			padding: 9px 0;
		}
	</style>
	<link href="css/bootstrap-responsive.css" rel="stylesheet">		
</HEAD>
<body>
	<div class="container-fluid">
	
		<div class="row-fluid">
			<div class="span2">
				<h3>At a glance</h3>
				<div class="well sidebar-nav">
					<ul class="nav nav-list">
						<li class="nav-header">Drums</li>
						<li class=""><a href="#">OD Count: ''' + "{}".format( dTmpl['drums_total_ods'] ) + '''</a></li>
						<li class=""><a href="#">Fill Count: ''' + "{}".format( dTmpl['drums_total_fills'] ) + '''</a></li>
						<li class=""><a href="#">Kicks on X: ''' + "{}".format( dTmpl['drums_total_kicks_x'] ) + '''</a></li>
						<li class=""><a href="#">Kicks on H: ''' + "{}".format( dTmpl['drums_total_kicks_h'] ) + '''</a></li>
						<li class=""><a href="#">Kicks on M: ''' + "{}".format( dTmpl['drums_total_kicks_m'] ) + '''</a></li>
						<li class=""><a href="#">Kicks on E: ''' + "{}".format( dTmpl['drums_total_kicks_e'] ) + '''</a></li>
						<li class="nav-header">Bass</li>
						<li class=""><a href="#">OD Count: ''' + "{}".format( dTmpl['bass_total_ods'] ) + '''</a></li>
						<li class="nav-header">Guitar</li>
						<li class=""><a href="#">OD Count: ''' + "{}".format( dTmpl['guitar_total_ods'] ) + '''</a></li>
						<li class="nav-header">Keys</li>
						<li class=""><a href="#">OD Count:  ''' + "{}".format( dTmpl['keys_total_ods'] ) + '''</a></li>
						<li class="nav-header">PRO Keys</li>
						<li class=""><a href="#">OD Count: </a></li>
						<li class="nav-header">Vocals / Harmonies</li>
						<li class=""><a href="#">Vocals OD Count: ''' + str( len( dTmpl['vocals_od_start'] ) ) + '''</a></li>
						<li class=""><a href="#">Harmony 1 OD Count: ''' + str( len( dTmpl['harm1_od_start'] ) ) + '''</a></li>
					</ul>
				</div><!--/.well -->
			</div><!--/span-->
			<div class="span9">
				<div class="tabbable">
					<ul class="nav nav-tabs">
						<li class="active"><a href="#tab_drums" data-toggle="tab">Drums ''' + dTmpl['drums_error_icon'] + '''</a></li>
						<li><a href="#tab_bass" data-toggle="tab">Bass ''' + dTmpl['bass_error_icon'] + '''</a></li>
						<li><a href="#tab_guitar" data-toggle="tab">Guitar ''' + dTmpl['guitar_error_icon'] + '''</a></li>
						<li><a href="#tab_prokeys" data-toggle="tab">PRO Keys ''' + dTmpl['pro_error_icon'] + '''</a></li>
						<li><a href="#tab_keys" data-toggle="tab">Keys ''' + dTmpl['keys_error_icon'] + '''</a></li>
						<li><a href="#tab_vocals" data-toggle="tab">Vocals ''' + dTmpl['vocals_error_icon'] + '''</a></li>
						<li><a href="#tab_harm1" data-toggle="tab">Harm 1 ''' + dTmpl['harm1_error_icon'] + '''</a></li>
						<li><a href="#tab_harm2" data-toggle="tab">Harm 2 ''' + dTmpl['harm2_error_icon'] + '''</a></li>
						<li><a href="#tab_harm3" data-toggle="tab">Harm 3 ''' + dTmpl['harm3_error_icon'] + '''</a></li>
						<li><a href="#tab_events" data-toggle="tab">Events ''' + dTmpl['events_error_icon'] + '''</a></li>
						<li><a href="#tab_venue" data-toggle="tab">Venue ''' + dTmpl['venue_error_icon'] + '''</a></li>
						<li><a href="#tab_od" data-toggle="tab">OD Graph</a></li>
					</ul>
					<div class="tab-content">
						<div class="tab-pane active" id="tab_drums">
							<div class="span12">'''
	if( dTmpl['drums_kick_gem'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Easy Kick + Gem</h3>
									<div>''' + "{}".format( dTmpl['drums_kick_gem'] ) + '''</div>
								</div>'''
	if( dTmpl['drums_kick_gem_m'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Medium Kick + 2 Gems</h3>
									<div>''' + "{}".format( dTmpl['drums_kick_gem_m'] ) + '''</div>
								</div>'''	
	if( dTmpl['drums_not_found_lower'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Lower Difficulties</h3>
									<div>''' + "{}".format( dTmpl['drums_not_found_lower'] ) + '''</div>
								</div>'''	
	if( dTmpl['drums_tom_marker'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Tom Markers</h3>
									<div>''' + "{}".format( dTmpl['drums_tom_marker'] ) + '''</div>
								</div>'''	
	if( dTmpl['drums_fills_errors'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Drum Fills Issues</h3>
									<div>''' + "{}".format( dTmpl['drums_fills_errors'] ) + '''</div>
								</div>'''	
	var_html += '''
							</div>
						</div>
						<div class="tab-pane" id="tab_bass">
							<div class="span12">'''
	if( dTmpl['bass_green_oranges_three'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Gem + G + O</h3>
									<div>''' + "{}".format( dTmpl['bass_green_oranges_three'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_four_notes'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">4 Notes chords</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_four_notes'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_three_notes'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">3 Notes chords on Hard</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_three_notes'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_dont_exist'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Non Existent chords on Lower Dif</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_dont_exist'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_h_green_orange'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Green + Orange chords on Hard</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_h_green_orange'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_m_chord_combos'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">G+B / G+O / R+O chords on Medium</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_m_chord_combos'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_m_hopos'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Forced hopos on Medium</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_m_hopos'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_chords_easy'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Easy chords</h3>
									<div>''' + "{}".format( dTmpl['bass_chords_easy'] ) + '''</div>
								</div>'''
	if( dTmpl['bass_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Errors / Warnings</h3>
									<div>''' + "{}".format( dTmpl['bass_general_issues'] ) + '''</div>
								</div>'''
	var_html += '''
							</div>
						</div>
						<div class="tab-pane" id="tab_guitar">
							<div class="span12">'''
	if( dTmpl['guitar_green_oranges_three'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Gem + G + O</h3>
									<div>''' + "{}".format( dTmpl['guitar_green_oranges_three'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_four_notes'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">4 Notes chords</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_four_notes'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_three_notes'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">3 Notes chords on Hard</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_three_notes'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_dont_exist'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Non Existent chords on Lower Dif</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_dont_exist'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_h_green_orange'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Green + Orange chords on Hard</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_h_green_orange'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_m_chord_combos'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">G+B / G+O / R+O chords on Medium</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_m_chord_combos'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_m_hopos'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Forced hopos on Medium</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_m_hopos'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_chords_easy'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Easy chords</h3>
									<div>''' + "{}".format( dTmpl['guitar_chords_easy'] ) + '''</div>
								</div>'''
	if( dTmpl['guitar_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Errors / Warnings</h3>
									<div>''' + "{}".format( dTmpl['guitar_general_issues'] ) + '''</div>
								</div>'''
							
	var_html += '''</div>
						
						</div>
						<div class="tab-pane" id="tab_prokeys">
							<div class="span12">
							
							</div>
						
						</div>
						<div class="tab-pane" id="tab_keys">
							<div class="span12"> '''
	if( dTmpl['keys_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Issues</h3>
									<div>''' + "{}".format( dTmpl['keys_general_issues'] ) + '''</div>
								</div>'''
	if( dTmpl['keys_gems_not_found'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Lower dif gems not found on Expert</h3>
									<div>''' + "{}".format( dTmpl['keys_gems_not_found'] ) + '''</div>
								</div>'''
	if( dTmpl['keys_chords_four_notes'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">4 notes chords</h3>
									<div>''' + "{}".format( dTmpl['keys_chords_four_notes'] ) + '''</div>
								</div>'''
	if( dTmpl['keys_chords_three_notes'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">3 notes chords on Medium</h3>
									<div>''' + "{}".format( dTmpl['keys_chords_three_notes'] ) + '''</div>
								</div>'''
	if( dTmpl['keys_chords_easy'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">Chord on easy</h3>
									<div>''' + "{}".format( dTmpl['keys_chords_easy'] ) + '''</div>
								</div>'''
	var_html += '''							
							</div>
						
						</div>
						<div class="tab-pane" id="tab_vocals">
							<div class="span12">'''
							
	if( len( dTmpl['vocals_od_start'] ) != len( dTmpl['harm1_od_start'] ) ):
		var_html += '''
							<div class="alert alert-error">
								<h3>Vocals Errors</h3>
								<div>- Numbers of Overdrives in Vocals(''' + str( len( dTmpl['vocals_od_start'] ) ) + ''') are different than HARM1(''' + str( len( dTmpl['harm1_od_start'] ) ) + ''')</div>
							</div>
		'''
	else:
		for index, item in enumerate( dTmpl['vocals_od_start'] ):
			if( item != dTmpl['harm1_od_start'][index] or dTmpl['vocals_od_end'][index] != dTmpl['harm1_od_end'][index] ):
				var_html += '''
							<div class="alert alert-error">
								<h3>Vocals Errors (Overdrive)</h3>
								<div>
									''' + "- Overdrive #{} in VOCALS [ Starts: {}, Ends: {} ] starts or ends in a different place than HARM1 [ Starts: {}, Ends: {} ]".format( index+1, format_location( item ), format_location( dTmpl['vocals_od_end'][index] ), format_location( dTmpl['harm1_od_start'][index] ), format_location( dTmpl['harm1_od_end'][index] ) ) + '''
								</div>
							</div>
				'''	
	if( dTmpl['vocals_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Issues</h3>
									<div>''' + "{}".format( dTmpl['vocals_general_issues'] ) + '''</div>
								</div>'''
	var_html += '''
								<h3 class="alert alert-info">Lyrics</h3>
								''' +( dTmpl['vocals_phrases'] )+'''
							</div>
						</div>
						<div class="tab-pane" id="tab_harm1">
							<div class="span12"> '''
	if( dTmpl['harm1_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Issues</h3>
									<div>''' + "{}".format( dTmpl['harm1_general_issues'] ) + '''</div>
								</div>'''
	var_html += '''
								<h3 class="alert alert-info">Lyrics</h3>
									''' +( dTmpl['harm1_phrases'] )+'''
							</div>
						
						</div>
						<div class="tab-pane" id="tab_harm2">
							<div class="span12"> '''
	if( dTmpl['harm2_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Issues</h3>
									<div>''' + "{}".format( dTmpl['harm2_general_issues'] ) + '''</div>
								</div>'''
	var_html += '''
							<h3 class="alert alert-info">Lyrics</h3>
								''' +( dTmpl['harm2_phrases'] )+'''
							</div>
						
						</div>
						<div class="tab-pane" id="tab_harm3">
							<div class="span12"> '''
	if( dTmpl['harm3_general_issues'] != '' ):
		var_html += '''
								<div>
									<h3 class="alert alert-error">General Issues</h3>
									<div>''' + "{}".format( dTmpl['harm3_general_issues'] ) + '''</div>
								</div>'''
	var_html += '''
							<h3 class="alert alert-info">Lyrics</h3>
								''' +( dTmpl['harm3_phrases'] )+'''
							</div>
						
						</div>
						<div class="tab-pane" id="tab_events">
						
						</div>
						<div class="tab-pane" id="tab_venue">
						
						</div>
						<div class="tab-pane" id="tab_od">
						
						</div>
					</div>
				</div>
			</div>
	</div><!--/.fluid-container-->	
	<!-- Le javascript
	================================================== -->
	<!-- Placed at the end of the document so the pages load faster -->
	<script type="text/javascript" src="http://platform.twitter.com/widgets.js"></script>
	<script src="js/jquery.js"></script>
	<script src="js/google-code-prettify/prettify.js"></script>
	<script src="js/bootstrap-transition.js"></script>
	<script src="js/bootstrap-alert.js"></script>
	<script src="js/bootstrap-modal.js"></script>
	<script src="js/bootstrap-dropdown.js"></script>
	<script src="js/bootstrap-scrollspy.js"></script>
	<script src="js/bootstrap-tab.js"></script>
	<script src="js/bootstrap-tooltip.js"></script>
	<script src="js/bootstrap-popover.js"></script>
	<script src="js/bootstrap-button.js"></script>
	<script src="js/bootstrap-collapse.js"></script>
	<script src="js/bootstrap-carousel.js"></script>
	<script src="js/bootstrap-typeahead.js"></script>
	<script src="js/application.js"></script>		
  </body>
</html>
'''
	debug_html(str(var_html))
webbrowser.open( OUTPUT_HTML_FILE )