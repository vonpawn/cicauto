import os
import winsound
import win32api

AUDIO_PATH_BASE = 'cicauto/data/sounds/'


SCALE = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88,
    'C2': 523.25
}


def get_audio_path(filename):
    return os.path.join(os.getcwd(), AUDIO_PATH_BASE, filename)


def play_win(filename):
    filepath = get_audio_path(filename)
    winsound.PlaySound(filepath, winsound.SND_FILENAME)


def play_note(note_char, timings=500):
    if note_char not in SCALE.keys():
        raise ValueError(f'Unexpected note: {note_char}')
    note_freq = SCALE[note_char]
    # C, D, E, F, G, A, B, C(1 octave higher)
    # Do, Re, Mi, Fa, Sol, La, Si/Ti, Do(1 octave higher)
    # for note in [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]:
    win32api.Beep(int(note_freq + .5), timings)


def play_notes(notes: str, timings=None):
    for i, note in enumerate(notes):
        if timings:
            play_note(note.upper(), timings[i])
        else:
            play_note(note)


if __name__ == '__main__':
    play_notes('DEAD', timings=[150]*4)
