import io
import xml.etree.ElementTree as ET
import zipfile
from backend.core.parser.gp_parser import GPParser
from typing import Dict

from backend.models.song_model import (
    Beat,
    Measure,
    Note,
    NoteType,
    Song,
    Track,
)


class XmlParser(GPParser):
    def parse_file(self, file_path: str) -> Song:
        with open(file_path, "rb") as f:
            content = f.read()
        return self.parse_bytes(content)

    def parse_bytes(self, file_content: bytes) -> Song:
        with zipfile.ZipFile(io.BytesIO(file_content)) as z:
            filenames = z.namelist()
            score_file = None
            if "score.gpif" in filenames:
                score_file = "score.gpif"
            elif "Content/score.gpif" in filenames:
                score_file = "Content/score.gpif"

            if not score_file:
                raise ValueError("Invalid GPX/GP file: score.gpif not found")

            with z.open(score_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                return self._parse_xml(root)

    def _parse_xml(self, root: ET.Element) -> Song:
        # Check Namespace
        ns_match = root.tag.split("}")
        self.ns = ns_match[0] + "}" if len(ns_match) > 1 else ""

        # Build Typed ID map
        self._build_id_map(root)

        song = Song()
        self._parse_metadata(root, song)
        self._parse_rhythms(root) # Update internal map
        self._parse_tempo(root, song)
        
        # Parse Tracks
        track_ids = self._get_track_refs(root)
        self._parse_tracks(song, track_ids)

        # Parse Structure (MasterBars -> Measures -> Notes)
        self._parse_structure(root, song, track_ids)

        return song

    def _build_id_map(self, root: ET.Element):
        self.id_map = {}
        for elem in root.iter():
            eid = elem.get("id")
            if eid is not None:
                tag_local = elem.tag.split("}")[-1]
                if tag_local not in self.id_map:
                    self.id_map[tag_local] = {}
                self.id_map[tag_local][str(eid)] = elem

    def _get_elem(self, tag_suffix, eid):
        return self.id_map.get(tag_suffix, {}).get(str(eid))

    def _ft(self, elem, tag):
        return elem.findtext(f"{self.ns}{tag}")

    def _get_ref_list(self, elem, tag):
        txt = self._ft(elem, tag)
        return txt.split() if txt else []

    def _find_child(self, parent, tag):
        return parent.find(f"{self.ns}{tag}")

    def _findall_child(self, parent, tag):
        return parent.findall(f"{self.ns}{tag}")

    def _parse_metadata(self, root, song: Song):
        song.title = self._ft(root, "Title") or "Untitled"
        song.artist = self._ft(root, "Artist") or "Unknown"

    def _parse_tempo(self, root, song: Song):
        master_track = self._find_child(root, "MasterTrack")
        if master_track:
            automations = self._find_child(master_track, "Automations")
            if automations:
                for auto in self._findall_child(automations, "Automation"):
                    type_elem = self._find_child(auto, "Type")
                    if type_elem is not None and type_elem.text == "Tempo":
                        val_str = self._ft(auto, "Value")
                        if val_str:
                            try:
                                song.tempo = int(val_str.split()[0])
                            except Exception:
                                pass

    def _get_track_refs(self, root):
        master_track = self._find_child(root, "MasterTrack")
        if master_track:
            return [int(tid) for tid in self._get_ref_list(master_track, "Tracks")]
        return []

    def _parse_tracks(self, song: Song, track_ids: list):
         for i, tid in enumerate(track_ids):
            track_elem = self._get_elem("Track", tid)
            if not track_elem:
                continue

            name = self._ft(track_elem, "Name") or f"Track {i + 1}"
            program = 0
            is_percussion = False

            # Sounds / Program
            sounds = self._find_child(track_elem, "Sounds")
            if sounds:
                sound = self._find_child(sounds, "Sound")
                if sound:
                    midi_node = self._find_child(sound, "MIDI")
                    if midi_node:
                        p_str = self._ft(midi_node, "Program")
                        if p_str:
                            program = int(p_str)
                        # Bank Parsing
                        bank_node = self._find_child(midi_node, "Bank")
                        if bank_node is not None:
                            # GP often stores bank as a single string "General MIDI" or a number.
                            # We might need to look for specific Children like "MSB", "LSB" or just "Number"
                            # Re-inspecting typical GPX structure:
                            # <Bank>Could be text</Bank> OR <Bank><MSB>0</MSB><LSB>0</LSB></Bank>?
                            pass # Placeholder, usually GPX uses 'Primary' or 'Secondary' attributes


            inst_set = self._find_child(track_elem, "InstrumentSet")
            if inst_set and self._ft(inst_set, "Type") == "drumKit":
                is_percussion = True

            # Tuning
            tuning = []
            properties = self._find_child(track_elem, "Properties")
            if properties:
                for p in self._findall_child(properties, "Property"):
                    if p.get("name") == "Tuning":
                        pitches_str = self._ft(p, "Pitches")
                        if pitches_str:
                            tuning = [int(x) for x in pitches_str.split()]
                        break

            track = Track(
                number=i + 1,
                name=name,
                program=program,
                is_percussion=is_percussion,
                channel=9 if is_percussion else (i % 16),
                tuning=tuning,
            )
            # Store track reference by ID in a temporary map if needed, 
            # but we can just use song.tracks and index match since track_ids are ordered.
            song.tracks.append(track)
            
            # We also need a way to lookup track by ID during stricture parsing.
            # Let's attach the ID to the track object temporarily or use a helper map.
            track._gp_id = tid

    def _parse_structure(self, root, song: Song, track_ids: list):
        # Create a map for quick track lookup
        tracks_by_id = {t._gp_id: t for t in song.tracks if hasattr(t, "_gp_id")}
        track_cursors = {tid: 0 for tid in track_ids}
        TICKS_PER_QUARTER = 960

        master_bars = root.findall(f".//{self.ns}MasterBar")
        
        for mb_idx, mb in enumerate(master_bars):
            ts_str = self._ft(mb, "Time") or "4/4"
            num, den = map(int, ts_str.split("/"))
            measure_length_ticks = int(num * TICKS_PER_QUARTER * 4 / den)
            
            bar_ids_str = self._get_ref_list(mb, "Bars")

            for tr_idx, bar_id_str in enumerate(bar_ids_str):
                if tr_idx >= len(track_ids):
                    break
                track_id = track_ids[tr_idx]
                track = tracks_by_id.get(track_id)
                if not track:
                    continue

                cursor = track_cursors[track_id]
                measure = Measure(number=mb_idx + 1, numerator=num, denominator=den)
                track.measures.append(measure)

                if bar_id_str:
                    self._parse_bar_content(bar_id_str, measure, cursor)

                track_cursors[track_id] += measure_length_ticks

    def _parse_bar_content(self, bar_id_str, measure: Measure, cursor: int):
        bar_elem = self._get_elem("Bar", bar_id_str)
        if not bar_elem:
            return

        voice_ids = self._get_ref_list(bar_elem, "Voices")
        for vid in voice_ids:
            voice_elem = self._get_elem("Voice", vid)
            if not voice_elem:
                continue

            voice_cursor = cursor
            beat_ids = self._get_ref_list(voice_elem, "Beats")

            for bid in beat_ids:
                beat_elem = self._get_elem("Beat", bid)
                if not beat_elem:
                    continue

                duration_ticks = self._get_beat_duration(beat_elem)
                beat_obj = Beat(start_time=voice_cursor, duration=duration_ticks)

                note_ids = self._get_ref_list(beat_elem, "Notes")
                for nid in note_ids:
                    note_elem = self._get_elem("Note", nid)
                    if note_elem:
                        self._parse_note(note_elem, beat_obj)

                measure.beats.append(beat_obj)
                voice_cursor += duration_ticks

    def _get_beat_duration(self, beat_elem):
        duration_ticks = 960
        rhythm_ref = self._find_child(beat_elem, "Rhythm")
        if rhythm_ref is not None:
            rid = rhythm_ref.get("ref")
            if rid in self.rhythm_map:
                duration_ticks = int(960 * self.rhythm_map[rid])
        return duration_ticks

    def _parse_rhythms(self, root):
        # ... logic as before but store in self.rhythm_map
        mapping = {}
        base_values = {
            "Whole": 4.0, "Half": 2.0, "Quarter": 1.0, "Eighth": 0.5,
            "16th": 0.25, "32nd": 0.125, "64th": 0.0625, "128th": 0.03125,
        }
        rhythms_node = root.find(f".//{self.ns}Rhythms")
        if rhythms_node is not None:
            for r in rhythms_node.findall(f"{self.ns}Rhythm"):
                rid = r.get("id")
                note_value_str = r.findtext(f"{self.ns}NoteValue")
                val = base_values.get(note_value_str, 1.0)
                dots = r.find(f"{self.ns}AugmentationDot")
                if dots is not None:
                    count = int(dots.get("count", 1))
                    val *= 2.0 - (1.0 / (2**count))
                mapping[rid] = val
        self.rhythm_map = mapping
        return mapping

    def _parse_note(self, note_elem: ET.Element, beat: Beat):
         # ... reuse existing logic but adapted ...
        props_node = note_elem.find(f"{self.ns}Properties")
        props = {}
        if props_node:
            for p in props_node.findall(f"{self.ns}Property"):
                props[p.get("name")] = p

        fret = 0
        string = 1
        velocity = 100
        midi_num = None

        def _val(prop_elem, tags=["Number", "Int", "Fret", "String"]):
            for t in tags:
                v = prop_elem.findtext(f"{self.ns}{t}")
                if v:
                    try:
                        return int(float(v))
                    except ValueError:
                        pass
            return 0

        if "Fret" in props:
            fret = _val(props["Fret"], ["Number", "Int", "Fret"])
        if "String" in props:
            string = _val(props["String"], ["Number", "Int", "String"]) + 1
        if "Velocity" in props:
            velocity = _val(props["Velocity"], ["Number", "Int"])
        if "Midi" in props:
            midi_num = _val(props["Midi"], ["Number", "Int"])

        tie = note_elem.find(f"{self.ns}Tie")
        is_tie = False
        if tie is not None:
            if tie.get("destination") == "true":
                is_tie = True
        
        note_type = NoteType.TIE if is_tie else NoteType.NORMAL
        
        # Detect bends (basic)
        effects = []
        # TODO: Detect bends from GPX properties if available
        
        note = Note(
            string=string,
            fret=fret,
            velocity=velocity,
            duration=1.0,
            type=note_type,
            midi_number=midi_num,
            effects=effects
        )
        beat.notes.append(note)
