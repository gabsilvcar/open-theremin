from multiprocessing import Process, Value
from ctypes import c_double
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
import ctcsound


class Synthesizer:
    def __init__(self, freq_value, volume_value):
        self.freq_value = freq_value
        self.volume_value = volume_value

    def run(self):
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
               aout vco2 kamp, kfreq
               outs aout, aout
               endin"""

        self.c.setOption("-odac")
        self.c.compileOrc(orc)
        self.c.readScore("i1 0 60")
        self.c.start()

        while self.c.performKsmps() == 0:
            # Update frequency and volume from shared values
            self.c.setControlChannel("freq", self.freq_value.value)
            self.c.setControlChannel("volume", self.volume_value.value)

        self.c.stop()


class SynthTestWindow(QMainWindow):
    def __init__(self, freq_value, volume_value):
        super().__init__()

        self.freq_value = freq_value
        self.volume_value = volume_value

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

    def update_frequency(self):
        self.freq_value.value = self.freq_slider.value()

    def update_volume(self):
        # Convert slider value (0-100) to volume (0-1)
        self.volume_value.value = self.volume_slider.value() / 100.0


if __name__ == "__main__":
    freq_value = Value(c_double, 440.0)  # Shared frequency value
    volume_value = Value(c_double, 0.5)  # Shared volume value

    app = QApplication(sys.argv)
    window = SynthTestWindow(freq_value, volume_value)
    window.show()

    # Create and start the Synthesizer process
    synth_process = Process(target=Synthesizer(freq_value, volume_value).run)
    synth_process.start()

    sys.exit(app.exec())

    synth_process.join()
