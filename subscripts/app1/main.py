# coding:utf-8

import numpy as np
import struct
import pyaudio
import wave
#import matplotlib.pyplot as plt


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout


class MainWidget(Widget):

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.List = [["sin_a_1", "sin_hz_1", "cos_a_1", "cos_hz_1"],
                        ["sin_a_2", "sin_hz_2", "cos_a_2", "cos_hz_2"],
                        ["sin_a_3", "sin_hz_3", "cos_a_3", "cos_hz_3"],
                        ["sin_a_4", "sin_hz_4", "cos_a_4", "cos_hz_4"],
                        ["sin_a_5", "sin_hz_5", "cos_a_5", "cos_hz_5"],
                        ["sin_a_6", "sin_hz_6", "cos_a_6", "cos_hz_6"],
                        ["sin_a_7", "sin_hz_7", "cos_a_7", "cos_hz_7"],
                        ["sin_a_8", "sin_hz_8", "cos_a_8", "cos_hz_8"],
                        ["sin_a_9", "sin_hz_9", "cos_a_9", "cos_hz_9"],
                        ["sin_a_10", "sin_hz_10", "cos_a_10", "cos_hz_10"],]

        self.Rate = int(self.ids["rate_input"].text)
        self.Time = float(self.ids["time_input"].text)
        self.Flg = False

    def startWave(self):
        self.Rate = int(self.ids["rate_input"].text)
        self.Time = float(self.ids["time_input"].text)
        x = np.arange(0, self.Time, 1/self.Rate)

        self.saveWave = np.zeros(len(x))
        tmp_wave = []
        for i in range(10):
            sin_a = float(self.ids[self.List[i][0]].text)
            sin_hz = float(self.ids[self.List[i][1]].text)
            cos_a = float(self.ids[self.List[i][2]].text)
            cos_hz = float(self.ids[self.List[i][3]].text)

            tmp_wave = sin_a * np.sin(2*np.pi*sin_hz*x)
            tmp_wave += cos_a * np.cos(2*np.pi*cos_hz*x)

            self.saveWave += tmp_wave

        self.normal2bite()

        p = pyaudio.PyAudio()
        stream = p.open(    format=pyaudio.paInt16,
                            channels=1,
                            rate=self.Rate,
                            frames_per_buffer=1024,
                            input=False,
                            output=True)

        stream.write(self.data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.Flg = True



    def save(self):
        if self.Flg:
            import datetime
            todaydateil = datetime.datetime.today()
            fileName = str(todaydateil.strftime("%Y%m%d_%H_%M_%S"))
            fileName = "./save/{}.wav".format(fileName)

            wf = wave.open(fileName, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.Rate)
            wf.writeframes(self.data)
            wf.close()


    def normal2bite(self):
        ampAbs = np.absolute(self.saveWave)
        ampMax = np.amax(ampAbs)

        if ampMax >= 1.0:
            self.saveWave /= ampMax

        self.data = [int(x * 32767.0) for x in self.saveWave]
        self.data = struct.pack("h" * len(self.data), *self.data)


class MainApp(App):

    def build(self):
        mainWidget = MainWidget()
        return mainWidget


if __name__ == "__main__":
    MainApp().run()
