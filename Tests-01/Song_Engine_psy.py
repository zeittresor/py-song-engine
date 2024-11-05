import os
import random
from datetime import datetime
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

from music21 import *
import fluidsynth

# ================== Globale Einstellungen ==================

# Constants
BPM = 140  # Erhöht für einen typischen Techno/Psytrance-Charakter
SECTION_MEASURES = 16  # Anzahl der Takte pro Abschnitt (z.B. verse, chorus)

# Taktarten
time_signature_options = ['4/4', '3/4']

# Genre-Auswahl
GENRE = "psytrance"  # Optionen: "psytrance", "classic", "synth"

# Scale and Key options for variation, ensuring harmony
keys_and_scales_options = [
    ('C', 'MajorScale'),
    ('G', 'MajorScale'),
    ('A', 'MinorScale'),
    ('D', 'MinorScale'),
    ('F', 'MajorScale'),
    ('E', 'MinorScale'),
    ('Bb', 'MajorScale'),
]

# Chord progressions with randomized but harmonic options
chord_progressions_options = {
    'intro': [['Am', 'F', 'C', 'G'], ['Am', 'F', 'C', 'G']],
    'verse': [['Am', 'F', 'C', 'G'], ['Dm', 'Am', 'Bb', 'F'], ['Em', 'C', 'G', 'D']],
    'chorus': [['C', 'G', 'Am', 'F'], ['F', 'G', 'Am', 'C'], ['C', 'G', 'F', 'Am']],
    'bridge': [['Dm', 'Am', 'Bb', 'F'], ['Gm', 'Bb', 'C', 'Dm'], ['Am', 'F', 'C', 'G']],
    'outro': [['Am', 'F', 'C', 'G'], ['Am', 'F', 'C', 'G']],
}

# ================== Musikgenerierungsfunktionen ==================

# Funktion zur zufälligen Auswahl von Schlüssel und Skala
def get_random_key_and_scale():
    key_name, scale_type = random.choice(keys_and_scales_options)
    k = key.Key(key_name)
    if scale_type == 'MajorScale':
        s = scale.MajorScale(key_name)
    elif scale_type == 'MinorScale':
        s = scale.MinorScale(key_name)
    else:
        s = scale.MajorScale(key_name)
    return k, s

# Funktion zur zufälligen Auswahl der Akkordprogression für einen Abschnitt
def get_random_chord_progression(section):
    return random.choice(chord_progressions_options[section])

# Funktion zur Generierung der Melodie basierend auf Akkordnoten
def generate_melody_section(num_measures, scale_obj, chord_progression):
    melody = stream.Part()
    melody.id = 'Melody'
    melody.append(instrument.ElectricOrgan())  # Korrigiert auf ElectricOrgan
    for measure in range(num_measures):
        chord_str = chord_progression[measure % len(chord_progression)]
        try:
            chord_symbol = harmony.ChordSymbol(chord_str)
        except Exception as e:
            print(f"Fehler beim Erstellen von ChordSymbol für '{chord_str}': {e}")
            continue  # Überspringen Sie den aktuellen Akkord und fahren Sie fort

        chord_pitches = [p.nameWithOctave for p in chord_symbol.pitches]
        # Wähle eine zufällige Note aus den Akkordnoten
        melody_note = note.Note(random.choice(chord_pitches))
        melody_note.duration = duration.Duration(1.0)  # Viertelnoten
        melody_note.volume.velocity = 80
        melody.append(melody_note)
    return melody

# Funktion zur Generierung der Basslinie basierend auf Akkordnoten
def generate_bass_section(num_measures, chord_progression):
    bass = stream.Part()
    bass.id = 'Bass'
    bass.append(instrument.ElectricBass())
    for i in range(num_measures):
        chord_str = chord_progression[i % len(chord_progression)]
        try:
            chord_symbol = harmony.ChordSymbol(chord_str)
            root = chord_symbol.root()
            bass_note = note.Note(root, octave=2)
            bass_note.duration = duration.Duration(1.0)  # Viertelnoten
            bass_note.volume.velocity = 100
            bass.append(bass_note)
        except Exception as e:
            print(f"Fehler beim Erstellen von ChordSymbol für Bassnote '{chord_str}': {e}")
            continue  # Überspringen Sie den aktuellen Akkord und fahren Sie fort
    return bass

