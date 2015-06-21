import logging
logger = logging.getLogger(__name__)

import itertools as it
import operator as op

import numpy as np
from numpy.core.defchararray import isspace as numpy_isspace

import music as mu
import util as ut

modifier_handlers = ut.HandlersByRegex({
    r"^=(?P<degree>[abcdefg])(?P<accidental>[b#])?(?P<octave>\d)?$": lambda **kwargs: dict(pitch=mu.get_pitch(**kwargs)),
})

def parse_row_modifiers(row):
    row_info = dict()
    for modifier in row.split():
        try:
            row_info.update(modifier_handlers[modifier])
        except KeyError:
            logger.warning("ignoring malformed row modifier %s" % repr(modifier))
            continue
    return row_info

def matrix_rows(array):
    return ["".join(row) for row in array]

def infer_pitches(pitches):
    pitches = list(pitches)
    inferred_pitches = list(pitches)
    try:
        i_pitch0 = [pitch is not None for pitch in pitches].index(True)
    except ValueError:
        i_pitch0 = 0
        inferred_pitches[i_pitch0] = 0
    for i in xrange(i_pitch0, 0, -1):
        inferred_pitches[i - 1] = inferred_pitches[i] - 1
    for i in xrange(i_pitch0 + 1, len(pitches)):
        if inferred_pitches[i] is None:
            inferred_pitches[i] = inferred_pitches[i - 1] + 1
    if any(inferred_pitch != pitch
           for inferred_pitch, pitch
           in zip(inferred_pitches, pitches)
           if pitch is not None):
        raise ValueError("inferred pitches %s do not match explicit pitches %s" % (inferred_pitches, pitches))
    return inferred_pitches

def parse_rows_modifiers(matrix):
    row_metas = [parse_row_modifiers(row) for row in matrix_rows(matrix)]
    inferred_pitches = infer_pitches(map(op.methodcaller("get", "pitch"), row_metas))
    for row_meta, inferred_pitch in zip(row_metas, inferred_pitches):
        row_meta["pitch"] = inferred_pitch
    return row_metas

def parse_piano_roll(matrix, row_metas, t0):
    voices = {}
    voices_last_t = {}
    for t in xrange(matrix.shape[1]):
        for i in xrange(matrix.shape[0]):
            c = matrix[i, t]
            if c.isalpha():
                name = c.lower()
                # should be: if voices[name].get_duration() < t0, pad
                if name not in voices:
                    voices[name] = mu.Sequence(notes=[], name=name)
                last_t = voices_last_t.get(name, 0)
                if last_t < t - 1:
                    voices[name].append(mu.Rest(duration=t - last_t),
                                        try_tie=True)
                voices_last_t[name] = t
                voices[name].append(mu.Note(pitch=row_metas[i]["pitch"],
                                            duration=1),
                                    try_tie=c.islower())
    return voices

def parse_matrix(string, beats_per_bar=4):
    rows = [row.strip() for row in string.strip().splitlines()]
    columns = list(it.izip_longest(*rows, fillvalue=" "))
    matrix = np.array(columns, dtype="string").T
    # time starts at leftmost dot
    i_t0 = list(np.any(matrix == ".", axis=0)).index(True)
    # now back up while not all whitespace (to get any lead-in)
    i_spaces = np.nonzero(np.all(numpy_isspace(matrix[:, :i_t0]), axis=0))[0]
    i_note0 = i_spaces[-1] if i_spaces else 0
    # what comes before that is row modifiers
    row_metas = parse_rows_modifiers(matrix[:, :i_note0])
    # what comes after it is piano roll
    voices = parse_piano_roll(matrix[:, i_note0:], row_metas, i_note0 - i_t0)
    voices = [mu.Sequence(name=k, notes=v) for k, v in voices.iteritems()]
    return voices
