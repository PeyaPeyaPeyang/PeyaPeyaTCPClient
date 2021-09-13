from gui import ui_support, ui


class UILogic:
    def __init__(self, main_form):
        main_form: ui.MainForm
        self.mf = main_form
        self.init()

    def init(self):
        form = self.mf
        form.Action.bind("<Button-1>", self.on_action_pressed)

    def on_action_pressed(self, e):
        self.mf.Action.configure(state="disabled")
        self.mf.Action.configure(text="Connecting...")
