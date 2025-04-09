import _thread
import time
from machine import Pin
import network
import socket


def core0_main():
    pass


def core1_server():
    pass


if __name__ == '__main__':
    _thread.start_new_thread(core1_server, ())
    core0_main()
