from PySide2.QtWidgets import QWidget, QMenu, QAction, QFileDialog, QVBoxLayout
from PySide2.QtCore import Signal
import numpy as _np
import pyqtgraph as pg
from os.path import splitext, dirname, join, basename, exists, abspath
import wave, subprocess, sys
from time import sleep
from videoPanel import resource_path

FFMPEG = resource_path("utils/ffmpeg")

class waveform(QWidget):
    file_loaded = Signal(str)
    def __init__(self, parent=None):
        super(waveform, self).__init__(parent)
        self._waveFile = {'path': "",
                          'framerate': "",
                          'nchannels': "",
                          'sample_width': "",
                          'nframes': ""}
        layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.pw = pg.PlotWidget()
        self.pw.plot([-0.1, 0.1], pen='b')
        layout.addWidget(self.pw)
        self.selectionCtrl = pg.LinearRegionItem([50,10000])
        self.selectionCtrl.setZValue(-10)
        self.loadAudioAction = QAction("Load Audio File (*.wav)", self)
        self.loadAudioAction.triggered.connect(self.load_wavFile)
        self.extAudioAction = QAction("Extract Audio File (*.wav)", self)
        self.extAudioAction.triggered.connect(self.extract_wavFile)
        self.selectRegion = QAction("Select Region", self)
        self.selectRegion.triggered.connect(self.activateRegion)
        self.remSelection = QAction("Disable Selection", self)
        self.remSelection.triggered.connect(self.deactivateRegion)

    def contextMenuEvent(self, event):
        # print("Right Clicked!", event)
        menu = QMenu(self)
        menu.addAction(self.loadAudioAction)
        menu.addAction(self.extAudioAction)
        menu.addAction(self.selectRegion)
        menu.addAction(self.remSelection)
        menu.exec_(event.globalPos())
    
    def _wav2array(self, nchannels, sampwidth, data):  # From wavio https://github.com/WarrenWeckesser/wavio/blob/master/wavio.py
        """data must be the string containing the bytes from the wav file."""
        num_samples, remainder = divmod(len(data), sampwidth * nchannels)
        if remainder > 0:
            raise ValueError('The length of data is not a multiple of '
                            'sampwidth * num_channels.')
        if sampwidth > 4:
            raise ValueError("sampwidth must not be greater than 4.")

        if sampwidth == 3:
            a = _np.empty((num_samples, nchannels, 4), dtype=_np.uint8)
            raw_bytes = _np.frombuffer(data, dtype=_np.uint8)
            a[:, :, :sampwidth] = raw_bytes.reshape(-1, nchannels, sampwidth)
            a[:, :, sampwidth:] = (a[:, :, sampwidth - 1:sampwidth] >> 7) * 255
            result = a.view('<i4').reshape(a.shape[:-1])
        else:
            # 8 bit samples are stored as unsigned ints; others as signed ints.
            dt_char = 'u' if sampwidth == 1 else 'i'
            a = _np.frombuffer(data, dtype='<%s%d' % (dt_char, sampwidth))
            result = a.reshape(-1, nchannels)
        return result

    def open_wavFile(self, audiofile):
        self._waveFile['path'] = audiofile
        _wav = wave.open(self._waveFile['path'])
        # print("Loading ", self._waveFile['path'])
        self._waveFile['framerate'] = _wav.getframerate()
        self._waveFile['nchannels'] = _wav.getnchannels()
        self._waveFile['sample_width'] = _wav.getsampwidth()
        self._waveFile['nframes'] = _wav.getnframes()
        data = self._wav2array(self._waveFile['nchannels'], 
                                self._waveFile['sample_width'], 
                                _wav.readframes(self._waveFile['nframes']))
        _wav.close()
        return data
        del data

    def processAudio(self, data):
        if self._waveFile['nchannels'] == 2:
            _mL = data[:,0] # Vertical Slice L
            _mR = data[:,1] # Vertical Slice R
            left_mono_track = _mL[::100].copy()  # Filter 100th Sample
            right_mono_track = _mR[::100].copy()
            left_mono_track = left_mono_track.astype(float)  # Convert to float
            right_mono_track = right_mono_track.astype(float)  # Convert to float
            left_mono_track /= _np.max(_np.abs(left_mono_track), axis=0) # normalise to -1 - 1
            left_mono_track *= 0.05
            left_mono_track += 0.05  # Shift Up
            right_mono_track /= _np.max(_np.abs(right_mono_track), axis=0) # normalise to -1 - 1
            right_mono_track *= 0.05
            right_mono_track += -0.05  # Shift Down
            return left_mono_track, right_mono_track

    def plotWaveform(self, left, right):
        self.pw.getPlotItem().clear()
        self.pw.setYRange(min=-0.5, max=0.5)
        self.pw.plot(left, pen='b')
        self.pw.plot(right, pen='b')

    def loadPlot_audioFile(self, audioFileName):
        data = self.open_wavFile(audioFileName)
        # print(data)
        left_mono_track, right_mono_track = self.processAudio(data)
        del data  # Delete from Memory
        self.plotWaveform(left_mono_track, right_mono_track)
        self.file_loaded.emit(f"{audioFileName} Loaded!")
    
    def load_wavFile(self):
        file_dialog = QFileDialog(self, "Open Project")
        file_dialog.setNameFilter("Audio File (*.wav)")
        file_dialog.setDefaultSuffix("wav")
        selected_file, valid = file_dialog.getOpenFileName()
        if valid:
            filename, ext = splitext(selected_file)
            if ext == ".wav":
                self.loadPlot_audioFile(selected_file)
    
    def extract_wavFile(self):
        video_file = self.parent().parent().getVideoFilePath()
        if video_file:
            print(f"[Debug] - Extracting Audio from {video_file}")
            if sys.platform == 'darwin':
                video_file = str(video_file).replace(' ', '\ ')
            out_waveFile = join(dirname(video_file), splitext(basename(video_file))[0]+".wav")
            # cmd = f"ffmpeg -i {video_file} -af \"pan=stereo|c0=c0|c1=c0\" -acodec pcm_s16le -ac 2 {out_waveFile}"
            cmd = f"{FFMPEG} -i {video_file} -filter_complex \"[0:a]channelsplit=channel_layout=mono\" -acodec pcm_s16le -ac 2 {out_waveFile}"
            print(f"[Debug] - {cmd}")
            s = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, err = s.communicate()
            s.wait(30)
            if exists(out_waveFile) == True:
                print(f"[Debug] - Extraction Completed - {out_waveFile}")
                self.loadPlot_audioFile(out_waveFile)
            else:
                print("[Error] -", err)  # Filename with spaces still spits out Error

    def activateRegion(self):
        self.pw.addItem(self.selectionCtrl)
    
    def deactivateRegion(self):
        self.pw.removeItem(self.selectionCtrl)
    
    def getTotalAudioFrames(self):
        return self._waveFile['nframes']