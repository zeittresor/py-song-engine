from music21 import *
import random
from datetime import datetime
import os
# Source https://github.com/Zeittresor

us = environment.UserSettings()
us['musicxmlPath'] = None
us['musescoreDirectPNGPath'] = None
us['ipythonShowFormat'] = None

# Constants
BPM = 120  # Constant tempo
NUM_MEASURES = 64  # Total number of measures
SECTION_MEASURES = 16  # Number of measures per section (e.g., verse, chorus)

# Define keys and scales for sections
keys_and_scales = {
    'verse': (key.Key('C'), scale.MajorScale('C')),
    'chorus': (key.Key('G'), scale.MajorScale('G')),
    'bridge': (key.Key('A'), scale.MinorScale('A')),
    'intro': (key.Key('D'), scale.MajorScale('D')),
    'outro': (key.Key('E'), scale.MinorScale('E')),
}

# Chord progressions for sections
chord_progressions = {
    'verse': ['C', 'Am', 'F', 'G'],
    'chorus': ['G', 'D', 'Em', 'C'],
    'bridge': ['Am', 'F', 'C', 'G'],
    'intro': ['D', 'G', 'A', 'D'],
    'outro': ['Em', 'C', 'G', 'D'],
}

# Define bass notes for sections
bass_notes_dict = {
    'verse': ['C2', 'A1', 'F1', 'G1'],
    'chorus': ['G2', 'D2', 'E2', 'C2'],
    'bridge': ['A2', 'F2', 'C2', 'G2'],
    'intro': ['D2', 'G1', 'A1', 'D2'],
    'outro': ['E2', 'C2', 'G2', 'D2'],
}

# Add melodic and rhythmic patterns
melodic_patterns = [
    [0, 2, 4, 5], [0, -2, -4, -5], [0, 2, 0, -2],
    [0, 3, 5, 7], [0, -3, -5, -7],  # New patterns
]
rhythmic_patterns = [
    [1.0, 1.0, 1.0, 1.0], [0.5, 0.5, 1.0, 2.0], [0.75, 0.75, 0.5, 2.0],
    [1.5, 0.5, 1.5, 0.5], [0.5, 1.5, 0.5, 1.5],  # New patterns
]

# Generate melody section with specified scale and chord progression
def generate_melody_section(num_measures, scale_obj, chord_progression):
    melody = stream.Part()
    melody.id = 'Melody'
    pitch_range = scale_obj.getPitches('C4', 'C6')
    scale_pitches = [p.pitchClass for p in pitch_range]
    current_note = note.Note(random.choice(pitch_range))

    for measure in range(num_measures):
        notes_in_measure = []
        chord_symbol = harmony.ChordSymbol(chord_progression[measure % len(chord_progression)])
        chord_pitches = [p.pitchClass for p in chord_symbol.pitches]
        melodic_pattern = random.choice(melodic_patterns)
        rhythmic_pattern = random.choice(rhythmic_patterns)
        pattern_length = min(len(melodic_pattern), len(rhythmic_pattern))
        
        for i in range(pattern_length):
            interval_steps = melodic_pattern[i]
            new_pitch = current_note.pitch.transpose(interval_steps)
            if new_pitch not in pitch_range:
                new_pitch = random.choice(pitch_range)
            if new_pitch.pitchClass not in chord_pitches:
                new_pitch = chord_symbol.root()
            current_note = note.Note(new_pitch)
            current_note.duration = duration.Duration(rhythmic_pattern[i])
            current_note.volume.velocity = 80
            notes_in_measure.append(current_note)
        melody.append(notes_in_measure)
    return melody

# Generate chords for a section
def generate_chords_section(num_measures, chord_progression):
    chords_part = stream.Part()
    chords_part.id = 'Chords'
    for i in range(num_measures):
        chord_symbol = harmony.ChordSymbol(chord_progression[i % len(chord_progression)])
        chord_symbol.duration = duration.Duration(4.0)
        chords_part.append(chord_symbol)
    return chords_part

# Generate bass for a section
def generate_bass_section(num_measures, bass_notes):
    bass = stream.Part()
    bass.id = 'Bass'
    pitch_range = [pitch.Pitch(p) for p in bass_notes]
    for i in range(num_measures):
        notes_in_measure = []
        rhythm_choices = [1.0, 2.0]
        total_duration = 0.0
        while total_duration < 4.0:
            duration_choice = random.choice(rhythm_choices)
            if total_duration + duration_choice > 4.0:
                duration_choice = 4.0 - total_duration
            bass_note = note.Note(
                random.choice(pitch_range)
            )
            bass_note.duration = duration.Duration(duration_choice)
            bass_note.volume.velocity = 70
            notes_in_measure.append(bass_note)
            total_duration += duration_choice
        bass.append(notes_in_measure)
    return bass

# Generate strings for a section
def generate_strings_section(num_measures, scale_obj, chord_progression):
    strings = stream.Part()
    strings.id = 'Strings'
    pitch_range = scale_obj.getPitches('C3', 'C5')
    for i in range(num_measures):
        chord_symbol = harmony.ChordSymbol(chord_progression[i % len(chord_progression)])
        string_chord = chord.Chord(chord_symbol.pitches)
        string_chord.duration = duration.Duration(4.0)
        string_chord.volume.velocity = 60
        strings.append(string_chord)
    return strings

