from enum import Enum
import socket
from threading import Thread
from time import sleep


class AbstractClient:
    def state_changed(self, state):
        pass

    def on_connected(self):
        pass

    def on_disconnected(self):
        pass

    def send_data(self, octet):
        pass

    def on_receive_data(self, octet):
        pass


class State(Enum):
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    RECEIVING_DATA = "Data receiving"


class Client:
    def __init__(self, handler):
        self.state = [State.DISCONNECTED]
        self.buffer_size = 1024
        self.handler = handler

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.read_thread = Thread(target=self.read)
        Thread(target=self.watchdog).start()

        self.send_sec = 0
        self.receive_sec = 0

    def watchdog(self):
        while True:
            if State.DISCONNECTED in self.state:
                sleep(1)
                continue
            if self.receive_sec == 0 and State.RECEIVING_DATA in self.state:
                self.push_state(State.RECEIVING_DATA, True)
            self.send_sec = 0
            self.receive_sec = 0
            sleep(1)

    def read(self):
        while True:
            chunk = self.client.recv(self.buffer_size)
            if not chunk or self.state == State.DISCONNECTED:
                break
            self.receive_sec += len(chunk)
            self.handler.on_receive_data(chunk)

    def push_state(self, state, m=False):
        if m:
            if state not in self.state:
                return
            self.state.remove(state)
        else:
            if state in self.state:
                return
            self.state.append(state)

        self.handler.state_changed(self.state)

    def connect(self, host, port, buffer_size=1024):
        self.push_state(State.CONNECTING)
        self.buffer_size = buffer_size
        self.client.connect((host, port))
        self.push_state(State.CONNECTING, True)
        self.push_state(State.CONNECTED)
        self.read_thread.start()
        self.handler.on_connected()

    def disconnect(self):
        if self.state != State.DISCONNECTED:
            self.client.close()
            self.push_state(State.CONNECTED, True)
            self.push_state(State.DISCONNECTED)
            self.handler.on_disconnected()

    def send_data(self, octet):
        self.send_sec += len(octet)
        self.client.send(octet)
