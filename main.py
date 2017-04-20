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
        looper_thread = threading.Thread(self._looper_logic())
        looper_thread.start()
        while looper_thread.is_alive():
            root_window.update()

    def cancel(self):
        self.running = False

looper_test = PingLooper()
looper_test.delay = 1
# looper_test.run()

root_window = tkinter.Tk()

go_button = tkinter.ttk.Button(root_window)
go_button.configure(text="GO", command=looper_test.run)
go_button.grid(row=0, column=0)

cancel_button = tkinter.ttk.Button(root_window)
cancel_button.configure(text="Cancel", command=looper_test.cancel)
cancel_button.grid(row=0, column=1)

root_window.mainloop()
