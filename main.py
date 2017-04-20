import tkinter
import tkinter.ttk
import time
import threading
import ping_lib


class PingLooper(object):
    def __init__(self):
        self.running = False
        self.delay = "5"
        self.net_address = "127.0.0.1"
        self.log_file_path = ""

    def _looper_logic(self):
        self.running = True
        ping_fire = False
        ping_fire_counter = 0
        while self.running:
            ping_fire_counter += 1
            if ping_fire_counter == int(self.delay) * 60:
                ping_fire = True
            if ping_fire:
                if ping_lib.ping(self.net_address):
                    print("Host Present")
                else:
                    print("Host Not Present")
                ping_fire = False
                ping_fire_counter = 0
            else:
                print("dead_loop_test" + str(ping_fire_counter))
            time.sleep(1)

    def run(self):
        self._looper_logic()

looper_test = PingLooper()
looper_test.delay = 1
looper_test.run()
