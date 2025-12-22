import zipfile
import xml.etree.ElementTree as ET
import io
from typing import List, Dict, Optional
from models.song_model import Song, Track, Measure, Beat, Note, NoteType, EffectType, NoteEffect
from parser.gp_parser import GPParser

class XmlParser(GPParser):
    def parse_file(self, file_path: str) -> Song:
        with open(file_path, 'rb') as f:
            content = f.read()
        return self.parse_bytes(content)

    def parse_bytes(self, file_content: bytes) -> Song:
        with zipfile.ZipFile(io.BytesIO(file_content)) as z:
            filenames = z.namelist()
            score_file = None
            if 'score.gpif' in filenames:
                score_file = 'score.gpif'
            elif 'Content/score.gpif' in filenames:
                score_file = 'Content/score.gpif'
            
            if not score_file:
                raise ValueError("Invalid GPX/GP file: score.gpif not found")
            
            with z.open(score_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                return self._parse_xml(root)

    def _parse_xml(self, root: ET.Element) -> Song:
        # Check Namespace
        ns_match = root.tag.split('}')
        ns = ''
        if len(ns_match) > 1:
            ns = ns_match[0] + '}'
        
        def _ft(elem, tag):
            return elem.findtext(f"{ns}{tag}")

        def _get_ref_list(elem, tag):
            txt = _ft(elem, tag)
            return txt.split() if txt else []
        
        # Helpers
        def find_child(parent, tag):
            return parent.find(f"{ns}{tag}")
            
        def findall_child(parent, tag):
            return parent.findall(f"{ns}{tag}")
        
        song = Song()
        
        # Metadata
        title = _ft(root, 'Title') or "Untitled"
        artist = _ft(root, 'Artist') or "Unknown"
        song.title = title
        song.artist = artist
        
        # Build Typed ID map for fast lookup
        # { TagName : { id : Element } }
        id_map = {}
        for elem in root.iter():
            eid = elem.get('id')
            if eid is not None:
                # Use local tag name (remove namespace) for key
                tag_local = elem.tag.split('}')[-1]
                if tag_local not in id_map:
                    id_map[tag_local] = {}
                id_map[tag_local][str(eid)] = elem
                
        def get_elem(tag_suffix, eid):
            # tag_suffix should be the local tag name e.g. 'Track'
            return id_map.get(tag_suffix, {}).get(str(eid))

        # Parse Rhythms
        rhythm_map = self._parse_rhythms(root, ns)
        
        # Parse MasterTrack (Tempo)
        master_track = find_child(root, 'MasterTrack')
        if master_track:
            automations = find_child(master_track, 'Automations')
            if automations:
                for auto in findall_child(automations, 'Automation'):
                    type_elem = find_child(auto, 'Type')
                    if type_elem is not None and type_elem.text == 'Tempo':
                        val_str = _ft(auto, 'Value')
                        if val_str:
                            try:
                                bpm = int(val_str.split()[0])
                                song.tempo = bpm
                            except:
                                pass
                                
        # Parse Tracks
        track_ids = []
        if master_track is not None:
             track_ids = [int(tid) for tid in _get_ref_list(master_track, 'Tracks')]
            
        tracks_by_id = {}
        for i, tid in enumerate(track_ids):
            # Lookup specific typed element
            track_elem = get_elem('Track', tid)
            if not track_elem: continue
            
            name = _ft(track_elem, 'Name') or f"Track {i+1}"
            
            # Program/Channel
            program = 0
            is_percussion = False
            
            # Check for generic MIDI property or instrument set
            sounds = find_child(track_elem, 'Sounds')
            if sounds:
                sound = find_child(sounds, 'Sound')
                if sound:
                    midi_node = find_child(sound, 'MIDI')
                    if midi_node:
                        p_str = _ft(midi_node, 'Program')
                        if p_str: program = int(p_str)
            
            inst_set = find_child(track_elem, 'InstrumentSet')
            if inst_set and _ft(inst_set, 'Type') == 'drumKit':
                is_percussion = True

            # Tuning
            tuning = []
            properties = find_child(track_elem, 'Properties')
            if properties:
                for p in findall_child(properties, 'Property'):
                    if p.get('name') == 'Tuning':
                        pitches_str = _ft(p, 'Pitches')
                        if pitches_str:
                             tuning = [int(x) for x in pitches_str.split()]
                        break
            
            track = Track(
                number=i + 1,
                name=name,
                program=program,
                is_percussion=is_percussion,
                channel=9 if is_percussion else (i % 16), 
                tuning=tuning
            )
            tracks_by_id[tid] = track
            song.tracks.append(track)
            
        # Parse MasterBars (Structure)
        master_bars = root.findall(f".//{ns}MasterBar")
        
        track_cursors = {tid: 0 for tid in track_ids}
        TICKS_PER_QUARTER = 960
        
        for mb_idx, mb in enumerate(master_bars):
            # Time Signature
            ts_str = _ft(mb, 'Time') or "4/4"
            num, den = map(int, ts_str.split('/'))
            
            measure_length_ticks = int(num * TICKS_PER_QUARTER * 4 / den)
            
            # Get list of Bar IDs for this MasterBar
            bar_ids_str = _get_ref_list(mb, 'Bars')
            
            for tr_idx, bar_id_str in enumerate(bar_ids_str):
                if tr_idx >= len(track_ids): break
                track_id = track_ids[tr_idx]
                track = tracks_by_id.get(track_id)
                if not track: continue
                
                cursor = track_cursors[track_id]
                
                measure = Measure(number=mb_idx+1, numerator=num, denominator=den)
                track.measures.append(measure)
                
                if bar_id_str:
                    bar_elem = get_elem('Bar', bar_id_str)
                    if bar_elem:
                        # Voices
                        voice_ids = _get_ref_list(bar_elem, 'Voices')
                        
                        for vid in voice_ids:
                            voice_elem = get_elem('Voice', vid)
                            if not voice_elem: continue
                            
                            voice_cursor = cursor
                            beat_ids = _get_ref_list(voice_elem, 'Beats')
                            
                            for bid in beat_ids:
                                beat_elem = get_elem('Beat', bid)
                                if not beat_elem: continue
                                
                                # Determine Duration
                                duration_ticks = 960 # Fallback
                                rhythm_ref = find_child(beat_elem, 'Rhythm')
                                if rhythm_ref is not None:
                                    rid = rhythm_ref.get('ref')
                                    if rid in rhythm_map:
                                        duration_ticks = int(960 * rhythm_map[rid])
                                        
                                beat_obj = Beat(start_time=voice_cursor, duration=duration_ticks)
                                
                                # Notes
                                note_ids = _get_ref_list(beat_elem, 'Notes')
                                for nid in note_ids:
                                    note_elem = get_elem('Note', nid)
                                    if not note_elem: continue
                                    self._parse_note(note_elem, beat_obj, ns)
                                
                                measure.beats.append(beat_obj)
                                voice_cursor += duration_ticks
                
                # Advance track cursor
                track_cursors[track_id] += measure_length_ticks

        return song

    def _parse_rhythms(self, root: ET.Element, ns: str) -> Dict[str, float]:
        mapping = {}
        base_values = {
            "Whole": 4.0, "Half": 2.0, "Quarter": 1.0, 
            "Eighth": 0.5, "16th": 0.25, "32nd": 0.125, 
            "64th": 0.0625, "128th": 0.03125
        }
        
        rhythms_node = root.find(f".//{ns}Rhythms")
        if rhythms_node is not None:
            for r in rhythms_node.findall(f"{ns}Rhythm"):
                rid = r.get('id')
                note_value_str = r.findtext(f"{ns}NoteValue")
                val = base_values.get(note_value_str, 1.0)
                
                dots = r.find(f"{ns}AugmentationDot")
                if dots is not None:
                    count = int(dots.get('count', 1))
                    val *= (2.0 - (1.0 / (2 ** count)))
                
                mapping[rid] = val
        return mapping

    def _parse_note(self, note_elem: ET.Element, beat: Beat, ns: str):
        props_node = note_elem.find(f"{ns}Properties")
        props = {}
        if props_node:
            for p in props_node.findall(f"{ns}Property"):
                props[p.get('name')] = p
        
        fret = 0
        string = 1
        velocity = 100
        midi_num = None
        
        def _val(prop_elem, tags=['Number', 'Int', 'Fret', 'String']):
            for t in tags:
                v = prop_elem.findtext(f"{ns}{t}")
                if v: 
                    try:
                        return int(float(v))
                    except ValueError:
                        pass
            return 0

        if 'Fret' in props:
            fret = _val(props['Fret'], ['Number', 'Int', 'Fret'])
            
        if 'String' in props:
            string = _val(props['String'], ['Number', 'Int', 'String']) + 1 

        if 'Velocity' in props:
             velocity = _val(props['Velocity'], ['Number', 'Int'])
             
        if 'Midi' in props:
            midi_num = _val(props['Midi'], ['Number', 'Int'])
        
        tie = note_elem.find(f"{ns}Tie")
        is_tie = False
        if tie is not None:
            if tie.get('destination') == 'true':
                is_tie = True
                
        note_type = NoteType.TIE if is_tie else NoteType.NORMAL
        
        note = Note(
            string=string,
            fret=fret,
            velocity=velocity,
            duration=1.0, 
            type=note_type,
            midi_number=midi_num
        )
        beat.notes.append(note)
