from music21 import *
from music21 import roman
import random
from datetime import datetime
import os
# github.com/zeittresor

BPM = 120              # Tempo
NUM_MEASURES = 64      # Gesamtlänge in Takten
SECTION_MEASURES = 16  # Takte pro Abschnitt

possible_keys = [
    ('C', 'major'), ('G', 'major'), ('D', 'major'), ('A', 'major'), ('E', 'major'),
    ('F', 'major'), ('Bb', 'major'), ('A', 'minor'), ('E', 'minor'), ('D', 'minor')
]

common_major = [
    ['I', 'vi', 'IV', 'V'],
    ['I', 'IV', 'V', 'I'],
    ['vi', 'IV', 'I', 'V'],
    ['I', 'V', 'vi', 'IV'],
    ['I', 'iii', 'IV', 'V']
]
common_minor = [
    ['i', 'VI', 'III', 'VII'],
    ['i', 'iv', 'V', 'i'],
    ['i', 'VII', 'VI', 'VII'],
    ['i', 'iv', 'VII', 'III']
]

melodic_patterns = [
    [0, 2, 4, 5], [0, -2, -4, -5], [0, 2, 0, -2],
    [0, 3, 5, 7], [0, -3, -5, -7],
]
rhythmic_patterns = [
    [1.0, 1.0, 1.0, 1.0], [0.5, 0.5, 1.0, 2.0], [0.75, 0.75, 0.5, 2.0],
    [1.5, 0.5, 1.5, 0.5], [0.5, 1.5, 0.5, 1.5],
]

def generate_random_progression(key_obj, mode):
    """Erzeugt eine zufällige Akkordfolge als Liste von gültigen Akkordnamen (z. B. 'Bb', 'Gm')."""
    if mode == 'major':
        progression = random.choice(common_major)
    else:
        progression = random.choice(common_minor)
    chord_names = []
    for rn in progression:
        rn_obj = roman.RomanNumeral(rn, key_obj)
        root_name = rn_obj.root().name  # z. B. "Bb" oder "C"
        if rn[0].islower():
            chord_names.append(root_name + "m")
        else:
            chord_names.append(root_name)
    return chord_names

def get_bass_note_from_chord(chord_str):
    """Ermittelt aus dem Akkordnamen die Bassnote."""
    if len(chord_str) > 1 and chord_str[1] in ['#', 'b']:
        root = chord_str[:2]
    else:
        root = chord_str[0]
    return root + "2"

def generate_melody_section(num_measures, scale_obj, chord_progression):
    melody = stream.Part()
    melody.id = 'Melody'
    pitch_range = scale_obj.getPitches('C4', 'C6')
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

def generate_chords_section(num_measures, chord_progression):
    chords_part = stream.Part()
    chords_part.id = 'Chords'
    for i in range(num_measures):
        chord_symbol = harmony.ChordSymbol(chord_progression[i % len(chord_progression)])
        chord_symbol.duration = duration.Duration(4.0)
        chords_part.append(chord_symbol)
    return chords_part

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
            bass_note = note.Note(random.choice(pitch_range))
            bass_note.duration = duration.Duration(duration_choice)
            bass_note.volume.velocity = 70
            notes_in_measure.append(bass_note)
            total_duration += duration_choice
        bass.append(notes_in_measure)
    return bass

def generate_strings_section(num_measures, scale_obj, chord_progression):
    strings = stream.Part()
    strings.id = 'Strings'
    for i in range(num_measures):
        chord_symbol = harmony.ChordSymbol(chord_progression[i % len(chord_progression)])
        string_chord = chord.Chord(chord_symbol.pitches)
        string_chord.duration = duration.Duration(4.0)
        string_chord.volume.velocity = 60
        strings.append(string_chord)
    return strings

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

def generate_piece():
    print("Generating musical piece...")
    s = stream.Stream()
    s.insert(0, tempo.MetronomeMark(number=BPM))

    key_choice = random.choice(possible_keys)
    root, mode = key_choice
    if mode == 'major':
        key_obj = key.Key(root)
        scale_obj = scale.MajorScale(root)
    else:
        key_obj = key.Key(root, 'minor')
        scale_obj = scale.MinorScale(root)
    print(f"Ausgewählte Tonart: {key_obj}")

    sections = ['intro', 'verse', 'chorus', 'verse', 'bridge', 'chorus', 'outro']
    total_measures = 0

    melody = stream.Part()
    chords = stream.Part()
    bass = stream.Part()
    strings = stream.Part()
    drums = stream.Part()

    for section in sections:
        chord_progression = generate_random_progression(key_obj, mode)
        bass_notes = [get_bass_note_from_chord(ch) for ch in chord_progression]

        melody_section = generate_melody_section(SECTION_MEASURES, scale_obj, chord_progression)
        chords_section = generate_chords_section(SECTION_MEASURES, chord_progression)
        bass_section = generate_bass_section(SECTION_MEASURES, bass_notes)
        strings_section = generate_strings_section(SECTION_MEASURES, scale_obj, chord_progression)
        drums_section = generate_techno_beat_section(SECTION_MEASURES, total_measures)
        if section in ['chorus', 'outro']:
            drums_section.append(generate_fill_in(SECTION_MEASURES, total_measures))
        
        melody.append(melody_section)
        chords.append(chords_section)
        bass.append(bass_section)
        strings.append(strings_section)
        drums.append(drums_section)

        total_measures += SECTION_MEASURES

    for i, n in enumerate(strings.flatten().getElementsByClass('Note')):
        if n.offset >= (NUM_MEASURES - 4) * 4:
            n.volume.velocity = max(60 - (i * 5), 0)

    melody.insert(0, instrument.StringInstrument())
    chords.insert(0, instrument.StringInstrument())
    bass.insert(0, instrument.ElectricBass())
    strings.insert(0, instrument.StringInstrument())

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
        print(f"Das Stück wurde erfolgreich als '{midi_filename}' in {os.getcwd()} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der MIDI-Datei: {e}")

if __name__ == "__main__":
    generate_piece()
