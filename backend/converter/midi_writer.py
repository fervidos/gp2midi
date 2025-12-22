import mido

from converter.channel_manager import ChannelManager
from models.song_model import EffectType, NoteType, Song, Track


class MidiWriter:
    def __init__(self, song: Song, high_fidelity: bool = True):
        self.song = song
        self.high_fidelity = high_fidelity
        self.midi_file = mido.MidiFile(ticks_per_beat=960)  # Standard high resolution
        self.channel_manager = ChannelManager()

    def write(self, output_path: str):
        # Create Tempo Track
        tempo_track = mido.MidiTrack()
        self.midi_file.tracks.append(tempo_track)
        tempo_bpm = self.song.tempo
        tempo_midi = mido.bpm2tempo(tempo_bpm)
        tempo_track.append(mido.MetaMessage("set_tempo", tempo=tempo_midi, time=0))
        tempo_track.append(mido.MetaMessage("end_of_track", time=0))

        for track in self.song.tracks:
            midi_track = self._process_track(track)
            self.midi_file.tracks.append(midi_track)

        self.midi_file.save(output_path)

    def _process_track(self, track: Track) -> mido.MidiTrack:
        midi_track = mido.MidiTrack()
        midi_track.append(mido.MetaMessage("track_name", name=track.name, time=0))

        # Channel setup
        # If percussion, hardcode channel 9 (10)
        # If HighFi, allocate multiple channels.
        # If Standard, allocate 1.

        channels = []
        if track.is_percussion:
            channels = [9]
        elif self.high_fidelity:
            channels = self.channel_manager.allocate_channel(track.number, count=6)
        else:
            channels = self.channel_manager.allocate_channel(track.number, count=1)

        print(f"Track {track.name}: Allocated channels {channels}")
        if not channels:
            print("WARNING: No channels allocated!")
            channels = [0]  # Fallback

        current_program = track.program

        # Set Program for all allocated channels
        for ch in channels:
            midi_track.append(
                mido.Message(
                    "program_change", program=current_program, channel=ch, time=0
                )
            )
            # Set Pitch Bend Range to 12 semitones (or 24) for safe wide bends
            self._set_pitch_bend_range(midi_track, ch, semitones=12)

        # Convert simple timeline to absolute events
        # This is a bit complex: We need to flatten the IR
        # (Measures -> Beats -> Notes) into a list of events.
        events = []

        # Cursor in ticks
        # current_tick = 0

        # Simple assumption: 4/4, Measure duration depends on signature
        # But our Beat model has 'duration' in GP format (1.0 = whole?).
        # Verify GP Beat.duration.value: 1.0 = Quarter note usually in GP internal, OR
        # In PyGuitarPro: duration is an object. value assumes 4/4 context usually.
        # Let's assume Beat.duration from IR is already in "Quarter Notes" unit?
        # Wait, in parser I did: duration=gp_beat.duration.value.
        # Read PyGuitarPro docs/source: Beat.duration.value is an integer?
        # No, it's a Duration object.
        # value 1 = whole, 2 = half, 4 = quarter.
        # So duration in beats = 4 / value.

        for measure in track.measures:
            # This is naive. GP beats structure is weird.
            # We will use accumulated time.
            # measure_start_tick = current_tick

            for beat in measure.beats:
                # Calculate duration in ticks
                # beat.duration came from 1/value. e.g. 1/4 = 0.25?
                # Actually in parser I just said 'value'.
                # Let's check parser again. 'gp_beat.start' is absolute time in GP?
                # PyGuitarPro: beat.start is "Start time of the beat".
                # relative to measure? or song?
                # Usually song absolute time in 960 ticks/quarter.
                # If beat.start is available, use it!

                # If beat.start_time is reliable, we place notes there.

                # beat_tick = beat.start_time
                # beat.start_time is already absolute ticks from the parser 
                # (using 960 TPQ)

                for note in beat.notes:
                    if note.type in [NoteType.REST, NoteType.DEAD]:
                        continue

                    # Channel Selection
                    channel = channels[0]
                    if self.high_fidelity and not track.is_percussion:
                        # Map string index to channel index
                        # string 1..6 -> index 0..5
                        # Safely wrap around if we have fewer channels (fallback)
                        idx = (note.string - 1) % len(channels)
                        channel = channels[idx]

                    # Note On
                    # Velocity
                    vel = note.velocity
                    # Duration
                    # In the parser, beat.duration is already calculated in ticks 
                    # (e.g. 960 for quarter note)
                    note_duration_ticks = beat.duration

                    # Start absolute time
                    start_abs = beat.start_time
                    end_abs = start_abs + note_duration_ticks

                    if note.midi_number is not None:
                        midi_note = note.midi_number
                    else:
                        midi_note = (
                            note.fret + track.tuning[note.string - 1]
                            if not track.is_percussion
                            else note.fret
                        )  # Fallback

                    events.append(
                        {
                            "time": start_abs,
                            "type": "note_on",
                            "note": midi_note,
                            "velocity": vel,
                            "channel": channel,
                        }
                    )
                    events.append(
                        {
                            "time": end_abs,
                            "type": "note_off",
                            "note": midi_note,
                            "velocity": 0,
                            "channel": channel,
                        }
                    )

                    # Handle Bends (simplistic implementation)
                    for effect in note.effects:
                        if effect.type == EffectType.BEND:
                            # Add pitch wheel events between start and end
                            pass  # TODO: Implement curve interpolation

        # Sort events by time
        events.sort(key=lambda x: x["time"])

        # Write to track with delta times
        last_time = 0
        for ev in events:
            dt = ev["time"] - last_time
            if dt < 0:
                dt = 0  # Safety
            midi_track.append(
                mido.Message(
                    ev["type"],
                    note=ev["note"],
                    velocity=ev["velocity"],
                    channel=ev["channel"],
                    time=dt,
                )
            )
            last_time = ev["time"]

        return midi_track

    def _set_pitch_bend_range(self, track, channel, semitones=2):
        # RPN 00 00 is Pitch Bend Range
        # CC 101 0, CC 100 0
        track.append(
            mido.Message(
                "control_change", control=101, value=0, channel=channel, time=0
            )
        )
        track.append(
            mido.Message(
                "control_change", control=100, value=0, channel=channel, time=0
            )
        )
        # Data Entry MSB (CC 6) = semitones
        track.append(
            mido.Message(
                "control_change", control=6, value=semitones, channel=channel, time=0
            )
        )
        # Data Entry LSB (CC 38) = cents (0)
        track.append(
            mido.Message("control_change", control=38, value=0, channel=channel, time=0)
        )
        # Reset RPN (optional but good practice)
        track.append(
            mido.Message(
                "control_change", control=101, value=127, channel=channel, time=0
            )
        )
        track.append(
            mido.Message(
                "control_change", control=100, value=127, channel=channel, time=0
            )
        )
