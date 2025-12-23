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
                    for effect in note.effects:
                        if effect.type == EffectType.BEND and effect.bend_points:
                            points = sorted(effect.bend_points, key=lambda p: p.position)
                            
                            # Constants
                            BEND_RANGE_SEMITONES = 12
                            GP_VALUE_TO_SEMITONES = 1.0 / 50.0 # 100 = 2 semitones
                            CENTER_PITCH = 0
                            MAX_PITCH = 8191
                            MIN_PITCH = -8192
                            
                            def val_to_pitch(gp_val):
                                semitones = gp_val * GP_VALUE_TO_SEMITONES
                                # Scale to -8192..+8191 range based on bend range
                                # unit = 8192 / BEND_RANGE_SEMITONES
                                offset = (semitones / BEND_RANGE_SEMITONES) * 8192
                                pitch = int(CENTER_PITCH + offset)
                                return max(MIN_PITCH, min(MAX_PITCH, pitch))
                            
                            # Generate Points
                            # We assume points positions are 0-100 where 100 = note duration?
                            # Or strict GP ticks? Let's assume 0-100 percentage for now as it's common.
                            # If positions are large (>100), treat as absolute ticks relative to note start?
                            # Standard GPX usually uses 0-100 for Position.
                            
                            # Interpolation
                            # We will generate a point every X ticks
                            resolution_ticks = 30 
                            
                            if len(points) == 1:
                                # Constant bend?
                                ev_time = start_abs + int(points[0].position / 100.0 * beat.duration)
                                pitch = val_to_pitch(points[0].value)
                                events.append({
                                    "time": ev_time, "type": "pitchwheel", 
                                    "pitch": pitch, "channel": channel
                                })
                            else:
                                for i in range(len(points) - 1):
                                    p1 = points[i]
                                    p2 = points[i+1]
                                    
                                    t1_rel = int(p1.position / 100.0 * beat.duration)
                                    t2_rel = int(p2.position / 100.0 * beat.duration)
                                    
                                    val1 = p1.value
                                    val2 = p2.value
                                    
                                    duration = t2_rel - t1_rel
                                    if duration <= 0:
                                        # Instant jump
                                        events.append({
                                            "time": start_abs + t1_rel, "type": "pitchwheel",
                                            "pitch": val_to_pitch(val1), "channel": channel
                                        })
                                        continue
                                        
                                    # Interpolate
                                    steps = max(1, int(duration / resolution_ticks))
                                    for s in range(steps + 1):
                                        alpha = s / float(steps)
                                        cur_time_rel = t1_rel + int(duration * alpha)
                                        cur_val = val1 + (val2 - val1) * alpha
                                        
                                        events.append({
                                            "time": start_abs + cur_time_rel, "type": "pitchwheel",
                                            "pitch": val_to_pitch(cur_val), "channel": channel
                                        })

                            # Reset Pitch Bend at end of note
                            events.append({
                                "time": end_abs, "type": "pitchwheel", 
                                "pitch": CENTER_PITCH, "channel": channel
                            }) 

        # Sort events by time
        events.sort(key=lambda x: x["time"])

        # Write to track with delta times
        last_time = 0
        for ev in events:
            dt = ev["time"] - last_time
            if dt < 0: dt = 0
            if ev["type"] == "pitchwheel":
                 midi_track.append(
                    mido.Message(
                        "pitchwheel",
                        pitch=ev["pitch"],
                        channel=ev["channel"],
                        time=dt,
                    )
                )
            else:
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
