from gui import ui, ui_support, ui_logic

try:
    import Tkinter as tkinter
except ImportError:
    import tkinter


class Main:
    def __init__(self):
        self.ui = None

    def main(self):
        ui_support.setup_ui()
        ui_support.top_level.resizable(0, 0)
        self.ui = ui_logic.UILogic(ui_support.w)
        ui_support.show_ui()


if __name__ == '__main__':
    global main
    main = Main()
    main.main()
    main.ui.dispose()
