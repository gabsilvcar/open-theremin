from multiprocessing import Process, Value
from ctypes import c_double
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
import ctcsound


class Synthesizer:
    def __init__(self, freq):
       self.freq_value = freq

    def run(self):
        self.c = ctcsound.Csound()

        # Orchestra definition
        orc = """
               sr=44100
               ksmps=32
               nchnls=2
               0dbfs=1

               instr 1 
               kamp = 0.5
               kfreq chnget "freq"
               aout vco2 kamp, kfreq
               outs aout, aout
               endin"""

        self.c.setOption("-odac")
        self.c.compileOrc(orc)
        self.c.readScore("i1 0 60")
        self.c.start()
        while self.c.performKsmps() == 0:
            print(self.freq_value.value)
            # Update frequency from shared value
            self.c.setControlChannel("freq", self.freq_value.value)
        self.c.stop()


class SynthTestWindow(QMainWindow):
    def __init__(self, freq_value):
        super().__init__()

        self.freq_value = freq_value

        # Create a vertical layout widget
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create a slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(20)
        self.slider.setMaximum(2000)
        self.slider.setValue(440)  # Default frequency
        self.slider.valueChanged.connect(self.update_frequency)
        layout.addWidget(self.slider)

    def update_frequency(self):
        self.freq_value.value = self.slider.value()


if __name__ == "__main__":
    freq_value = Value(c_double, 0)  # Shared frequency value

    app = QApplication(sys.argv)
    window = SynthTestWindow(freq_value)
    window.show()

    # Create and start the Synth2 process
    synth_process = Process(target=Synthesizer(freq_value).run)
    synth_process.start()

    sys.exit(app.exec())

    synth_process.join()