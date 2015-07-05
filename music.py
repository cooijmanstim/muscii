import copy

import util as ut
import events as ev

class Transformable(object):
    def transform(self, transformation):
        transformation(self)

    def transformed(self, transformation):
        other = copy.deepcopy(self)
        other.transform(transformation)
        return other

class Transformation(object):
    def __call__(self, transformable):
        raise NotImplementedError()

class HasPitch(Transformable):
    def __init__(self, pitch=0, **kwargs):
        super(HasPitch, self).__init__(**kwargs)
        self.pitch = pitch

class HasDuration(Transformable):
    def __init__(self, duration=0, **kwargs):
        super(HasDuration, self).__init__(**kwargs)
        self.duration = duration

    def compute_duration(self):
        return self.duration

class HasTime(Transformable):
    def __init__(self, time=0, **kwargs):
        super(HasTime, self).__init__(**kwargs)
        self.time = time

class MaybeNamed(object):
    def __init__(self, name=None, **kwargs):
        super(MaybeNamed, self).__init__(**kwargs)
        self.name = name

class Note(HasPitch, HasDuration, ut.DefaultEqualityMixin):
    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)

    def get_events(self, channel, t0):
        return [ev.NoteOn(channel=channel, pitch=self.pitch, time=t0),
                ev.NoteOff(channel=channel, pitch=self.pitch, time=t0 + self.duration)]

    def __repr__(self):
        return ("Note(pitch=%i, duration=%i)"
                % (self.pitch, self.duration))

class Rest(HasDuration, ut.DefaultEqualityMixin):
    def __init__(self, **kwargs):
        super(Rest, self).__init__(**kwargs)

    def get_events(self, channel, t0):
        return []

    def __repr__(self):
        return "Rest(duration=%i)" % self.duration

class Shift(Transformation):
    def __init__(self, attr, delta, **kwargs):
        super(Transformation, self).__init__(**kwargs)
        self.attr = attr
        self.delta = delta

    def __call__(self, note):
        if hasattr(note, self.attr):
            setattr(note, self.attr, getattr(note, self.attr) + self.delta)

class Scale(Transformation):
    def __init__(self, attr, scale, **kwargs):
        super(Transformation, self).__init__(**kwargs)
        self.attr = attr
        self.scale = scale

    def __call__(self, note):
        if hasattr(note, self.attr):
            setattr(note, self.attr, getattr(note, self.attr) * self.scale)

class Sequence(MaybeNamed, ut.DefaultEqualityMixin):
    def __init__(self, notes=[], **kwargs):
        super(Sequence, self).__init__(**kwargs)
        self.notes = []
        self.extend(notes)

    def __iter__(self):
        return iter(self.notes)

    def __len__(self):
        return len(self.notes)

    def append(self, note, try_tie=False):
        if try_tie and self.notes:
            try:
                self.notes[-1] = tie(self.notes[-1], note)
                return
            except InvalidTieError:
                pass
        self.notes.append(note)

    def extend(self, notes):
        for note in notes:
            self.append(note)

    def transform(self, transformation):
        for note in self.notes:
            note.transform(transformation)

    def get_events(self, channel, t0=0):
        events = []
        for note in self.notes:
            events.extend(note.get_events(channel, t0))
            t0 += note.compute_duration()
        return events

    def compute_duration(self):
        return sum(note.compute_duration() for note in self.notes)

    def __repr__(self):
        return "Sequence(%s)" % ", ".join((["name=%s" % self.name] if self.name else [])
                                          + list(map(repr, self.notes)))

class Tie(Sequence):
    def __init__(self, *notes, **kwargs):
        super(Tie, self).__init__(notes=notes, **kwargs)

    def __repr__(self):
        return "Tie(%s)" % ", ".join(map(repr, self.notes))

    def append(self, note):
        if isinstance(note, Tie):
            self.extend(note.notes)
        else:
            if not isinstance(note, Note):
                raise InvalidTieError(self, note)
            if self.notes and self.notes[-1].pitch == note.pitch:
                self.notes[-1].duration += note.duration
            else:
                self.notes.append(note)

    # TODO: override get_events

def tie(a, b):
    if isinstance(a, Tie) or isinstance(b, Tie):
        return Tie(a, b)
    if isinstance(a, Rest) and isinstance(b, Rest):
        a.duration += b.duration
        return a
    if isinstance(a, Note) and isinstance(b, Note):
        if a.pitch == b.pitch:
            a.duration += b.duration
            return a
        else:
            return Tie(a, b)
    raise InvalidTieError(a, b)

class InvalidTieError(RuntimeError):
    def __init__(self, *notes):
        super(InvalidTieError, self).__init__(
            """Can't tie notes %s""" % (notes,))
        self.notes = notes

class InsufficientInformationError(RuntimeError):
    pass

def get_pitch(octave=None, degree=None, accidental=None):
    pitch = 0
    if octave is not None: pitch += 12*get_octave(octave=octave)
    if degree is not None: pitch += get_pitch_klass(degree=degree)
    if accidental is not None: pitch += get_accidental(accidental=accidental)
    return pitch

def get_octave(octave=None):
    if octave is not None:
        if isinstance(octave, basestring):
            return int(octave)
        else:
            return octave
    raise InsufficientInformationError()

def get_pitch_klass(degree=None):
    if degree is not None:
        return "c d ef g a b".index(degree)
    raise InsufficientInformationError()

def get_accidental(accidental=None):
    if accidental is not None:
        if isinstance(accidental, basestring):
            return "b*#".index(accidental) - 1
        else:
            return accidental
    raise InsufficientInformationError()
