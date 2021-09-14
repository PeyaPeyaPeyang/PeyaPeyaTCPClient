from gui import ui_support, ui
from utils import *


class UILogic:
    def __init__(self, main_form):
        main_form: ui.MainForm
        self.mf = main_form
        self.init()

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
        disable(self.mf.Action)
        disable(self.mf.IP)
        disable(self.mf.Port)
        disable(self.mf.Auto_Send)