# Generate techno beat with optional fills
def generate_techno_beat_section(num_measures, start_measure):
    drums = stream.Part()
    drums.id = 'Drums'
    drums.insert(0, instrument.Percussion())
    drums.insert(0, clef.PercussionClef())
    drums.insert(0, meter.TimeSignature('4/4'))

    for measure in range(num_measures):
        measure_offset = (start_measure + measure) * 4.0
        for beat in range(4):
            kick = note.Unpitched()
            kick.ps = 35
            kick.duration = duration.Duration(1.0)
            kick.volume.velocity = 90
            kick.offset = measure_offset + beat
            drums.append(kick)
            if beat == 3 and measure % 4 == 3:
                extra_kick = note.Unpitched()
                extra_kick.ps = 35
                extra_kick.duration = duration.Duration(0.5)
                extra_kick.volume.velocity = 90
                extra_kick.offset = measure_offset + beat + 0.5
                drums.append(extra_kick)
        for beat in [1, 3]:
            snare = note.Unpitched()
            snare.ps = 38
            snare.duration = duration.Duration(1.0)
            snare.volume.velocity = 80
            snare.offset = measure_offset + beat
            drums.append(snare)
        for beat in range(8):
            hihat = note.Unpitched()
            hihat.ps = 42
            hihat.duration = duration.Duration(0.5)
            hihat.volume.velocity = 70
            hihat.offset = measure_offset + (beat * 0.5)
            drums.append(hihat)
        if (measure % 4) == 3:
            crash = note.Unpitched()
            crash.ps = 49
            crash.duration = duration.Duration(1.0)
            crash.volume.velocity = 85
            crash.offset = measure_offset + 3
            drums.append(crash)
    for n in drums.recurse():
        if 'Instrument' in n.classes:
            n.midiChannel = 9
        elif 'Note' in n.classes or 'Unpitched' in n.classes:
            n.channel = 9
    return drums

# Generate an optional fill-in for drums
def generate_fill_in(num_measures, start_measure):
    fill = stream.Part()
    fill.id = 'DrumFill'
    for measure in range(num_measures):
        measure_offset = (start_measure + measure) * 4.0
        for beat in [0, 1, 2, 3]:
            snare = note.Unpitched()
            snare.ps = 38
            snare.duration = duration.Duration(0.5)
            snare.volume.velocity = 80
            snare.offset = measure_offset + beat * 0.5
            fill.append(snare)
    return fill

# Generate the entire piece with different sections
def generate_piece():
    print("Generating musical piece...")  # Debug message
    s = stream.Stream()
    s.insert(0, tempo.MetronomeMark(number=BPM))

    sections = ['intro', 'verse', 'chorus', 'verse', 'bridge', 'chorus', 'outro']
    total_measures = 0

    melody = stream.Part()
    chords = stream.Part()
    bass = stream.Part()
    strings = stream.Part()
    drums = stream.Part()

    for section in sections:
        key_signature, scale_obj = keys_and_scales[section]
        chord_progression = chord_progressions[section]
        bass_notes = bass_notes_dict[section]

        melody_section = generate_melody_section(SECTION_MEASURES, scale_obj, chord_progression)
        melody.append(melody_section)

        chords_section = generate_chords_section(SECTION_MEASURES, chord_progression)
        chords.append(chords_section)

        bass_section = generate_bass_section(SECTION_MEASURES, bass_notes)
        bass.append(bass_section)

        strings_section = generate_strings_section(SECTION_MEASURES, scale_obj, chord_progression)
        strings.append(strings_section)

        drums_section = generate_techno_beat_section(SECTION_MEASURES, total_measures)
        if section in ['chorus', 'outro']:
            drums_section.append(generate_fill_in(SECTION_MEASURES, total_measures))
        drums.append(drums_section)

        total_measures += SECTION_MEASURES

    # Using flatten() to avoid deprecation warning
    for i, n in enumerate(strings.flatten().getElementsByClass('Note')):
        if n.offset >= (NUM_MEASURES - 4) * 4:
            n.volume.velocity = max(60 - (i * 5), 0)

    melody.insert(0, instrument.Piano())
    chords.insert(0, instrument.ElectricGuitar() if 'chorus' in sections else instrument.AcousticGuitar())
    bass.insert(0, instrument.ElectricBass())
    strings.insert(0, instrument.StringInstrument() if 'bridge' in sections else instrument.Violoncello())

    s.insert(0, drums)
    s.insert(0, strings)
    s.insert(0, bass)
    s.insert(0, chords)
    s.insert(0, melody)

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    midi_filename = f'Song_{current_time}.mid'
    file_path = os.path.join(os.getcwd(), midi_filename)

    try:
        s.write('midi', fp=file_path)
        print(f"The piece was successfully saved as '{midi_filename}' in {os.getcwd()}.")
    except Exception as e:
        print(f"Error saving MIDI file: {e}")

if __name__ == "__main__":
    generate_piece()
