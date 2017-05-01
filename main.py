import tkinter.filedialog
import tkinter.ttk
import time
import threading
import ping_lib
import socket_test_lib
import os
import rclick_menu


class PingLooper(object):
    def __init__(self):
        self.running = False
        self.delay = "5"
        self.net_address = "127.0.0.1"
        self.output_path = os.path.join(os.path.expanduser('~'))
        self.output_filename = self.net_address + " ping log.csv"
        self.output_full_path = os.path.join(self.output_path, self.output_filename)
        self.log_file = None
        self.log_on_response = False
        self.log_on_non_response = False
        self.looper_thread = None
        self.ping_fire = False
        self.ping_fire_counter = 0
        self.ping_fire_delay = int(self.delay) * 60
        self.check_mode_socket = False

    def set_full_path(self, input_path):
        self.output_path = os.path.dirname(input_path)
        self.output_filename = os.path.basename(input_path)
        self.output_full_path = input_path

    def set_new_filename(self, file_name):
        self.output_filename = file_name
        self.output_full_path = os.path.join(self.output_path, self.output_filename)

    def _looper_logic(self):
        self.running = True
        self.ping_fire = False
        self.ping_fire_counter = 0
        self.ping_fire_delay = int(self.delay) * 60

        def _ping():
            self._write_log_entry(ping_lib.ping(self.net_address))

        def _socket_test():
            self._write_log_entry(socket_test_lib.socket_connect(self.net_address, socket_test_port.get()))

        def threaded_check():
            if not self.check_mode_socket:
                self.ping_thread = threading.Thread(target=_ping)
                self.ping_thread.start()
            else:
                self.socket_thread = threading.Thread(target=_socket_test())
                self.socket_thread.start()

        while self.running:
            self.ping_fire_counter += 1
            set_status_bar("Running, " + str(self.ping_fire_delay - self.ping_fire_counter) +
                           " seconds until next ping")
            if self.ping_fire_counter == self.ping_fire_delay:
                self.ping_fire = True
            if self.ping_fire:
                threaded_check()
                self.ping_fire = False
                self.ping_fire_counter = 0
            time.sleep(1)
        self.close_log_file()

    def toggle_run(self):
        if self.running:
            self.cancel()
        else:
            self.run()

    def run(self):
        state_toggle_button.configure(text="Stop")
        select_file_button.configure(state='disabled')
        log_on_response_checkbutton.configure(state='disabled')
        log_on_non_response_checkbutton.configure(state='disabled')
        test_mode_ping_radiobutton.configure(state='disabled')
        test_mode_socket_radiobutton.configure(state='disabled')
        for child in address_frame.winfo_children():
            child.configure(state='disabled')
        for child in test_mode_frame.winfo_children():
            child.configure(state='disabled')
        address_input.unbind("<3>")
        self.create_log_file()
        self.looper_thread = threading.Thread(target=self._looper_logic)
        self.looper_thread.start()
        set_status_bar("Running")
        while self.looper_thread.is_alive():
            time.sleep(0.1)
            root_window.update()
        state_toggle_button.configure(text="Start")
        address_input.bind("<3>", right_click_address_input)
        for child in address_frame.winfo_children():
            child.configure(state='normal')
        for child in test_mode_frame.winfo_children():
            child.configure(state='normal')
        log_on_response_checkbutton.configure(state='normal')
        log_on_non_response_checkbutton.configure(state='normal')
        delay_spinbutton.configure(state='readonly')
        socket_test_port.configure(state='readonly')
        state_toggle_button.configure(state='disabled')
        select_file_button.configure(state='enabled')
        set_status_bar("Run finished, please select log file")

    def cancel(self):
        self.running = False
        state_toggle_button.configure(text='Cancelling')

    def create_log_file(self):
        try:
            self.log_file = open(self.output_full_path, "wb")
        except IOError:
            return False
        self.log_file.write("Date and Time,Tested Address,Host Response\r\n".encode())
        return True

    def _write_log_entry(self, state):
        if state is True and self.log_on_response is True or state is False and self.log_on_non_response is True:
            self.log_file.write((str(time.strftime("%Y-%m-%d %H:%M:%S")) + "," +
                                 looper_job.net_address + "," + str(state) + "\r\n").encode())

    def close_log_file(self):
        self.log_file.close()


class FileSelection(object):
    def __init__(self):
        self.file_selection = looper_job.output_path
        self.output_path_proposed = ''

    def select_file(self):
        name_output_file()
        self.output_path_proposed = tkinter.filedialog.asksaveasfilename(
            initialdir=looper_job.output_path,
            initialfile=looper_job.output_filename,
            filetypes=[("CSV File", "*.csv")])
        if os.path.exists(os.path.dirname(self.output_path_proposed)):
            looper_job.set_full_path(self.output_path_proposed)
        else:
            return
        if os.path.exists(looper_job.output_path):
            state_toggle_button.configure(state='enabled')
            set_status_bar("Press start to ping server on schedule")


looper_job = PingLooper()
file_selector = FileSelection()


def set_delay():
    looper_job.delay = int(delay_spinbutton.get())


