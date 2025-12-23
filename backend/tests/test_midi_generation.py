import os
import sys

# Add current directory to path so we can import modules
# Add project root directory to path so we can import 'backend' package
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from backend.converter.midi_writer import MidiWriter
from backend.models.song_model import (
    Beat,
    EffectType,
    Measure,
    Note,
    NoteEffect,
    NoteType,
    Song,
    Track,
)


def test_midi_generation():
    print("Creating dummy song...")
    song = Song(title="Test Song", artist="Me", tempo=120)

    # Create a wrapper track
    # Standard E Tuning: E2 A2 D3 G3 B3 E4 -> 40 45 50 55 59 64
    track = Track(
        number=1,
        name="Distortion Guitar",
        program=30,
        channel=0,
        tuning=[40, 45, 50, 55, 59, 64],
    )

    # Create one measure
    measure = Measure(number=1, numerator=4, denominator=4)

    # Create 4 beats (quarter notes)
    # C Major Scale: C3, D3, E3, F3
    notes = [48, 50, 52, 53]

    for i, pitch in enumerate(notes):
        beat = Beat(start_time=i * 960, duration=4)  # 960 ticks per beat

        note = Note(
            string=1,
            fret=pitch,  # Simplified: mapping fret directly to pitch for this test
            velocity=100,
            duration=1.0,
            type=NoteType.NORMAL,
            duration_percent=1.0,
        )

        # Add a bend to the 3rd note
        if i == 2:
            note.effects.append(NoteEffect(type=EffectType.BEND))

        beat.notes.append(note)
        measure.beats.append(beat)

    track.measures.append(measure)
    song.tracks.append(track)

    print("Converting to MIDI...")
    writer = MidiWriter(song, high_fidelity=True)
    output_file = "test_output.mid"
    writer.write(output_file)

    if os.path.exists(output_file):
        print(f"Success! {output_file} created.")
        print(f"Size: {os.path.getsize(output_file)} bytes")
    else:
        print("Failed to create MIDI file.")


if __name__ == "__main__":
    test_midi_generation()
