from codecs import encode
from datetime import datetime
from threading import Thread
from time import sleep

from client_base import Client, AbstractClient, State
from gui import ui_support, ui
from utils import *

try:
    import Tkinter as tkinter
    from Tkinter import messagebox
except ImportError:
    import tkinter as tkinter
    from tkinter import messagebox


class UILogic(AbstractClient):
    def __init__(self, main_form):
        main_form: ui.MainForm

        self.mf = main_form
        self.client = Client(self)
        self.alive = True
        self.try_connect = False
        self.logger = None

        # line by line send
        self.sent = 0
        self.data = None

        self.encodings = get_encodings()
        self.encodings.insert(4, "Raw bytes")

        self.init()
        Thread(target=self.update_display).start()

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

        disable(form.Action)

        form.Packet_log = init_packet_log()
        self.logger = Logger(form.Packet_log)

        form.Packet_log.configure(cursor="")

        form.IP.insert(1.0, "localhost")

        ui_support.send_encoding.set("Send Encoding")
        ui_support.receive_encoding.set("Receive Encoding")

        form.Send_Encoding.configure(state="readonly")
        form.Send_Encoding.configure(values=self.encodings)
        form.Receive_Encoding.configure(state="readonly")
        form.Receive_Encoding.configure(values=self.encodings)

        ui_support.port_num.set(80)
        ui_support.buffer_size.set(1024)

        form.Action.bind("<ButtonRelease-1>", self.on_action_pressed)
        form.Clear_In.bind("<ButtonRelease-1>", self.on_clear_input_pressed)
        form.Clear_Logs.bind("<ButtonRelease-1>", self.on_clear_output_pressed)
        form.Send.bind("<ButtonRelease-1>", self.on_send_pressed)
        form.IP.bind("<KeyPress>", self.validate)
        form.Send_Encoding.bind("<<ComboboxSelected>>", self.validate)
        form.Receive_Encoding.bind("<<ComboboxSelected>>", self.validate)

    def validate(self, *args):
        if "\n" in self.mf.IP.get("1.0", "end").replace("\n", ""):
            disable(self.mf.Action)
        elif ui_support.send_encoding.get() == "Send Encoding" or \
                ui_support.receive_encoding.get() == "Receive Encoding":
            disable(self.mf.Action)
        else:
            enable(self.mf.Action)

    def on_send_pressed(self, *args):
        if self.mf.Send.cget("state") == "disabled":
            return

        enc = ui_support.send_encoding.get()

        if not ui_support.send_one_line_checked.get():
            self.client.send_data(encode_data(self.mf.Input.get("1.0", "end")[:-1], enc))
            return

        if self.data is None:
            self.data = self.mf.Input.get("1.0", "end")[:-1].split("\n")

        self.client.send_data(encode_data(self.data[self.sent], enc))
        self.sent += 1

        ln = len(self.data)
        if ln == self.sent:
            disable(self.mf.Send)
        elif ln <= self.sent:
            return

    def on_clear_output_pressed(self, e):
        self.logger.clear()

    def on_clear_input_pressed(self, e):
        self.mf.Input.delete(1.0, "end")

    def on_action_pressed(self, e):
        if self.mf.Action.cget("state") == "disabled":
            return
        if not self.try_connect:
            if ui_support.auto_clear_checked:
                self.logger.clear()
            self.try_connect = True
            self.logger.push("Connection", "Connecting...")
            disable(self.mf.Action)
            disable(self.mf.IP)
            disable(self.mf.Port)
            disable(self.mf.Auto_Send)
            self.client = Client(self)
            Thread(target=self.client.connect, args=(self.mf.IP.get("1.0", "end").replace("\n", ""),
                                                     ui_support.port_num.get(), ui_support.buffer_size.get())).start()
        else:
            self.try_connect = False
            self.logger.push("Connection", "Disconnecting...")
            self.client.disconnect()

    def on_error(self, message, detail, error_type):
        self.logger.push("Error", message)
        messagebox.showerror(message, detail)
        if error_type is "TRYCONN_ERR":
            self.try_connect = False
            enable(self.mf.Action)
            enable(self.mf.IP, "xterm")
            enable(self.mf.Port, "xterm")
            enable(self.mf.Auto_Send)
            disable(self.mf.Send)

    def on_connected(self):
        enable(self.mf.Send)
        self.mf.Action.configure(text="Disconnect")
        enable(self.mf.Action)
        self.logger.push("Connection", "Connection established to " + self.mf.IP.get("1.0", "end").replace("\n", "") +
                         ":" + str(ui_support.port_num.get()))
        if ui_support.auto_send_checked.get():
            if ui_support.send_one_line_checked.get():
                for i in range(0, self.mf.Input.get("1.0", "end").replace("\n", "", 1).count("\n")):
                    self.on_send_pressed()
            else:
                self.on_send_pressed()

    def on_disconnected(self):
        enable(self.mf.Action)
        enable(self.mf.IP, "xterm")
        enable(self.mf.Port, "xterm")
        enable(self.mf.Auto_Send)
        disable(self.mf.Send)
        self.mf.Action.configure(text="Connect")
        self.logger.push("Connection", "Disconnected from server.")


def encode_data(data, encoding):
    if encoding == "Raw bytes":
        return bytes.fromhex(data.replace("-", "").replace("0x", "").lower().replace(" ", ""))
    return encode(data, encoding.lower().replace("-", "_"))


def init_packet_log():
    a = PopupListBox(ui_support.top_level)
    a.place(relx=0.021, rely=0.553, relheight=0.35, relwidth=0.965)
    a.configure(background="white")
    a.configure(cursor="xterm")
    a.configure(disabledforeground="#a3a3a3")
    a.configure(font="TkFixedFont")
    a.configure(foreground="black")
    a.configure(highlightbackground="#d9d9d9")
    a.configure(highlightcolor="#d9d9d9")
    a.configure(selectbackground="blue")
    a.configure(selectforeground="white")
    return a


class LogElement:
    def __init__(self, date, name, message):
        self.date = date
        self.name = name
        self.message = message

    def format(self):
        return "{}  {:10}  {}".format(self.date.strftime("%Y/%m/%d %H:%M:%S"), self.name, self.message)

    def __str__(self):
        return self.format()


class PopupListBox(ui.ScrolledListBox):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.popup = tkinter.Menu(self, tearoff=0)

        self.bind("<ButtonRelease-3>", self.click)

    def click(self, e):
        self.selection_clear(0, "end")
        self.selection_set(self.nearest(e.y))
        self.activate(self.nearest(e.y))
        try:
            self.popup.tk_popup(e.x_root, e.y_root, 0)
        finally:
            self.popup.grab_release()

    def add_command(self, name, func):
        self.popup.add_command(label=name, command=func)


class Logger:

    def __init__(self, control):
        self.control = control
        control.add_command("Copy the body", self.copy)
        self.log_type_len = 0
        self.logs = []

    def copy(self):
        log = self.logs[self.control.curselection()[0]]
        clipboard = tkinter.Tk()
        clipboard.withdraw()
        clipboard.clipboard_clear()
        clipboard.clipboard_append(log.message)
        clipboard.update()
        clipboard.destroy()

    def push(self, log_type, message):
        self.log_type_len = max([len(log_type), self.log_type_len])
        ls = LogElement(datetime.now(), log_type, message)

        self.logs.append(ls)
        self.control.insert("end", ls)

    def clear(self):
        self.control.delete(0, "end")
        del self.logs
        self.logs = []
