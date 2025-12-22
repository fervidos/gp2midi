from parser.xml_parser import XmlParser
import sys

def debug_parse(file_path):
    print(f"DEBUG: Parsing {file_path}")
    parser = XmlParser()
    try:
        song = parser.parse_file(file_path)
        print(f"DEBUG: Parsing complete.")
        print(f"DEBUG: Song Title: {song.title}")
        print(f"DEBUG: Song Artist: {song.artist}")
        print(f"DEBUG: Tempo: {song.tempo}")
        print(f"DEBUG: Track Count: {len(song.tracks)}")
        
        total_notes = 0
        for track in song.tracks:
            print(f"  Track {track.number}: {track.name}, Measures: {len(track.measures)}")
            notes_in_track = 0
            for measure in track.measures:
                for beat in measure.beats:
                    notes_in_track += len(beat.notes)
            print(f"    Notes in track: {notes_in_track}")
            total_notes += notes_in_track
            
        print(f"DEBUG: Total Notes in Song: {total_notes}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parse(r"c:\Users\sales\Downloads\Code Stuff\gp2midi\My Bloody Valentine-When You Sleep-11-06-2025.gp")
