# coding:utf-8

import sys
import pyaudio
import subprocess
import os
import struct
import wave

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from kivy.properties import BooleanProperty, NumericProperty


class SoundWidget(Widget):
    # 音声合成時の利用パラメータ
    pitch_var = NumericProperty(2.0)
    voice_switch = BooleanProperty(False)


    def __init__(self, **kwargs):
        super(SoundWidget, self).__init__(**kwargs)
        # スクリプトの絶対パスを入手
        self.dir = os.path.dirname(os.path.abspath(__name__))
        # それに対してSPTKを結合
        self.path = self.dir + "\SPTK\\bin"
        # 一時保存フォルダ。まだ使う予定がない。
        self.saveDir = "./save/filename"

        # 音声系の基礎設定
        self.chunk = 1024 * 8
        self.rate = 16000
        self.channels = 1

        # 録音用
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(  format=pyaudio.paInt16,
                                    channels=self.channels,
                                    rate=self.rate,
                                    input=True,
                                    output=True,
                                    frames_per_buffer=self.chunk)

        # 使用(しないこともある)コマンド群
        self.gwaves = self.get_cmd("gwaves")
        self.xgr = self.get_cmd("xgr")
        self.raw2wav = self.get_cmd("rawtowav")
        self.bcut = self.get_cmd("bcut")
        self.x2x = self.get_cmd("x2x")
        self.pitch = self.get_cmd("pitch")
        self.frame = self.get_cmd("frame")
        self.window = self.get_cmd("window")
        self.mcep = self.get_cmd("mcep")
        self.sopr = self.get_cmd("sopr")
        self.excite = self.get_cmd("excite")
        self.mlsadf = self.get_cmd("mlsadf")
        self.clip = self.get_cmd("clip")

        # 一時保存のファイル群
        self.raw_file = "./save/tmp.raw"
        self.pitch_file = "./save/tmp.pitch"
        self.mcep_file = "./save/tmp.mcep"

        Clock.schedule_interval(self.update, 1.0/60.0)


    def get_cmd(self, cmd):
        command = self.path + "\{cmd}.exe".format(cmd=cmd)
        return command


    def call_cmd(self, cmd):
        subprocess.call(cmd, shell=True)


    def record(self):
        fp = open(self.raw_file, "wb")
        data = self.stream.read(self.chunk)
        fp.write(data)
        fp.close()


    def extract_pitch(self):
        cmd = "{x2x} +sf {raw_file} | {pitch} -a 1 -s 16 -p 80 > {pitch_file}".format(x2x=self.x2x, raw_file=self.raw_file, pitch=self.pitch, pitch_file=self.pitch_file)
        self.call_cmd(cmd)


    def extract_mcep(self):
        cmd = "{x2x} +sf {raw_file} | {frame} -p 80 | {window} | {mcep} -m 25 -a 0.42 > {mcep_file}".format(x2x=self.x2x, raw_file=self.raw_file, frame=self.frame, window=self.window, mcep=self.mcep, mcep_file=self.mcep_file)
        self.call_cmd(cmd)


    def change_pitch_voice(self):
        cmd = "{sopr} -m {pitch_var} {pitch_file} | {excite} -p 80 | {mlsadf} -m 25 -a 0.1 -p 80 {mcep_file} | {clip} -y -32000 32000 | {x2x} +fs > {raw_file}".format(sopr=self.sopr, pitch_file=self.pitch_file, pitch_var=self.pitch_var, excite=self.excite, mlsadf=self.mlsadf, mcep_file=self.mcep_file, clip=self.clip, x2x=self.x2x, raw_file=self.raw_file)
        self.call_cmd(cmd)


    def play(self):
        f = open(self.raw_file, "rb")
        data = f.read()
        f.close()
        self.stream.write(data)


    def start_voice_change(self):
        if self.voice_switch:
            self.record()
            self.extract_pitch()
            self.extract_mcep()
            self.change_pitch_voice()
            self.play()


    def switch(self):
        if self.voice_switch:
            self.voice_switch = False
        else:
            self.voice_switch = True


    def down_pitch(self):
        self.pitch_var -= 0.1
        if self.pitch_var <= 0:
            self.pitch_var = 0.0
        self.pitch_var = round(self.pitch_var, 2)


    def up_pitch(self):
        self.pitch_var += 0.1
        if self.pitch_var >= 2.0:
            self.pitch_var = 2.0
        self.pitch_var = round(self.pitch_var, 2)


    def update(self, dt):
        self.start_voice_change()



class SoundApp(App):

    def build(self):
        soundWidget = SoundWidget()
        return SoundWidget()


if __name__ == "__main__":
    SoundApp().run()
