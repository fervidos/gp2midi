import mido
import math
from backend.core.converter.channel_manager import ChannelManager
from backend.models.song_model import EffectType, NoteType, Song, Track

class MidiWriter:
    def __init__(self, song: Song, high_fidelity: bool = True):
        self.song = song
        self.high_fidelity = high_fidelity
        self.midi_file = mido.MidiFile(ticks_per_beat=960)
        self.channel_manager = ChannelManager()

    def write(self, output_path=None, file=None):
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

        if file:
            self.midi_file.save(file=file)
        elif output_path:
            self.midi_file.save(filename=output_path)
        else:
            raise ValueError("Either output_path or file must be provided")

    def _process_track(self, track: Track) -> mido.MidiTrack:
        midi_track = mido.MidiTrack()
        midi_track.append(mido.MetaMessage("track_name", name=track.name, time=0))

        # Channel setup
        channels = []
        if track.is_percussion:
            channels = [9]
        elif self.high_fidelity:
            channels = self.channel_manager.allocate_channel(track.number, count=6)
        else:
            channels = self.channel_manager.allocate_channel(track.number, count=1)

        if not channels:
            channels = [0]  # Fallback

        current_program = track.program

        # Set Program for all allocated channels
        for ch in channels:
            # Bank Select
            if track.bank_msb is not None:
                midi_track.append(
                    mido.Message("control_change", control=0, value=track.bank_msb, channel=ch, time=0)
                )
            if track.bank_lsb is not None:
                midi_track.append(
                    mido.Message("control_change", control=32, value=track.bank_lsb, channel=ch, time=0)
                )
            
            midi_track.append(
                mido.Message("program_change", program=current_program, channel=ch, time=0)
            )
            self._set_pitch_bend_range(midi_track, ch, semitones=12)

        events = []
        
        for measure in track.measures:
            for beat in measure.beats:
                for note in beat.notes:
                    if note.type in [NoteType.REST, NoteType.DEAD]:
                        continue

                    # Channel Selection
                    channel = channels[0]
                    if self.high_fidelity and not track.is_percussion:
                        # Map string index to channel index (safe modulo)
                        idx = (note.string - 1) % len(channels)
                        channel = channels[idx]

                    # Velocity & Duration
                    vel = min(127, max(0, note.velocity))
                    start_abs = beat.start_time
                    end_abs = int(start_abs + beat.duration) # Simple duration logic

                    # MIDI Number calculation
                    midi_note = note.midi_number
                    if midi_note is None:
                         # Fallback calculation
                        base = note.fret
                        if not track.is_percussion and track.tuning:
                             # Ensure string index is within bounds of tuning array
                            string_idx = note.string - 1
                            if 0 <= string_idx < len(track.tuning):
                                base += track.tuning[string_idx]
                        midi_note = base
                    
                    # Clamp MIDI note
                    midi_note = min(127, max(0, midi_note))

                    events.append({
                        "time": start_abs, "type": "note_on", 
                        "note": midi_note, "velocity": vel, "channel": channel
                    })
                    events.append({
                        "time": end_abs, "type": "note_off", 
                        "note": midi_note, "velocity": 0, "channel": channel
                    })

                    # Handle Bends
                    # TODO: Real interpolation from GPX points. 
                    # For now just checking if BEND effect exists and adding a dummy slide if needed?
                    # Actually without points data we can't do much.
                    # But if we had points, we would generate pitchwheel events here.
                    pass 

        # Sort events by time
        events.sort(key=lambda x: x["time"])

        # Write to track with delta times
        last_time = 0
        for ev in events:
            dt = ev["time"] - last_time
            if dt < 0: dt = 0
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
            
        midi_track.append(mido.MetaMessage("end_of_track", time=0))
        return midi_track

    def _set_pitch_bend_range(self, track, channel, semitones=12):
        # RPN 00 00 Pitch Bend Range
        track.append(mido.Message("control_change", control=101, value=0, channel=channel, time=0))
        track.append(mido.Message("control_change", control=100, value=0, channel=channel, time=0))
        track.append(mido.Message("control_change", control=6, value=semitones, channel=channel, time=0))
        track.append(mido.Message("control_change", control=38, value=0, channel=channel, time=0))
        # Reset RPN
        track.append(mido.Message("control_change", control=101, value=127, channel=channel, time=0))
        track.append(mido.Message("control_change", control=100, value=127, channel=channel, time=0))
