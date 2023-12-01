# Run the application
import sys

from PyQt6.QtWidgets import QApplication

from open_theremin.interface import MainWindow
from open_theremin.synth.synth import Synth

app = QApplication(sys.argv)
synth = Synth()
synth.startPerformance(20)


main_window = MainWindow(synth)
main_window.show()
sys.exit(app.exec())
