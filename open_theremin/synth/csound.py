import ctcsound
from random import randint, random

def midi2pch(num):
    "Convert MIDI Note Numbers to Csound PCH format"
    return "%d.%02g" % (3 + (num / 12), num % 12)

class Note(object):
    def __init__(self, *args):
        self.pfields = list(args)

    def __str__(self):
        retVal = "i"
        for i in range(len(self.pfields)):
            if(i == 4):
                retVal += " " + midi2pch(self.pfields[i])
            else:
                retVal += " " + str(self.pfields[i])
        return retVal

class RandomLine(object):
    def __init__(self, base, range):
        self.curVal = 0.0
        self.reset()
        self.base = base
        self.range = range

    def reset(self):
        self.dur = randint(64,256)
        self.end = random()
        self.increment = (self.end - self.curVal) / self.dur
    
    def getValue(self):
        self.dur -= 1
        if(self.dur < 0):
            self.reset()
        retVal = self.curVal
        self.curVal += self.increment
        return self.base + (self.range * retVal)

def createChannel(channelName):
    chn,_ = c.channelPtr(channelName,
            ctcsound.CSOUND_CONTROL_CHANNEL | ctcsound.CSOUND_INPUT_CHANNEL)
    return chn

class ChannelUpdater(object):
    def __init__(self, channelName, updater):
        self.updater = updater
        self.channel = createChannel(channelName)

    def update(self):
        self.channel[0] = self.updater.getValue()


# Our Orchestra for our project
orc = """
sr=44100
ksmps=32
nchnls=2
0dbfs=1

instr 1 
kamp chnget "amp"
kfreq chnget "freq"
kres chnget "resonance"
kfiltfreq chnget "filtfreq"
printk 0.5, kamp
printk 0.5, kfreq
printk 0.5, kres
aout vco2 kamp, kfreq 
aout moogladder aout, kfiltfreq, kres
outs aout, aout
endin
"""

c = ctcsound.Csound()    # create an instance of Csound
c.setOption("-odac")  # Set option for Csound
c.setOption("-m7")
c.setOption("-b -64")
c.compileOrc(orc)     # Compile Orchestra from String

sco = "i1 0 60\n"

c.readScore(sco)     # Read in Score generated from notes 

c.start()             # When compiling from strings, this call is necessary before doing any performing

channels = [ChannelUpdater("amp", RandomLine(.4, .2)),
            ChannelUpdater("freq", RandomLine(400, 80)),
            ChannelUpdater("resonance", RandomLine(0.4, .3)),
            ChannelUpdater("filtfreq", RandomLine(2000, 1000))]

for chn in channels:
    chn.update()

# The following is our main performance loop. We will perform one block of sound at a time 
while (c.performKsmps() == 0):
    for chn in channels:
        chn.update()

c.reset()
