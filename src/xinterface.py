#!/usr/bin/env python3

import threading
import queue
from Xlib import X, display
from Xlib.ext import record
from Xlib.protocol import rq, event
import CONSTANTS
import service


class Interface():

    def __init__(self, callback=None):
        self.main_loop = threading.Thread(
            target=self._main_loop, name='Main Loop', daemon=True)
        self.queue = queue.Queue()

        self.event_hook = threading.Thread(
            target=self._event_hook, name='Event Hook', daemon=True)
        self.callback = callback
        self.last_time_key_pressed = 0
        self.service = service.Service(self)
        self.static_display = display.Display()
        self.local_display = display.Display()
        self.record_display = display.Display()
        self.context = self.record_display.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (X.FocusIn, X.FocusIn),
                'device_events': (X.KeyPress, X.KeyRelease),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])

        self.MODIFIER_MASK = {'NoModifier': 0,
                              '<Shift>': X.ShiftMask,
                              '<Control>': X.ControlMask,
                              '<Alt>': 0,
                              '<AltGr>': 0,
                              '<Super>': 0,
                              '<NumLock>': 0}
        self.set_modifier_mask()
        self.KEYPAD = set()
        for name in dir(CONSTANTS.XK):
            if name.startswith('XK_KP'):
                self.KEYPAD.add(self.local_display.keysym_to_keycode(
                    getattr(CONSTANTS.XK, name)))

        self.static_root = self.static_display.screen().root
        self.static_window = self.static_display.get_input_focus().focus
        self.root_window = self.local_display.screen().root
        self._name_atom = self.local_display.intern_atom("_NET_WM_NAME", True)
        self._visible_name_atom = self.local_display.intern_atom(
            "_NET_WM_VISIBLE_NAME", True)
        self.update_active_window()

    def start(self):
        if self.service is None:
            self.service = service.Service(self)
        self.service.start()
        self.main_loop.start()
        self.event_hook.start()

    def stop(self):
        self.enqueue(None)
        self.service.stop()
        self.service = None

    def _main_loop(self):

        while True:
            method, args = self.queue.get()

            if method is None:
                break

            try:
                method(*args)
            except Exception as exc:
                print('Error in the interface main loop\n', exc)

            self.queue.task_done()

    def enqueue(self, method, *args):

        self.queue.put_nowait((method, args))

    def _event_hook(self):

        self.record_display.record_enable_context(
            self.context, self.process_event)

    def get_window_class(self, window):
        if type(window) == int:
            return '.'
        wm_class = window.get_wm_class()
        if (wm_class is None or wm_class == ''):
            return self.get_window_class(window.query_tree().parent)
        return '{0}.{1}'.format(wm_class[0], wm_class[1])

    def get_window_title(self, window):
        if type(window) == int:
            return ''
        atom = window.get_property(self._visible_name_atom, 0, 0, 255)
        if atom is None:
            atom = window.get_property(self._name_atom, 0, 0, 255)
        if atom:
            if type(atom.value) is not str:
                return atom.value.decode('UTF-8')
            else:
                return atom.value
        else:
            return self.get_window_title(
                window.query_tree().parent)

    def update_active_window(self):
        self.static_window = self.static_display.get_input_focus().focus
        self.active_window = self.local_display.get_input_focus().focus
        self.active_window_class = self.get_window_class(self.active_window)
        self.active_window_title = self.get_window_title(self.active_window)

    def set_modifier_mask(self):

        MOD_MAP = self.local_display.get_modifier_mapping()
        MOD_INDEX = {X.ShiftMapIndex: X.ShiftMask,
                     X.LockMapIndex: X.LockMask,
                     X.ControlMapIndex: X.ControlMask,
                     X.Mod1MapIndex: X.Mod1Mask,
                     X.Mod2MapIndex: X.Mod2Mask,
                     X.Mod3MapIndex: X.Mod3Mask,
                     X.Mod4MapIndex: X.Mod4Mask,
                     X.Mod5MapIndex: X.Mod5Mask}
        for index, mask in MOD_INDEX.items():
            keylist = [self.local_display.keycode_to_keysym(keycode, 0)
                       for keycode in MOD_MAP[index]]
            if ((CONSTANTS.XK.XK_Alt_L in keylist) or
                    (CONSTANTS.XK.XK_Alt_R in keylist)):
                self.MODIFIER_MASK['<Alt>'] = mask
            elif CONSTANTS.XK.XK_ISO_Level3_Shift in keylist:
                self.MODIFIER_MASK['<AltGr>'] = mask
            elif ((CONSTANTS.XK.XK_Super_L in keylist) or
                  (CONSTANTS.XK.XK_Super_R in keylist)):
                self.MODIFIER_MASK['<Super>'] = mask
            elif CONSTANTS.XK.XK_Num_Lock in keylist:
                self.MODIFIER_MASK['<NumLock>'] = mask

    def translate_state(self, state, keycode, modifiers={}):

        index = 0
        if (((state & self.MODIFIER_MASK['<Shift>']) ^
            (state & X.LockMask)) and
                keycode not in self.KEYPAD):
            index += 1
            if state & self.MODIFIER_MASK['<Shift>']:
                modifiers['<Shift>'] = True
        else:
            modifiers['<Shift>'] = False
        if ((state & self.MODIFIER_MASK['<AltGr>']) and
                keycode not in self.KEYPAD):
            index += 4
            modifiers['<AltGr>'] = True
        else:
            modifiers['<AltGr>'] = False
        if (state & self.MODIFIER_MASK['<NumLock>'] and
                keycode in self.KEYPAD):
            index += 7
        if state & self.MODIFIER_MASK['<Alt>']:
            modifiers['<Alt>'] = True
        else:
            modifiers['<Alt>'] = False
        if state & X.ControlMask:
            modifiers['<Control>'] = True
        else:
            modifiers['<Control>'] = False
        if state & self.MODIFIER_MASK['<Super>']:
            modifiers['<Super>'] = True
        else:
            modifiers['<Super>'] = False

        return index, modifiers

    def process_event(self, event):

        if event.category != record.FromServer:
            return
        if event.client_swapped:
            return
        if not len(event.data) or event.data[0] < 2:
            return

        data = event.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(
                data, self.record_display.display, None, None)

            if event.type is X.FocusIn:
                self.enqueue(self.update_active_window)
                return

            if event.type in [X.KeyPress, X.KeyRelease]:
                self.enqueue(self.handle_key_event,
                             event.type,
                             event.detail,
                             event.state,
                             self.active_window_class,
                             self.active_window_title)

    def emit_event(self):
        self.callback()

    def handle_key_event(self, type, keycode, state, window_class,
                         window_title):
        keypress = (type == X.KeyPress)
        raw_key = self.local_display.keycode_to_keysym(keycode, 0)
        index, modifiers = self.translate_state(state, keycode)
        if raw_key not in CONSTANTS.NO_INDEX:
            keysym = self.local_display.keycode_to_keysym(keycode, index)
        else:
            keysym = raw_key
        self.service.listener(
            keypress, keysym, raw_key, modifiers, window_class, window_title)

    def keysym_to_char(self, keysym):
        if keysym in CONSTANTS.PRINTABLE:
            char = CONSTANTS.PRINTABLE[keysym]
        elif keysym == CONSTANTS.XK.XK_Return:
            char = '\n'
        elif keysym == CONSTANTS.XK.XK_Tab:
            char = '\t'
        else:
            char = None
        return char

    def char_to_keysym(self, char):
        for keysym, string in CONSTANTS.PRINTABLE.items():
            if string == char:
                return keysym
        else:
            if char == '\b':
                return CONSTANTS.XK.XK_BackSpace
            elif char == '\t':
                return CONSTANTS.XK.XK_Tab
            elif char == '\n':
                return CONSTANTS.XK.XK_Return
            else:
                return 0

    def keysym_to_keycode(self, keysym):
        try:
            keycode, index = list(
                self.static_display.keysym_to_keycodes(keysym))[0]
        except IndexError:
            keycode, index = (0, 0)
        state = 0
        if index == 1:
            state |= 1
        elif index == 2:
            state |= 0x2000
        elif index == 3:
            state |= 0x2000 | 1
        elif index == 6:
            state |= 0x2000 * 2
        elif index == 7:
            state |= 0x2000 * 2 | 1
        elif index == 8:
            state |= 0x2000 * 3
        elif index == 9:
            state |= 0x2000 * 3 | 1
        return keycode, state

    def grab_keyboard(self):
        self.enqueue(self._grab_keyboard)

    def _grab_keyboard(self):
        self.static_window.grab_keyboard(
            True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)
        self.static_display.flush()

    def ungrab_keyboard(self):
        self.enqueue(self._ungrab_keyboard)

    def _ungrab_keyboard(self):
        self.static_display.ungrab_keyboard(X.CurrentTime)
        self.static_display.flush()

    def grab_key(self, keycode, state):
        self.enqueue(self._grab_key, keycode, state)

    def _grab_key(self, keycode, state):
        self.root_window.grab_key(
            keycode, state, False, X.GrabModeAsync, X.GrabModeAsync)

    def ungrab_key(self, keycode, state):
        self.enqueue(self._ungrab_key, keycode, state)

    def _ungrab_key(self, keycode, state):
        self.root_window.ungrab_key(keycode, state)

    def send_key_press(self, keycode, state):
        self.enqueue(self._send_key_press, keycode, state)

    def _send_key_press(self, keycode, state):
        key_press = event.KeyPress(detail=keycode,
                                   time=X.CurrentTime,
                                   root=self.static_root,
                                   window=self.static_window,
                                   child=X.NONE,
                                   root_x=0,
                                   root_y=0,
                                   event_x=0,
                                   event_y=0,
                                   state=state,
                                   same_screen=1)
        self.static_window.send_event(key_press)

    def send_key_release(self, keycode, state):
        self.enqueue(self._send_key_release, keycode, state)

    def _send_key_release(self, keycode, state):
        key_release = event.KeyRelease(detail=keycode,
                                       time=X.CurrentTime,
                                       root=self.static_root,
                                       window=self.static_window,
                                       child=X.NONE,
                                       root_x=0,
                                       root_y=0,
                                       event_x=0,
                                       event_y=0,
                                       state=state,
                                       same_screen=1)
        self.static_window.send_event(key_release)

def get_window_class(window):
    if type(window) == int:
        return '.'
    wm_class = window.get_wm_class()
    if (wm_class is None or wm_class == ''):
        return get_window_class(window.query_tree().parent)
    return '{0}.{1}'.format(wm_class[0], wm_class[1])



if __name__ == '__main__':
    root = display.Display().screen().root
    print(type(root))
    print(type(root.query_tree().parent))
    wm_class = root.get_wm_class()
    print(type(wm_class))
    # Get all windows?
    windows = display.Display().screen().root.query_tree().children
    # Print WM_CLASS properties of all windows.
    for w in windows: print(get_window_class(w))