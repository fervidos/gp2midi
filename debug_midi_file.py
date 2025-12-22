import mido
import sys

def inspect_midi(file_path):
    with open("midi_dump.txt", "w") as f:
        try:
            mid = mido.MidiFile(file_path)
            f.write(f"MIDI File: {file_path}\n")
            f.write(f"Type: {mid.type}, Ticks per beat: {mid.ticks_per_beat}\n")
            f.write(f"Track count: {len(mid.tracks)}\n")
            
            for i, track in enumerate(mid.tracks):
                f.write(f"\nTrack {i}: {track.name}\n")
                f.write(f"Event count: {len(track)}\n")
                # Print first 200 events
                for msg in track[:200]:
                    f.write(str(msg) + "\n")
        except Exception as e:
            f.write(f"Error reading MIDI: {e}\n")

if __name__ == "__main__":
    # Hardcoded path provided by user context
    inspect_midi(r"c:\Users\sales\Downloads\Code Stuff\gp2midi\My Bloody Valentine-When You Sleep-11-06-2025(Standard).mid")
