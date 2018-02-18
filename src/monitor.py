from Xlib import X, XK, protocol
from Xlib.display import Display
import time
import signal, sys

root = None
display = None



def propagate(event):
    display = Display()
    window = display.get_input_focus()._data["focus"]
    window.send_event(event, propagate=False)


def send_event(root, event):
    if type(event) == protocol.event.KeyPress:
        event = protocol.event.KeyPress(
            time=int(time.time()),
            root=root,
            window=event.window,
            same_screen=0,
            child=X.NONE,
            root_x=0,
            root_y=0,
            event_x=0,
            event_y=0,
            state=event.state,
            detail=event.detail
        )
        event.window.send_event(event, propagate=True)


def send_key(emulated_key):
    shift_mask = 0  # or Xlib.X.ShiftMask
    window = display.get_input_focus()._data["focus"]
    keysym = XK.string_to_keysym(emulated_key)
    keycode = display.keysym_to_keycode(keysym)
    event = protocol.event.KeyPress(
        time=int(time.time()),
        root=root,
        window=window,
        same_screen=0,
        child=X.NONE,
        root_x=0,
        root_y=0,
        event_x=0,
        event_y=0,
        state=shift_mask,
        detail=keycode
    )
    window.send_event(event, propagate=True)
    event = protocol.event.KeyRelease(
        time=int(time.time()),
        root=display.screen().root,
        window=window,
        same_screen=0,
        child=X.NONE,
        root_x=0,
        root_y=0,
        event_x=0,
        event_y=0,
        state=shift_mask,
        detail=keycode
    )
    window.send_event(event, propagate=True)


def grab_keyname(n):
    global root
    keysym = XK.string_to_keysym(n)
    keycode = display.keysym_to_keycode(keysym)
    root.grab_key(keycode,
                  X.AnyModifier,
                  False,
                  X.GrabModeSync,
                  X.GrabModeAsync)


def main2():
    # current display
    global display, root
    display = Display()
    root = display.screen().root

    root.change_attributes(event_mask=X.KeyPressMask | X.KeyReleaseMask)

    '''
    for keycode in range(0, 256):
        root.grab_key(keycode,
                      X.AnyModifier,
                      False,
                      X.GrabModeASync,
                      X.GrabModeAsync)
    '''
    grab_keyname("A")
    grab_keyname("j")
    grab_keyname("k")
    grab_keyname("l")

    '''
    signal.signal(signal.SIGALRM, lambda a, b: sys.exit(1))
    signal.alarm(4)
    '''

    while True:
        event = display.next_event()
        print(event.type)
        print(event.detail)
        #send_event(root, event)
        send_key('x')



def main():
    # current display
    display = Display()
    root = display.screen().root

    root.change_attributes(event_mask=X.KeyPressMask | X.KeyReleaseMask)

    root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

    signal.signal(signal.SIGALRM, lambda a, b: sys.exit(1))
    signal.alarm(10)

    while True:
        event = display.next_event()
        print(event)
        print(event.type)
        print(event.detail)
        display.ungrab_keyboard(X.CurrentTime)
        send_event(root, event)
        #event.window.send_event(event, propagate=True)
        root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)


if __name__ == '__main__':
    main2()
