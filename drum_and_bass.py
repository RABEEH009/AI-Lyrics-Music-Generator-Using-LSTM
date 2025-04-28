# Import necessary libraries
import pretty_midi
import numpy as np

def add_instruments_to_melody(input_path, output_path, theme, mood, style):
    """
    Add drum and bass tracks to a melody MIDI file and save the result.

    Args:
        input_path (str): Path to the input melody MIDI file.
        output_path (str): Path to save the output MIDI file with drums and bass.
        theme (str): Song theme (e.g., 'love', 'adventure').
        mood (str): Song mood (e.g., 'happy', 'melancholic').
        style (str): Song style (e.g., 'pop', 'rock').
    """
    # Try to load the input MIDI file
    try:
        midi = pretty_midi.PrettyMIDI(input_path)
    except Exception as e:
        raise Exception(f"Failed to load MIDI file {input_path}: {e}")

    # Set tempo depending on the style
    tempo = {
        'pop': 120,        # 120 BPM for pop
        'rock': 140,       # 140 BPM for rock
        'classical': 100   # 100 BPM for classical
    }.get(style, 120)      # Default is 120 BPM if style not found

    # Calculate beat and measure durations
    beat_duration = 60.0 / tempo          # Duration of one beat in seconds
    measure_duration = beat_duration * 4  # 4 beats per measure (common time)

    # Find the total duration of the melody
    melody_end = 0
    if midi.instruments:
        melody_end = max([note.end for note in midi.instruments[0].notes], default=0)

    if melody_end == 0:
        raise Exception("No notes found in the input melody MIDI file.")

    # ------------------ DRUM TRACK ------------------

    # Create a drum instrument (uses MIDI channel 10 for drums)
    drum_instrument = pretty_midi.Instrument(program=0, is_drum=True)

    # Define drum patterns based on style
    drum_patterns = {
        'pop': [
            (36, 100, 0.0),  # Kick drum on beat 1
            (42, 80, 0.0),   # Hi-hat
            (42, 80, 0.5),   # Hi-hat at beat 0.5
            (38, 100, 1.0),  # Snare drum on beat 2
            (42, 80, 1.0),   
            (42, 80, 1.5),
            (36, 100, 2.0),  # Kick again at beat 3
            (42, 80, 2.0),
            (42, 80, 2.5),
            (38, 100, 3.0),  # Snare again on beat 4
            (42, 80, 3.0),
            (42, 80, 3.5),
        ],
        'rock': [
            (36, 110, 0.0),  # Stronger kick for rock
            (42, 90, 0.0),
            (42, 90, 0.5),
            (38, 110, 1.0),  # Stronger snare
            (46, 90, 1.0),   # Open hi-hat
            (36, 110, 2.0),
            (42, 90, 2.0),
            (42, 90, 2.5),
            (38, 110, 3.0),
            (42, 90, 3.0),
        ],
        'classical': [
            (41, 80, 0.0),   # Very light drums for classical (Floor tom)
            (41, 80, 2.0),
        ]
    }

    # Get the drum pattern for the style, default to pop if not available
    drum_pattern = drum_patterns.get(style, drum_patterns['pop'])

    # Add drum notes throughout the melody duration
    current_time = 0.0
    while current_time < melody_end:
        for pitch, velocity, offset in drum_pattern:
            start_time = current_time + offset * beat_duration
            if start_time >= melody_end:
                break
            # Create a short drum note
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=pitch,
                start=start_time,
                end=start_time + beat_duration / 4  # Short hit
            )
            drum_instrument.notes.append(note)
        current_time += measure_duration

    # Add the drum instrument to the MIDI
    midi.instruments.append(drum_instrument)

    # ------------------ BASS TRACK ------------------

    # Create a bass instrument (Electric Bass = MIDI program 33)
    bass_instrument = pretty_midi.Instrument(program=33)

    # Define bass patterns based on mood
    bass_pattern = {
        'happy': [0.0, 2.0],                # Play bass on beats 1 and 3
        'melancholic': [0.0],               # Play bass only on beat 1
        'energetic': [0.0, 1.0, 2.0, 3.0]    # Play bass on every beat
    }.get(mood, [0.0, 2.0])                 # Default is [0, 2] if mood not found

    # Get the melody notes (assume first instrument is melody)
    melody_notes = midi.instruments[0].notes

    current_time = 0.0
    melody_idx = 0
    while current_time < melody_end and melody_idx < len(melody_notes):
        # Move to the current melody note based on time
        while melody_idx < len(melody_notes) and melody_notes[melody_idx].start < current_time:
            melody_idx += 1
        if melody_idx >= len(melody_notes):
            break

        # Take the pitch from the current melody note
        pitch = melody_notes[melody_idx].pitch
        bass_pitch = pitch - 12  # One octave lower

        # If pitch too low, bring it up
        if bass_pitch < 36:  # C1 is around MIDI 36
            bass_pitch += 12

        # Add bass notes based on bass pattern
        for offset in bass_pattern:
            start_time = current_time + offset * beat_duration
            if start_time >= melody_end:
                break
            note = pretty_midi.Note(
                velocity=90,
                pitch=bass_pitch,
                start=start_time,
                end=start_time + beat_duration  # Bass notes longer
            )
            bass_instrument.notes.append(note)

        current_time += measure_duration

    # Add the bass instrument to the MIDI
    midi.instruments.append(bass_instrument)

    # ------------------ SAVE FINAL MIDI FILE ------------------

    # Save the new MIDI file with drums and bass
    midi.write(output_path)