def log_success_checkbutton_callback():
    looper_job.log_on_response = log_on_response_checkbutton_var.get()
    if not looper_job.log_on_response and not looper_job.log_on_non_response:
        log_on_response_checkbutton.toggle()
        looper_job.log_on_response = log_on_response_checkbutton_var.get()
    else:
        select_file_button.configure(state=tkinter.NORMAL)


def log_non_success_checkbutton_callback():
    looper_job.log_on_non_response = log_on_non_response_checkbutton_var.get()
    if not looper_job.log_on_response and not looper_job.log_on_non_response:
        log_on_non_response_checkbutton.toggle()
        looper_job.log_on_non_response = log_on_non_response_checkbutton_var.get()
    else:
        select_file_button.configure(state=tkinter.NORMAL)


def set_status_bar(input_text):
    status_bar.configure(text=input_text)


def name_output_file():
    looper_job.set_new_filename(address_input.get() + " ping log.csv")


def set_mode_socket():
    looper_job.check_mode_socket = test_mode_variable.get()


def set_host_callback(input_address):
    looper_job.net_address = input_address.get()


root_window = tkinter.Tk()
root_window.title("Simple Ping Watchdog")
root_window.resizable(width=False, height=False)

status_bar_text = tkinter.StringVar(root_window)

address_frame = tkinter.ttk.Frame(root_window)
address_frame.grid(row=10, column=10, columnspan=20, sticky=tkinter.W + tkinter.E)

address_input_var = tkinter.StringVar()
address_input = tkinter.ttk.Entry(address_frame, textvariable=address_input_var)
address_input_var.trace("w", lambda name, index, mode,
                        anonymous_address_input_var=address_input_var: set_host_callback(anonymous_address_input_var))

address_input.insert(0, looper_job.net_address)
address_input.pack(side=tkinter.LEFT, fill='x', expand=True)
right_click_address_input = rclick_menu.RightClickMenu(address_input)
address_input.bind("<3>", right_click_address_input)

delay_label = tkinter.ttk.Label(address_frame, text="Minutes")
delay_label.pack(side=tkinter.RIGHT)

delay_spinbutton = tkinter.Spinbox(address_frame, from_=1, to_=9999, width=4, justify=tkinter.RIGHT)
delay_spinbutton.delete(0, "end")
delay_spinbutton.insert(0, 5)
delay_spinbutton.configure(state="readonly", command=set_delay)
delay_spinbutton.pack(side=tkinter.RIGHT)

log_on_response_checkbutton_var = tkinter.BooleanVar()
log_on_response_checkbutton_var.set(looper_job.log_on_response)
log_on_response_checkbutton = tkinter.Checkbutton(root_window,
                                                  text="Log on Response",
                                                  variable=log_on_response_checkbutton_var,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  command=log_success_checkbutton_callback)
log_on_response_checkbutton.grid(row=15, column=10)

log_on_non_response_checkbutton_var = tkinter.BooleanVar()
log_on_non_response_checkbutton_var.set(looper_job.log_on_non_response)
log_on_non_response_checkbutton = tkinter.Checkbutton(root_window,
                                                      text="Log on Non-Response",
                                                      variable=log_on_non_response_checkbutton_var,
                                                      onvalue=True,
                                                      offvalue=False,
                                                      command=log_non_success_checkbutton_callback)
log_on_non_response_checkbutton.grid(row=15, column=20)

test_mode_frame = tkinter.Frame(root_window)
test_mode_frame.grid(row=17, column=10, columnspan=20, sticky=tkinter.W)

test_mode_variable = tkinter.BooleanVar()
test_mode_variable.set(False)
test_mode_ping_radiobutton = tkinter.Radiobutton(test_mode_frame,
                                                 variable=test_mode_variable,
                                                 value=False,
                                                 text="Ping",
                                                 command=set_mode_socket)
test_mode_socket_radiobutton = tkinter.Radiobutton(test_mode_frame,
                                                   variable=test_mode_variable,
                                                   value=True,
                                                   text="Socket",
                                                   command=set_mode_socket)
test_mode_ping_radiobutton.pack(side=tkinter.LEFT)
test_mode_socket_radiobutton.pack(side=tkinter.LEFT)
tkinter.ttk.Label(test_mode_frame, text="Port=").pack(side=tkinter.LEFT)
socket_test_port = tkinter.Spinbox(test_mode_frame, from_=1, to_=65535, width=5, justify=tkinter.RIGHT)
socket_test_port.delete(0, "end")
socket_test_port.insert(0, 80)
socket_test_port.configure(state="readonly", command=set_delay)
socket_test_port.pack(side=tkinter.RIGHT)

state_toggle_button = tkinter.ttk.Button(root_window)
state_toggle_button.configure(text="GO", command=looper_job.toggle_run, state='disabled')
state_toggle_button.grid(row=20, column=10)

select_file_button = tkinter.ttk.Button(root_window)
select_file_button.configure(text="Select Log File", command=file_selector.select_file, state=tkinter.DISABLED)
select_file_button.grid(row=20, column=20)

status_bar = tkinter.ttk.Label(root_window)
set_status_bar("Please select log file")
status_bar.grid(row=30, column=10, columnspan=100)

root_window.mainloop()
