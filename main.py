import re
import collections
import copy
import fluidsynth
import itertools as it
import logging
import time

logging.basicConfig()
logger = logging.getLogger(__name__)

import music as mu
import matrix as mx
import events as ev

melodies = mx.parse_matrix("""=e5  .  . zz  .
                              =c5 z. z.  .  .
                              =a4  zz zz .  .
                              =g4  .  .  . zz""")
channels = dict(z=0)

events = []
for i in xrange(4):
    # repeat every four three-beat bars
    t = i * 3 * 4
    for melody in melodies:
        channel = channels[melody.name]
        events.extend(melody.get_events(channel, t))

def sortfun(event):
    if isinstance(event, ev.NoteOff):
        # ensure noteoffs occur before noteons so that new noteons
        # are not immediately cancelled.
        return event.time - 1e-5
    else:
        return event.time
events.sort(key=sortfun)

fs = fluidsynth.Synth()
fs.start(driver="alsa")

kbhstrings = fs.sfload("/home/tim/SF/strings/kbh-strings.sf2")
florestan_woodwinds = fs.sfload("/home/tim/SF/wind/Woodwinds/florestan_woodwinds.sf2")

instruments = dict(
    strings=(kbhstrings, 0, 0),
    bassoon=(florestan_woodwinds, 0, 70),
)

fs.program_select(0, *instruments["strings"])
fs.program_select(1, *instruments["strings"])

bpm = 140
beat_duration = 60.0/bpm
t = events[0].time
for event in events:
    dt = event.time - t
    if dt > 0:
        time.sleep(dt * beat_duration)
    t = event.time
    logger.warn("event %s from %s" % (event, event.source))
    event.occur(fs)

fs.delete()
