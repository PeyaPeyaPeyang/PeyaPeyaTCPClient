from gui import ui_support


class Main:
    def __init__(self):
        pass

    def main(self):
        ui_support.setup_ui()
        ui_support.show_ui()


if __name__ == '__main__':
    main = Main()
    main.main()
