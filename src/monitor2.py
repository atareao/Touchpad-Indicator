#!/usr/bin/env python3


import xinterface
import time
import sys


def main():
    interface = xinterface.Interface()
    interface.start()
    time.sleep(10)
    print('parado')
    interface.stop()
    time.sleep(5)

    # If Gtk throws an error or just a warning, main_quit() might not
    # actually close the app
    sys.exit(0)


if __name__ == '__main__':
    main()
