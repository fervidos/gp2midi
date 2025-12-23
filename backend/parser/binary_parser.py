from backend.parser.gp_parser import GPParser

import guitarpro

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


class BinaryParser(GPParser):
    def parse_file(self, file_path: str) -> Song:
        try:
            gp_song = guitarpro.parse(file_path)
            return self._map_to_ir(gp_song)
        except Exception as e:
            print(f"Error parsing GP file: {e}")
            raise

    def parse_bytes(self, file_content: bytes) -> Song:
        # PyGuitarPro parse expects a stream or path.
        # We might need to write to temp file or wrap bytes in io.BytesIO
        import io

        stream = io.BytesIO(file_content)
        # Note: guitarpro.parse might strictly require a filename for 
        # extension detection?
        # Let's inspect source or try. Usually it reads headers.
        # Ideally we save to temp file to be safe.
        gp_song = guitarpro.parse(stream)
        return self._map_to_ir(gp_song)

    def _map_to_ir(self, gp_song) -> Song:
        song = Song(title=gp_song.title, artist=gp_song.artist, tempo=gp_song.tempo)

        for gp_track in gp_song.tracks:
            track = Track(
                number=gp_track.number,
                name=gp_track.name,
                is_percussion=gp_track.isPercussionTrack,
                channel=gp_track.channel.channel,
                program=gp_track.channel.instrument,
            )

            for gp_measure in gp_track.measures:
                measure = Measure(
                    number=gp_measure.number,
                    numerator=gp_measure.timeSignature.numerator,
                    denominator=gp_measure.timeSignature.denominator.value,
                )

                for gp_voice in gp_measure.voices:
                    # GP has 2 voices per track usually. We flatten or keep them?
                    # For now, flatten beats from valid voices
                    for gp_beat in gp_voice.beats:
                        beat = Beat(
                            start_time=gp_beat.start,
                            duration=gp_beat.duration.value,
                            text=gp_beat.text,
                        )

                        for gp_note in gp_beat.notes:
                            note_type = NoteType.NORMAL
                            if gp_note.type.name == "rest":
                                note_type = NoteType.REST
                            elif gp_note.type.name == "dead":
                                note_type = NoteType.DEAD
                            elif (
                                gp_note.type.name == "tie"
                            ):  # Logic might be different in PyGuitarPro
                                note_type = NoteType.TIE

                            # Effects
                            effects = []
                            if gp_note.effect.isBend:
                                # Process bend points
                                effects.append(
                                    NoteEffect(type=EffectType.BEND)
                                )  # Simplify for now
                            if gp_note.effect.isHarmonic:
                                effects.append(NoteEffect(type=EffectType.HARMONIC))

                            note = Note(
                                string=gp_note.string,
                                fret=gp_note.value,
                                velocity=gp_note.velocity,
                                duration=1.0,  # Placeholder, need real duration calc
                                type=note_type,
                                effects=effects,
                            )
                            beat.notes.append(note)

                        if beat.notes:
                            measure.beats.append(beat)

                track.measures.append(measure)

            song.tracks.append(track)

        return song
