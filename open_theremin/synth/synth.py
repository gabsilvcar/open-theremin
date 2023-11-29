import threading
from functools import reduce

import ctcsound


class Synth(object):
    ####################################
    #
    # Configuracao
    #

    input_csd = ""

    audio_to_speaker = True
    speaker_device_name = ""

    output_file = "out.wav"

    out_buffer_size = 64  # Se houver latencia, diminuir,
    # Se o audio falhar (Buffer underrun), aumentar.
    # Deve ser sempre maior ou igual que o ksmps.
    # Usar sempre potencias de 2.
    # O valor real eh esse * ksmps.

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
        self.message_out = (
            2
            + (1 if self.message_note_amplitude else 0)
            + (4 if self.message_warnings else 0)
            + (128 if self.message_benchmark_info else 0)
        )

        # Inicializacao
        self.cs = ctcsound.Csound()
        self.cs.setDebug(self.debug)
        self.cs.setOption("-odac")  # Set option for Csound
        self.cs.setOption("-m" + str(self.message_out))  # Set option for Csound
        self.cs.setOption("-b -" + str(self.out_buffer_size))

        # Configuracao inicial da Orquestra
        orcSettings = (
            "ksmps="
            + str(self.ksmps)
            + "\n"
            + """
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
        )
        self.cs.compileOrc(orcSettings)

        # Configura Canais de Controle
        self.channels = dict()

        self.cs.setControlChannel("freq", 110)
        self.channels["freq"] = [self.__normalizeFreq, 110]

        self.cs.setControlChannel("ampt", 0.6)

        self.cs.setControlChannel("filtfreq", 1100)
        self.channels["filtfreq"] = [self.__normalizeFiltFreq, 1100]

        self.cs.setControlChannel("filtresl", 0.6)
        self.channels["filtres"] = [self.__normalizeFiltResl, 0.6]

        # self.cs.setControlChannel("vibrfreq", 15)
        # self.cs.setControlChannel("vibrampt", 1.01)

    def __del__(self):
        del self.cs

    """
        Auxilliary methods
    """

    def __normalizeFreq(self, value):
        return 55 + 880 * value

    def __normalizeFiltFreq(self, value):
        return 500 + 3000 * value

    def __normalizeFiltResl(self, value):
        return 1 - 2 * value

    """
        Thread do perform csound... :)
    """

    class PerformanceThread(threading.Thread):
        def __init__(self, csound, channels):
            threading.Thread.__init__(self)
            self.__stop_event = threading.Event()
            self.cs = csound
            self.out_buffer_size = self.cs.outputBufferSize() / self.cs.ksmps()
            self.channels = channels
            self.chnIntervals = {
                key: [
                    self.cs.controlChannel(key)[0],
                    self.cs.controlChannel(key)[0],
                    0.0,
                ]
                for key in self.channels.keys()
            }

        def stop(self):
            self.__stop_event.set()

        def stopped(self):
            return self.__stop_event.is_set()

        def run(self):
            counter = self.out_buffer_size
            self.__updateChannels()
            while self.cs.performKsmps() == 0:
                if counter == 1:
                    self.__updateChannels()
                    counter = self.out_buffer_size
                else:
                    for key in self.channels.keys():
                        chnInterval = self.chnIntervals[key]
                        chnInterval[0] += chnInterval[2]
                        self.cs.setControlChannel(key, chnInterval[0])
                        self.chnIntervals[key] = chnInterval
                    counter -= 1

        def __updateChannels(self):
            for key in self.channels.keys():
                chnInterval = self.chnIntervals[key]
                chnInterval[0] = chnInterval[1]
                self.cs.setControlChannel(key, chnInterval[0])
                chnInterval[1] = self.channels[key][1]
                self.chnIntervals[key] = self.__findInterpolationStep(chnInterval)

        def __findInterpolationStep(self, chnInterval):
            step = (chnInterval[1] - chnInterval[0]) / self.out_buffer_size
            chnInterval[2] = step
            return chnInterval

    def sendChannelUpdate(self, chn, value):
        self.channels[chn][1] = self.channels[chn][0](value)

    def startPerformance(self, duration):
        self.cs.readScore("i1 0 {}\n".format(duration))
        self.cs.start()
        self.thread = self.PerformanceThread(self.cs, self.channels)
        self.thread.start()

    def stopPerformance(self):
        self.thread.stop()
        self.thread.join()
        self.cs.reset()
