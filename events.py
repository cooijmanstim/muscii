class HasSource(object):
    def __init__(self, source=None, **kwargs):
        super(HasSource, self).__init__(**kwargs)
        self.source = source

class Event(HasSource):
    def __init__(self, channel, time, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.channel = channel
        self.time = time

    def occur(self, fs):
        raise NotImplementedError()

class NoteOn(Event):
    def __init__(self, pitch, velocity=100, **kwargs):
        super(NoteOn, self).__init__(**kwargs)
        self.pitch = pitch
        self.velocity = velocity

    def occur(self, fs):
        fs.noteon(self.channel, self.pitch, self.velocity)

    def __repr__(self):
        return ("NoteOn(pitch=%i, velocity=%i, channel=%i, time=%i)"
                % (self.pitch, self.velocity, self.channel, self.time))

class NoteOff(Event):
    def __init__(self, pitch, **kwargs):
        super(NoteOff, self).__init__(**kwargs)
        self.pitch = pitch

    def occur(self, fs):
        fs.noteoff(self.channel, self.pitch)

    def __repr__(self):
        return ("NoteOff(pitch=%i, channel=%i, time=%i)"
                % (self.pitch, self.channel, self.time))

