from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

class NoteType(Enum):
    REST = "rest"
    NORMAL = "normal"
    TIE = "tie"
    DEAD = "dead"

class EffectType(Enum):
    NONE = "none"
    BEND = "bend"
    SLIDE = "slide"
    HAMMER = "hammer"
    PULL = "pull"
    TRILL = "trill"
    HARMONIC = "harmonic"
    PALM_MUTE = "palm_mute"
    VIBRATO = "vibrato"

class BendPoint(BaseModel):
    position: int  # 0 to 100 type scale or 0-12
    value: int     # semitones * 2? 1/4 tones? specific GP value

class NoteEffect(BaseModel):
    type: EffectType
    value: Optional[float] = None # Generic value container
    bend_points: List[BendPoint] = [] 

class Note(BaseModel):
    string: int # 1-based or 0-based? Let's say 1-based for GP logic
    fret: int
    velocity: int
    duration: float # relative to quarter note? 
    type: NoteType
    effects: List[NoteEffect] = []
    
    # Absolute time calculation will happen later, but good to store relative
    duration_percent: float = 1.0 # 1.0 = full beat duration occupied
    midi_number: Optional[int] = None # Pre-calculated MIDI number from GP

class Beat(BaseModel):
    start_time: int # Ticks? 
    duration: int # Ticks
    notes: List[Note] = []
    text: Optional[str] = None

class Measure(BaseModel):
    number: int
    numerator: int
    denominator: int
    beats: List[Beat] = []

class Track(BaseModel):
    number: int
    name: str # "Distortion Guitar"
    is_percussion: bool = False
    channel: int # 0-15
    program: int # MIDI Program Change (0-127)
    tuning: List[int] = [] # String MIDI numbers, low to high
    measures: List[Measure] = []

class Song(BaseModel):
    title: str = "Untitled"
    artist: str = "Unknown"
    tempo: int = 120 # BPM
    tracks: List[Track] = []