# Funktion zur Generierung der Akkorde
def generate_chords_section(num_measures, chord_progression):
    chords_part = stream.Part()
    chords_part.id = 'Chords'
    chords_part.append(instrument.ElectricGuitar())
    for i in range(num_measures):
        chord_str = chord_progression[i % len(chord_progression)]
        try:
            chord_symbol = harmony.ChordSymbol(chord_str)
            chord_symbol.duration = duration.Duration(4.0)
            chords_part.append(chord_symbol)
        except Exception as e:
            print(f"Fehler beim Erstellen von ChordSymbol für '{chord_str}': {e}")
            continue  # Überspringen Sie den aktuellen Akkord und fahren Sie fort
    return chords_part

# Funktion zur Generierung der Strings
def generate_strings_section(num_measures, scale_obj, chord_progression):
    strings = stream.Part()
    strings.id = 'Strings'
    strings.append(instrument.StringInstrument())
    pitch_range = scale_obj.getPitches('C3', 'C5')
    for i in range(num_measures):
        chord_str = chord_progression[i % len(chord_progression)]
        try:
            chord_symbol = harmony.ChordSymbol(chord_str)
            string_chord = Chord(chord_symbol.pitches)  # Korrigiert auf Chord
            string_chord.duration = duration.Duration(4.0)
            string_chord.volume.velocity = 60
            strings.append(string_chord)
        except Exception as e:
            print(f"Fehler beim Erstellen von ChordSymbol für '{chord_str}': {e}")
            continue  # Überspringen Sie den aktuellen Akkord und fahren Sie fort
    return strings

# Funktion zur Generierung des Techno-Beats
def generate_techno_beat_section(num_measures, start_measure):
    drums = stream.Part()
    drums.id = 'Drums'
    drums.insert(0, instrument.Percussion())
    drums.insert(0, clef.PercussionClef())
    drums.insert(0, meter.TimeSignature('4/4'))

    for measure in range(num_measures):
        measure_offset = (start_measure + measure) * 4.0
        for beat in range(4):
            # Kick Drum auf jedem Beat
            kick = note.Unpitched()
            kick.ps = 35  # Standard Kick Drum MIDI Program Number
            kick.duration = duration.Duration(1.0)
            kick.volume.velocity = 90
            kick.offset = measure_offset + beat
            drums.append(kick)
            # Snare auf dem 2. und 4. Beat
            if beat in [1, 3]:
                snare = note.Unpitched()
                snare.ps = 38  # Standard Snare Drum MIDI Program Number
                snare.duration = duration.Duration(1.0)
                snare.volume.velocity = 80
                snare.offset = measure_offset + beat
                drums.append(snare)
            # Hi-Hat auf jedem halben Beat
            for sub_beat in range(2):
                hihat = note.Unpitched()
                hihat.ps = 42  # Closed Hi-Hat MIDI Program Number
                hihat.duration = duration.Duration(0.5)
                hihat.volume.velocity = 70
                hihat.offset = measure_offset + beat + (sub_beat * 0.5)
                drums.append(hihat)
            # Zusätzliche Percussion wie Claps auf dem 2. und 4. Beat
            if beat in [1, 3]:
                clap = note.Unpitched()
                clap.ps = 39  # Handclap MIDI Program Number
                clap.duration = duration.Duration(1.0)
                clap.volume.velocity = 80
                clap.offset = measure_offset + beat
                drums.append(clap)
        # Optional: Crash Cymbal alle 4 Takte
        if (measure + start_measure) % 4 == 3:
            crash = note.Unpitched()
            crash.ps = 49  # Crash Cymbal MIDI Program Number
            crash.duration = duration.Duration(1.0)
            crash.volume.velocity = 85
            crash.offset = measure_offset + 3
            drums.append(crash)
    # Setzen des MIDI-Kanals für Percussion
    for n in drums.recurse().notes:
        n.channel = 9  # General MIDI Percussion Channel
    return drums

