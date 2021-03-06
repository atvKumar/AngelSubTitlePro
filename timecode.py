from math import floor

class TimeCode(object):

    def __init__(self, Timecode="00:00:00:00"):  # Default Variables
        self.framerate = 25
        self.frames = 0
        self.hrs = 0
        self.mins = 0
        self.secs = 0
        self.ms = 0
        self.frms = 0
        # self.timecode = "00:00:00:00"
        self.setTimeCode(Timecode)

    def setFrameRate(self, framerate):
        self.framerate = framerate

    def getFrameRate(self):
        return self.framerate

    def setHours(self, hours):
        self.hrs = hours

    def getHours(self):
        return self.hrs

    def setMins(self, mins):
        self.mins = mins

    def getMins(self):
        return self.mins

    def setSecs(self, secs):
        if isinstance(secs, float):
            sec, ms = str(secs).split(".")
            self.secs = int(sec)
            self.ms = int(ms)
            frames = self.msToFrames(self.ms)
            self.frames = frames + (self.secs * self.framerate)
            self.frames_to_tc()
            self.timecode = self.getTimeCode()
        elif isinstance(secs, int):
            self.secs = secs
            self.frames = secs * self.framerate
            self.frames_to_tc()
            self.timecode = self.getTimeCode()

    def getSecs(self):
        return self.secs

    def setFrames(self, frames):
        self.frames = frames
        self.frames_to_tc()

    def getFrames(self):
        return self.frms

    def setTimeCode(self, timecode):
        self.timecode = timecode
        self.parseTimeCode()

    def getTimeCode(self):
        return f"{self.hrs:02}:{self.mins:02}:{self.secs:02}:{self.frms:02}"

    def parseTimeCode(self):
        if len(self.timecode) == 11:
            self.hrs = int(self.timecode[0:2])
            self.mins = int(self.timecode[3:5])
            self.secs = int(self.timecode[6:8])
            self.frms = int(self.timecode[9:11])
            self.tc_to_frames()

    def tc_to_frames(self):
        self.frames = (((self.hrs * 3600) + (self.mins * 60) + self.secs) * self.framerate) + self.frms

    def frames_to_tc(self):
        self.hrs = self.frames // (3600 * self.framerate)
        self.mins = (self.frames % (3600 * self.framerate)) // (60 * self.framerate)
        self.secs = ((self.frames % (3600 * self.framerate)) % (60 * self.framerate)) // self.framerate
        self.frms = ((self.frames % (3600 * self.framerate)) % (60 * self.framerate)) % self.framerate
        self.timecode = self.getTimeCode()
    
    def secs_to_tc(self, secs):  # Adapted from http://www.gummydev.com/timecode/
        total_seconds = max(0, round(secs))
        seconds = total_seconds % 60
        minutes = floor(total_seconds / 60) % 60
        hours = floor(total_seconds / (60*60))
        frames = self.msToFrames(str(secs).split(".")[1])
        self.timecode = f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"
    
    def get_mstc(self):
        return f"{self.hrs:02}:{self.mins:02}:{self.secs:02},{self.framesToMs(self.frms):03}"

    def msToFrames(self, ms):
        return int(round(float(self.framerate) / 1000 * float(ms)))
    
    def framesToMs(self, frames):
        return int(round(float(frames) *  1000 / float(25)))

    def __str__(self):
        return self.timecode

    def __add__(self, other):
        rtn = TimeCode()
        total_frames = 0
        if isinstance(other, TimeCode):
            total_frames = self.frames + other.frames
        elif isinstance(other, int):
            total_frames = self.frames + other
        rtn.setFrames(total_frames)
        return rtn

    def __sub__(self, other):
        rtn = TimeCode()
        total_frames = 0
        if isinstance(other, TimeCode):
            total_frames = self.frames - other.frames
        elif isinstance(other, int):
            total_frames = self.frames - other
        rtn.setFrames(total_frames)
        return rtn

    def __mul__(self, other):
        rtn = TimeCode()
        total_frames = 0
        if isinstance(other, int):
            total_frames = self.frames * other
        rtn.setFrames(total_frames)
        return rtn

    def __truediv__(self, other):
        rtn = TimeCode()
        total_frames = 0
        if isinstance(other, int):
            total_frames = self.frames // other
        rtn.setFrames(total_frames)
        return rtn

    def __repr__(self):
        return self.timecode


# inTime = TimeCode("01:21:31:23")
# outTime = TimeCode("12:31:23:12")
# print(outTime - inTime)
# 11:09:51:14
