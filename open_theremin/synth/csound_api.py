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

    ksmps = 128  # Valores menores resultam em uma melhor qualidade
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
        self.cs.setOption('-m' + str(message_out))
        self.cs.setOption('-b -' + str(self.io_buffer_size))
        if self.audio_to_speaker:
            self.cs.setOption('-odac' + speaker_setting)
        else:
            self.cs.setOption('-o ' + self.output_file)

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
        #self.cs.perform()
        #self.cs.reset()

    def stopPerformance(self):
        #self.thread.stop()
        #self.thread.join()
        self.cs.reset()

synth = Synth()

synth.startPerformance()
