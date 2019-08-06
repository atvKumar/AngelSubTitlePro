from PySide2.QtWidgets import QWidget, QMenu, QAction, QFileDialog, QVBoxLayout
from PySide2.QtCore import Signal
import numpy as _np
import pyqtgraph as pg
from os.path import splitext
import wave


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
        self.pw.plot([1,2,3,4], pen='b')
        layout.addWidget(self.pw)
        self.loadAudioAction = QAction("Load Audio File (*.wav)", self)
        self.loadAudioAction.triggered.connect(self.load_wavFile)

    def contextMenuEvent(self, event):
        # print("Right Clicked!", event)
        menu = QMenu(self)
        menu.addAction(self.loadAudioAction)
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
    
    def load_wavFile(self):
        file_dialog = QFileDialog(self, "Open Project")
        file_dialog.setNameFilter("Audio File (*.wav)")
        file_dialog.setDefaultSuffix("wav")
        selected_file, valid = file_dialog.getOpenFileName()
        if valid:
            filename, ext = splitext(selected_file)
            if ext == ".wav":
                self._waveFile['path'] = selected_file
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
                # print(data)
                if self._waveFile['nchannels'] > 1:
                    _mL = data[:,0] # Vertical Slice L
                    left_mono_track = _mL[::100].copy()  # Filter 100th Sample
                    del data  # Delete from Memory
                    left_mono_track = left_mono_track.astype(float)  # Convert to float
                    # _np.savetxt("/Users/promo3/Desktop/test.csv", left_mono_track ,delimiter=",")
                    # left_mono_track = _np.loadtxt("/Users/promo3/Desktop/test.csv", delimiter=",")
                    left_mono_track /= _np.max(_np.abs(left_mono_track), axis=0) # normalise to -1 - 1
                    self.pw.getPlotItem().clear()
                    self.pw.plot(left_mono_track, pen='b')
                    self.file_loaded.emit(f"{selected_file} Loaded!")