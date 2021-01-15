import base64
import io

import subprocess

import cv2
import numpy


class Shell:
    def __init__(self):
        self.proc = None
        self.iow = None
        self.ow = None

    def __enter__(self):
        self.proc = subprocess.Popen("adb shell",
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL,
                                     bufsize=-1)
        self.iow = io.TextIOWrapper(self.proc.stdin)
        self.ow = io.TextIOWrapper(self.proc.stdout)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.iow.close()
        self.ow.close()
        self.proc.kill()

    def wait(self):
        while self.ow.readline().rstrip():
            pass

    def get_an_image(self):
        self.iow.write("screencap -p | busybox base64\n")
        self.iow.flush()

        self.wait()

        data = self.ow.readline().rstrip()
        while len(data) % 76 == 0:
            data += self.ow.readline().rstrip()

        return cv2.imdecode(numpy.frombuffer(base64.b64decode(data), numpy.uint8), cv2.IMREAD_COLOR)

    def touch(self, point):
        self.iow.write("input tap {} {}\n".format(*point))
        self.iow.flush()
        self.wait()

    def sleep(self, time):
        self.iow.write("sleep {}\n".format(time))
        self.iow.flush()
        self.wait()