# Funktion zur Generierung eines Drum-Fill-Ins
def generate_fill_in(num_measures, start_measure):
    fill = stream.Part()
    fill.id = 'DrumFill'
    for measure in range(num_measures):
        measure_offset = (start_measure + measure) * 4.0
        for beat in [0, 1, 2, 3]:
            snare = note.Unpitched()
            snare.ps = 38  # Snare Drum
            snare.duration = duration.Duration(0.5)
            snare.volume.velocity = 80
            snare.offset = measure_offset + beat * 0.5
            fill.append(snare)
    # Setzen des MIDI-Kanals für Percussion
    for n in fill.recurse().notes:
        n.channel = 9  # General MIDI Percussion Channel
    return fill

# ================== GUI-Klasse ==================

class SongGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Song Generator")
        master.geometry("400x250")
        
        self.soundfont_path = None
        self.current_midi_file = None
        self.fs = None  # FluidSynth instance
        self.play_thread = None
        self.is_playing = False

        # SoundFont Auswahl
        self.select_sf_button = tk.Button(master, text="SoundFont auswählen", command=self.select_soundfont)
        self.select_sf_button.pack(pady=10)

        # Play Button
        self.play_button = tk.Button(master, text="Play", command=self.play_song, state=tk.DISABLED)
        self.play_button.pack(pady=5)

        # Stop Button
        self.stop_button = tk.Button(master, text="Stop", command=self.stop_song, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Next Button
        self.next_button = tk.Button(master, text="Next", command=self.generate_and_play, state=tk.DISABLED)
        self.next_button.pack(pady=5)
        
        # Status Label
        self.status_label = tk.Label(master, text="Bitte wählen Sie eine SoundFont-Datei aus.")
        self.status_label.pack(pady=10)

    def select_soundfont(self):
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine SoundFont-Datei aus",
            filetypes=[("SoundFont Dateien", "*.sf2")]
        )
        if file_path:
            self.soundfont_path = file_path
            self.status_label.config(text=f"Ausgewählte SoundFont: {os.path.basename(file_path)}")
            self.play_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Keine SoundFont-Datei ausgewählt.")
            self.play_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)

    def generate_and_play(self):
        if self.is_playing:
            self.stop_song()
        self.status_label.config(text="Generiere neuen Song...")
        self.master.update_idletasks()
        # Generiere neuen Song
        self.generate_song()
        # Spiele den neuen Song ab
        self.play_song()

    def generate_song(self):
        # Generiere den Song
        self.generate_piece()
        self.status_label.config(text="Song generiert und bereit zur Wiedergabe.")

    def play_song(self):
        if not self.current_midi_file:
            messagebox.showerror("Fehler", "Kein MIDI-File zum Abspielen vorhanden.")
            return
        if not self.soundfont_path:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine SoundFont-Datei aus.")
            return
        if self.is_playing:
            messagebox.showinfo("Info", "Ein Song wird bereits abgespielt.")
            return
        # Starten der Wiedergabe in einem separaten Thread
        self.play_thread = threading.Thread(target=self.play_midi)
        self.play_thread.start()

    def play_midi(self):
        self.is_playing = True
        self.status_label.config(text="Wiedergabe läuft...")
        try:
            if not self.fs:
                self.fs = fluidsynth.Synth()
                # Starten von FluidSynth mit dem entsprechenden Treiber
                # "alsa" für Linux, "coreaudio" für macOS, "dsound" für Windows
                driver = "dsound" if os.name == 'nt' else "alsa"
                # Für macOS könnte es erforderlich sein, den Treiber auf "coreaudio" zu setzen
                if sys.platform == 'darwin':
                    driver = "coreaudio"
                self.fs.start(driver=driver)
                sfid = self.fs.sfload(self.soundfont_path)
                self.fs.program_select(0, sfid, 0, 0)  # Kanal 0, SoundFont 0, Preset 0
            # Laden und Abspielen des MIDI-Files
            self.fs.play_midi(self.current_midi_file)
        except AttributeError as ae:
            messagebox.showerror("Fehler", f"Fehler beim Abspielen des Songs: {ae}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Abspielen des Songs: {e}")
        self.is_playing = False
        self.status_label.config(text="Wiedergabe beendet.")
        if self.fs:
            self.fs.delete()
            self.fs = None

    def stop_song(self):
        if self.fs:
            try:
                self.fs.stop()
                self.fs.delete()
                self.fs = None
                self.is_playing = False
                self.status_label.config(text="Wiedergabe gestoppt.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Stoppen des Songs: {e}")
        else:
            self.status_label.config(text="Keine Wiedergabe läuft.")

    def generate_piece(self):
        # Generieren des gesamten Stücks
        s = stream.Stream()
        s.insert(0, tempo.MetronomeMark(number=BPM))
        s.insert(0, meter.TimeSignature(random.choice(time_signature_options)))  # Zufällige Taktart auswählen

        sections = ['intro', 'verse', 'chorus', 'verse', 'bridge', 'chorus', 'outro']
        total_measures = 0

        melody = stream.Part()
        chords = stream.Part()
        bass = stream.Part()
        strings = stream.Part()
        drums = stream.Part()

        for section in sections:
            key_signature, scale_obj = get_random_key_and_scale()
            chord_progression = get_random_chord_progression(section)

            # Einfügen der Tonart an der richtigen Position
            s.insert(total_measures * 4, key_signature)

            # Generieren der einzelnen Abschnitte
            melody_section = generate_melody_section(SECTION_MEASURES, scale_obj, chord_progression)
            melody.append(melody_section)

            chords_section = generate_chords_section(SECTION_MEASURES, chord_progression)
            chords.append(chords_section)

            bass_section = generate_bass_section(SECTION_MEASURES, chord_progression)
            bass.append(bass_section)

            strings_section = generate_strings_section(SECTION_MEASURES, scale_obj, chord_progression)
            strings.append(strings_section)

            drums_section = generate_techno_beat_section(SECTION_MEASURES, total_measures)
            if section in ['chorus', 'outro']:
                fill = generate_fill_in(2, total_measures + SECTION_MEASURES)
                drums.append(fill)  # Fügen Sie das Fill-In hinzu
            drums.append(drums_section)

            total_measures += SECTION_MEASURES

        # Instrumentenzuweisungen
        melody.insert(0, instrument.ElectricOrgan())  # Korrigiert auf ElectricOrgan
        chords.insert(0, instrument.ElectricGuitar())
        bass.insert(0, instrument.ElectricBass())
        strings.insert(0, instrument.StringInstrument())

        # Hinzufügen aller Parts zum Hauptstream
        s.insert(0, drums)
        s.insert(0, strings)
        s.insert(0, bass)
        s.insert(0, chords)
        s.insert(0, melody)

        # Dateiname mit Zeitstempel generieren
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        midi_filename = f'Song_{GENRE}_{current_time}.mid'
        self.current_midi_file = os.path.join(os.getcwd(), midi_filename)

        # MIDI-Datei speichern
        try:
            s.write('midi', fp=self.current_midi_file)
            print(f"The piece was successfully saved as '{midi_filename}' in {os.getcwd()}.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Error saving MIDI file: {e}")

# ================== Hauptfunktion ==================

def main():
    root = tk.Tk()
    gui = SongGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
