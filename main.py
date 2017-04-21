import tkinter.ttk
import time
import threading
import ping_lib
import os


class Logger(object):
    def __init__(self):
        self.output_path = os.path.join(os.getcwd(), "log.csv")
        self.log_file = None
        self.log_on_response = False
        self.log_on_non_response = False

    def open_log_file(self):
        try:
            self.log_file = open(self.output_path, "wb")
        except IOError:
            return False
        return True

    def write_log_entry(self, state):
        if state is True and self.log_on_response is True or state is False and self.log_on_non_response is True:
            self.log_file.write((str(time.localtime()) + "," + str(state)).encode())

    def close_log_file(self):
        self.log_file.close()


class PingLooper(object):
    def __init__(self):
        self.running = False
        self.delay = "5"
        self.net_address = "127.0.0.1"
        self.log_file_path = ""

    def _looper_logic(self):
        self.running = True
        log_file.open_log_file()
        go_button.configure(state='disabled')
        cancel_button.configure(state='enabled')
        ping_fire = False
        ping_fire_counter = 0
        while self.running:
            ping_fire_counter += 1
            if ping_fire_counter == int(self.delay) * 60:
                ping_fire = True
            if ping_fire:
                log_file.write_log_entry(ping_lib.ping(self.net_address))
                ping_fire = False
                ping_fire_counter = 0
            else:
                print("dead_loop_test" + str(ping_fire_counter))
            time.sleep(1)
        log_file.close_log_file()
        go_button.configure(state='enabled')
        cancel_button.configure(state='disabled')

    def run(self):
        looper_thread = threading.Thread(target=self._looper_logic)
        looper_thread.start()
        while looper_thread.is_alive():
            root_window.update()

    def cancel(self):
        self.running = False

looper_job = PingLooper()
log_file = Logger()


def set_delay():
    looper_job.delay = int(delay_spinbutton.get())
root_window = tkinter.Tk()

address_input = tkinter.ttk.Entry(root_window)
address_input.insert(0, looper_job.net_address)
address_input.grid(row=10, column=10)

delay_spinbutton = tkinter.Spinbox(root_window, from_=1, to_=9999)
delay_spinbutton.delete(0, "end")
delay_spinbutton.insert(0, 5)
delay_spinbutton.configure(state="readonly", command=set_delay)
delay_spinbutton.grid(row=10, column=20)

go_button = tkinter.ttk.Button(root_window)
go_button.configure(text="GO", command=looper_job.run)
go_button.grid(row=20, column=10)

cancel_button = tkinter.ttk.Button(root_window)
cancel_button.configure(text="Cancel", command=looper_job.cancel, state='disabled')
cancel_button.grid(row=20, column=20)

root_window.mainloop()
