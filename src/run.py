from gui import ui_support, ui_logic
from tcp.client_base import Client


class Main:
    def __init__(self):
        self.tcp = None

    def main(self):
        ui_support.setup_ui()
        ui_support.top_level.resizable(0, 0)
        ui_logic.UILogic(ui_support.w)
        ui_support.show_ui()


if __name__ == '__main__':
    global main
    main = Main()
    main.main()
