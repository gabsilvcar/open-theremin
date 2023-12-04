import sys
from ctypes import c_double, c_int
from multiprocessing import Process, Value

import ctcsound
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class Synthesizer:
    def __init__(self, freq_value, volume_value, waveform_value):
        self.freq_value = freq_value
        self.volume_value = volume_value
        self.waveform_value = waveform_value
        self.current_wave = waveform_value.value

    def run(self):
        while True:
            self.load()

    def load(self):
        self.c = ctcsound.Csound()

        # Orchestra definition
        orc = """
               sr=44100
               ksmps=32
               nchnls=2
               0dbfs=1

               instr 1 
               kamp chnget "volume"
               kfreq chnget "freq"
               aout oscili kamp, kfreq
               outs aout, aout
               endin

               instr 2 
               kamp chnget "volume"
               kfreq chnget "freq"
               aout vco2 kamp, kfreq, 12
               outs aout, aout
               endin
                       
               instr 3
               kamp chnget "volume"
               kfreq chnget "freq"
               aout vco2 kamp, kfreq, 10
               outs aout, aout
               endin       
               """

        self.c.setOption("-odac")
        self.c.compileOrc(orc)
        self.c.readScore(f"i{self.current_wave} 0 60")
        self.c.start()

        while self.c.performKsmps() == 0:
            if self.waveform_value.value != self.current_wave:
                self.current_wave = self.waveform_value.value
                break

            # self.c.setControlChannel("wave", "oscili")
            # Update frequency and volume from shared values

            self.c.setControlChannel("freq", self.freq_value.value)
            self.c.setControlChannel("volume", self.volume_value.value)

        self.c.stop()


class SynthTestWindow(QMainWindow):
    def __init__(self, freq_value, volume_value, waveform_value):
        super().__init__()

        self.freq_value = freq_value
        self.volume_value = volume_value
        self.waveform_value = waveform_value

        # Create a vertical layout widget
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create frequency slider
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setMinimum(20)
        self.freq_slider.setMaximum(2000)
        self.freq_slider.setValue(440)  # Default frequency
        self.freq_slider.valueChanged.connect(self.update_frequency)
        layout.addWidget(self.freq_slider)

        # Create volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)  # Default volume (50%)
        self.volume_slider.valueChanged.connect(self.update_volume)
        layout.addWidget(self.volume_slider)

        # Create waveform selection dropdown
        self.waveform_selection = QComboBox()
        self.waveform_selection.addItem("Sine Wave", 1)
        self.waveform_selection.addItem("Triangle Wave", 2)
        self.waveform_selection.addItem("Square Wave", 3)
        self.waveform_selection.currentIndexChanged.connect(self.update_waveform)
        layout.addWidget(self.waveform_selection)

    def update_frequency(self):
        self.freq_value.value = self.freq_slider.value()

    def update_volume(self):
        # Convert slider value (0-100) to volume (0-1)
        self.volume_value.value = self.volume_slider.value() / 100.0

    def update_waveform(self, index):
        # Update the waveform value
        self.waveform_value.value = self.waveform_selection.currentData()


if __name__ == "__main__":
    freq_value = Value(c_double, 440.0)  # Shared frequency value
    volume_value = Value(c_double, 0.5)  # Shared volume value
    waveform_value = Value(c_int, 1)  # Shared waveform type (default to sine wave)

    app = QApplication(sys.argv)
    window = SynthTestWindow(freq_value, volume_value, waveform_value)
    window.show()

    # Create and start the Synthesizer process
    synth_process = Process(
        target=Synthesizer(freq_value, volume_value, waveform_value).run
    )
    synth_process.start()

    sys.exit(app.exec())

    synth_process.join()
