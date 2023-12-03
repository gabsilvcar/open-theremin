# Run the application
import sys
from ctypes import c_double
from multiprocessing import Value, Process

from PyQt6.QtWidgets import QApplication

from open_theremin.interface import MainWindow
from open_theremin.synth.synthesizer import Synthesizer, SynthTestWindow

freq_value = Value(c_double, 0)  # Shared frequency value
volume_value = Value(c_double, 0.5)  # Shared volume value

app = QApplication(sys.argv)
main_window = MainWindow(freq_value, volume_value)
main_window.show()

synth_process = Process(target=Synthesizer(freq_value, volume_value).run)
synth_process.start()

sys.exit(app.exec())

synth_process.join()
