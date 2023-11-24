import threading
import time

import ctcsound

class Synth(object):

    ####################################
    #
    # Configuracao
    #

    input_csd = ''

    audio_to_speaker = True
    speaker_device_name = ''

    output_file = 'out.wav'

    io_buffer_size = 2048 # Se houver latencia, diminuir,
                         # Se o audio falhar (Buffer underrun), aumentar.
                         # Deve ser sempre maior ou igual que o ksmps.
                         # Usar sempre potencias de 2

    ksmps = 32  # Valores menores resultam em uma melhor qualidade
                # de sintese, mas usa mais capacidade computacional.
                # Usar apenas potencias de 2.

    message_note_amplitude = False
    message_warnings = True
    message_benchmark_info = False

    debug = False

    #
    # Fim da Configuracao
    #
    ####################################

    def __init__(self):
        # Definicao de valores de inicializacao
        message_out = 2 \
            + (1 if self.message_note_amplitude else 0) \
            + (4 if self.message_warnings else 0) \
            + (128 if self.message_benchmark_info else 0)

        speaker_setting = ':' + self.speaker_device_name if self.speaker_device_name else ''

        # Inicializacao
        self.cs = ctcsound.Csound()
        self.cs.setDebug(self.debug)
        self.cs.setOption("-odac")  # Set option for Csound
        self.cs.setOption("-m7")  # Set option for Csound

        # Configuracao inicial da Orquestra
        orcSettings = \
                "ksmps=" + str(self.ksmps) + "\n" + \
                """
                sr = 44100
                nchnls=2
                0dbfs=1

                instr 1
                kfreq chnget "freq"
                kampt chnget "ampt"
                kfiltfreq chnget "filtfreq"
                kfiltresl chnget "filtresl"
                aout vco2 kampt, kfreq
                aout moogladder aout, kfiltfreq, kfiltresl
                outs aout, aout
                endin
                """
        self.cs.compileOrc(orcSettings)

        # Configura Canais de Controle
        self.cs.setControlChannel("freq", 110)
        self.cs.setControlChannel("ampt", 0.6)
        self.cs.setControlChannel("filtfreq", 1100)
        self.cs.setControlChannel("filtresl", 0.6)
        #self.cs.setControlChannel("vibrfreq", 15)
        #self.cs.setControlChannel("vibrampt", 1.01)


    def __del__(self):
        del self.cs

    def loadOrchestraStr(self, orc):
        self.cs.compileOrc(orc)

    def getControlChannel(self, chn):
        return self.cs.getControlChannel(chn)

    def setControlChannel(self, chn, value):
        self.cs.setControlChannel(chn, value)

    def startPerformance(self):
        self.cs.readScore("i1 0 120\n")
        self.cs.start()
        self.thread = ctcsound.CsoundPerformanceThread(self.cs.csound())
        self.thread.play()

        # Start a separate thread to modify the frequency over time
        self.freq_thread = threading.Thread(target=self.increase_frequency)
        self.freq_thread.start()
        #self.cs.perform()
        #self.cs.reset()

    def increase_frequency(self):
        start_freq = 110  # starting frequency
        end_freq = 880    # target frequency
        duration = 120    # duration of the increase in seconds

        for t in range(duration):
            # Calculate the new frequency
            new_freq = start_freq + (end_freq - start_freq) * t / duration
            print(new_freq)
            self.setControlChannel("freq", new_freq)
            time.sleep(1)  # wait for 1 second before updating the frequency again

    def stopPerformance(self):
        #self.thread.stop()
        #self.thread.join()
        self.cs.reset()

synth = Synth()

synth.startPerformance()
