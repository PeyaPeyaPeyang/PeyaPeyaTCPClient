from gui import ui_support, ui
from utils import *
from threading import Thread
from time import sleep
from client_base import Client, AbstractClient, State

try:
    from Tkinter import messagebox
except ImportError:
    from tkinter import messagebox


class UILogic(AbstractClient):
    def __init__(self, main_form):
        main_form: ui.MainForm

        self.mf = main_form
        self.client = Client(self)
        self.alive = True
        self.try_connect = False

        Thread(target=self.update_display).start()
        self.init()

    def dispose(self):
        self.alive = False
        self.client.alive = False

    def update_display(self):
        while self.alive:
            if State.DISCONNECTED in self.client.state:
                self.mf.Status.configure(text="Status: Disconnected")
                sleep(1)
                continue

            base = "Status: "

            for state in self.client.state:
                base += state.value + " |"

            base += " ↑ " + str(self.client.send_sec) + " b/s | ↓ " + str(self.client.receive_sec) + " b/s"

            self.mf.Status.configure(text=base)
            sleep(1)

    def init(self):
        form = self.mf

        form.IP.insert(1.0, "localhost")

        encoding = get_encodings()
        encoding.insert(4, "Raw")

        ui_support.send_encoding.set("Send Encoding")
        ui_support.receive_encoding.set("Receive Encoding")

        form.Send_Encoding.configure(state="readonly")
        form.Send_Encoding.configure(values=encoding)
        form.Receive_Encoding.configure(state="readonly")
        form.Receive_Encoding.configure(values=encoding)

        ui_support.port_num.set(80)
        ui_support.buffer_size.set(1024)

        form.Action.bind("<ButtonRelease-1>", self.on_action_pressed)
        form.Clear_In.bind("<ButtonRelease-1>", self.on_clear_input_pressed)
        form.Clear_Logs.bind("<ButtonRelease-1>", self.on_clear_output_pressed)

    def on_clear_output_pressed(self, e):
        self.mf.Packet_log.delete(0, "end")

    def on_clear_input_pressed(self, e):
        self.mf.Input.delete(1.0, "end")

    def on_action_pressed(self, e):
        if not self.try_connect:
            self.try_connect = True
            disable(self.mf.Action)
            disable(self.mf.IP)
            disable(self.mf.Port)
            disable(self.mf.Auto_Send)
            Thread(target=self.client.connect, args=(self.mf.IP.get("1.0", "end - 1 lines lineend"),
                                                     ui_support.port_num.get(), ui_support.buffer_size.get())).start()

    def on_error(self, message, detail, error_type):
        messagebox.showerror(message, detail)
        if error_type is "REFUSED":
            self.try_connect = False
            enable(self.mf.Action)
            enable(self.mf.IP, "xterm")
            enable(self.mf.Port, "xterm")
            enable(self.mf.Auto_Send)
