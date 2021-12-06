"""
This type stub file was generated by pyright.
"""
from __future__ import print_function as _print_function
import typing

import re as _re
import itertools as _itertools
import collections as _collections
import time as _time
import platform as _platform
from threading import Lock as _Lock, Thread as _Thread
from ._keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent
from ._generic import GenericListener as _GenericListener
from ._canonical_names import all_modifiers, normalize_name, sided_modifiers

try:
    # Python2
    # threading.Event is a function in Python2 wrappin _Event (?!).
    from threading import _Event as _UninterruptibleEvent  # type: ignore
except NameError:
    # Python3
    import queue as _queue
    from threading import Event as _UninterruptibleEvent


"""
keyboard
========

Take full control of your keyboard with this small Python library. Hook global events, register hotkeys, simulate key presses and much more.

## Features

- **Global event hook** on all keyboards (captures keys regardless of focus).
- **Listen** and **send** keyboard events.
- Works with **Windows** and **Linux** (requires sudo), with experimental **OS X** support (thanks @glitchassassin!).
- **Pure Python**, no C modules to be compiled.
- **Zero dependencies**. Trivial to install and deploy, just copy the files.
- **Python 2 and 3**.
- Complex hotkey support (e.g. `ctrl+shift+m, ctrl+space`) with controllable timeout.
- Includes **high level API** (e.g. [record](#keyboard.record) and [play](#keyboard.play), [add_abbreviation](#keyboard.add_abbreviation)).
- Maps keys as they actually are in your layout, with **full internationalization support** (e.g. `Ctrl+ç`).
- Events automatically captured in separate thread, doesn't block main program.
- Tested and documented.
- Doesn't break accented dead keys (I'm looking at you, pyHook).
- Mouse support available via project [mouse](https://github.com/boppreh/mouse) (`pip install mouse`).

## Usage

Install the [PyPI package](https://pypi.python.org/pypi/keyboard/):

    pip install keyboard

or clone the repository (no installation required, source files are sufficient):

    git clone https://github.com/boppreh/keyboard

or [download and extract the zip](https://github.com/boppreh/keyboard/archive/master.zip) into your project folder.

Then check the [API docs below](https://github.com/boppreh/keyboard#api) to see what features are available.


## Example


```py
import keyboard

keyboard.press_and_release('shift+s, space')

keyboard.write('The quick brown fox jumps over the lazy dog.')

keyboard.add_hotkey('ctrl+shift+a', print, args=('triggered', 'hotkey'))

# Press PAGE UP then PAGE DOWN to type "foobar".
keyboard.add_hotkey('page up, page down', lambda: keyboard.write('foobar'))

# Blocks until you press esc.
keyboard.wait('esc')

# Record events until 'esc' is pressed.
recorded = keyboard.record(until='esc')
# Then replay back at three times the speed.
keyboard.play(recorded, speed_factor=3)

# Type @@ then press space to replace with abbreviation.
keyboard.add_abbreviation('@@', 'my.long.email@example.com')

# Block forever, like `while True`.
keyboard.wait()
```

## Known limitations:

- Events generated under Windows don't report device id (`event.device == None`). [#21](https://github.com/boppreh/keyboard/issues/21)
- Media keys on Linux may appear nameless (scan-code only) or not at all. [#20](https://github.com/boppreh/keyboard/issues/20)
- Key suppression/blocking only available on Windows. [#22](https://github.com/boppreh/keyboard/issues/22)
- To avoid depending on X, the Linux parts reads raw device files (`/dev/input/input*`)
but this requires root.
- Other applications, such as some games, may register hooks that swallow all
key events. In this case `keyboard` will be unable to report events.
- This program makes no attempt to hide itself, so don't use it for keyloggers or online gaming bots. Be responsible.
"""

Callback = typing.Callable[[KeyboardEvent], None]

version: str
_is_str = typing.Callable[[typing.Any], bool]
_is_number = typing.Callable[[typing.Any], bool]
_is_list: typing.Callable[[typing.Any], bool]


class _State:
    ...


class _Event(_UninterruptibleEvent):
    def wait(self) -> None:
        ...


if _platform.system() == 'Windows':
    ...
else:
    ...
_modifier_scan_codes: set


def is_modifier(key) -> bool:
    """
    Returns True if `key` is a scan code or name of a modifier key.
    """
    ...


_pressed_events_lock: _Lock
_pressed_events: dict
_physically_pressed_keys: dict
_logically_pressed_keys: dict


class _KeyboardListener(_GenericListener):
    transition_table = {
        ('free', KEY_UP, 'modifier'): (False, True, 'free'),
        ('free', KEY_DOWN, 'modifier'): (False, False, 'pending'),
        ('pending', KEY_UP, 'modifier'): (True, True, 'free'),
        ('pending', KEY_DOWN, 'modifier'): (False, True, 'allowed'),
        ('suppressed', KEY_UP, 'modifier'): (False, False, 'free'),
        ('suppressed', KEY_DOWN, 'modifier'): (False, False, 'suppressed'),
        ('allowed', KEY_UP, 'modifier'): (False, True, 'free'),
        ('allowed', KEY_DOWN, 'modifier'): (False, True, 'allowed'),

        ('free', KEY_UP, 'hotkey'): (False, None, 'free'),
        ('free', KEY_DOWN, 'hotkey'): (False, None, 'free'),
        ('pending', KEY_UP, 'hotkey'): (False, None, 'suppressed'),
        ('pending', KEY_DOWN, 'hotkey'): (False, None, 'suppressed'),
        ('suppressed', KEY_UP, 'hotkey'): (False, None, 'suppressed'),
        ('suppressed', KEY_DOWN, 'hotkey'): (False, None, 'suppressed'),
        ('allowed', KEY_UP, 'hotkey'): (False, None, 'allowed'),
        ('allowed', KEY_DOWN, 'hotkey'): (False, None, 'allowed'),

        ('free', KEY_UP, 'other'): (False, True, 'free'),
        ('free', KEY_DOWN, 'other'): (False, True, 'free'),
        ('pending', KEY_UP, 'other'): (True, True, 'allowed'),
        ('pending', KEY_DOWN, 'other'): (True, True, 'allowed'),
        # Necessary when hotkeys are removed after beign triggered, such as
        # TestKeyboard.test_add_hotkey_multistep_suppress_modifier.
        ('suppressed', KEY_UP, 'other'): (False, False, 'allowed'),
        ('suppressed', KEY_DOWN, 'other'): (True, True, 'allowed'),
        ('allowed', KEY_UP, 'other'): (False, True, 'allowed'),
        ('allowed', KEY_DOWN, 'other'): (False, True, 'allowed'),
    }

    def init(self) -> None:
        ...

    def pre_process_event(self, event):
        ...

    def direct_callback(self, event):
        """
        This function is called for every OS keyboard event and decides if the
        event should be blocked or not, and passes a copy of the event to
        other, non-blocking, listeners.

        There are two ways to block events: remapped keys, which translate
        events by suppressing and re-emitting; and blocked hotkeys, which
        suppress specific hotkeys.
        """
        ...

    def listen(self) -> None:
        ...


_listener: _KeyboardListener


def key_to_scan_codes(key: typing.Union[int, str, typing.List[typing.Union[int, str]]], error_if_missing: bool = ...) -> typing.List[int]:
    """
    Returns a list of scan codes associated with this key (name or scan code).
    """
    ...


def parse_hotkey(hotkey) -> tuple[tuple[tuple[Unknown] | Unknown | tuple[()] | tuple[Unknown, ...]]] | tuple[tuple[tuple[Unknown] | Unknown | tuple[()] | tuple[Unknown, ...], ...]] | tuple[Unknown, ...]:
    """
    Parses a user-provided hotkey into nested tuples representing the
    parsed structure, with the bottom values being lists of scan codes.
    Also accepts raw scan codes, which are then wrapped in the required
    number of nestings.

    Example:

        parse_hotkey("alt+shift+a, alt+b, c")
        #    Keys:    ^~^ ^~~~^ ^  ^~^ ^  ^
        #    Steps:   ^~~~~~~~~~^  ^~~~^  ^

        # ((alt_codes, shift_codes, a_codes), (alt_codes, b_codes), (c_codes,))
    """
    ...


def send(hotkey: typing.Union[str, int], do_press: bool = ..., do_release: bool = ...) -> None:
    """
    Sends OS events that perform the given *hotkey* hotkey.

    - `hotkey` can be either a scan code (e.g. 57 for space), single key
    (e.g. 'space') or multi-key, multi-step hotkey (e.g. 'alt+F4, enter').
    - `do_press` if true then press events are sent. Defaults to True.
    - `do_release` if true then release events are sent. Defaults to True.

        send(57)
        send('ctrl+alt+del')
        send('alt+F4, enter')
        send('shift+s')

    Note: keys are released in the opposite order they were pressed.
    """
    ...


press_and_release = send


def press(hotkey) -> None:
    """ Presses and holds down a hotkey (see `send`). """
    ...


def release(hotkey) -> None:
    """ Releases a hotkey (see `send`). """
    ...


def is_pressed(hotkey) -> bool:
    """
    Returns True if the key is pressed.

        is_pressed(57) #-> True
        is_pressed('space') #-> True
        is_pressed('ctrl+space') #-> True
    """
    ...


def call_later(fn, args=..., delay=...) -> None:
    """
    Calls the provided function in a new thread after waiting some time.
    Useful for giving the system some time to process an event, without blocking
    the current execution flow.
    """
    ...


_hooks: dict[typing.Callable, Unknown]


def hook(callback: Callback, suppress=..., on_remove=...) -> typing.Callable[[], None]:
    """
    Installs a global listener on all available keyboards, invoking `callback`
    each time a key is pressed or released.

    The event passed to the callback is of type `keyboard.KeyboardEvent`,
    with the following attributes:

    - `name`: an Unicode representation of the character (e.g. "&") or
    description (e.g.  "space"). The name is always lower-case.
    - `scan_code`: number representing the physical key, e.g. 55.
    - `time`: timestamp of the time the event occurred, with as much precision
    as given by the OS.

    Returns the given callback for easier development.
    """
    ...


def on_press(callback: Callback, suppress=...) -> typing.Callable[[], None]:
    """
    Invokes `callback` for every KEY_DOWN event. For details see `hook`.
    """
    ...


def on_release(callback: Callback, suppress=...) -> typing.Callable[[], None]:
    """
    Invokes `callback` for every KEY_UP event. For details see `hook`.
    """
    ...


def hook_key(key: typing.Union[int, str, typing.List[typing.Union[int, str]]], callback: Callback, suppress: bool = ...) -> typing.Callable[[], None]:
    """
    Hooks key up and key down events for a single key. Returns the event handler
    created. To remove a hooked key use `unhook_key(key)` or
    `unhook_key(handler)`.

    Note: this function shares state with hotkeys, so `clear_all_hotkeys`
    affects it as well.
    """
    ...


def on_press_key(key, callback: Callback, suppress=...) -> typing.Callable[[], None]:
    """
    Invokes `callback` for KEY_DOWN event related to the given key. For details see `hook`.
    """
    ...


def on_release_key(key, callback: Callback, suppress=...) -> typing.Callable[[], None]:
    """
    Invokes `callback` for KEY_UP event related to the given key. For details see `hook`.
    """
    ...


def unhook(remove: typing.Callable[[], None]) -> None:
    """
    Removes a previously added hook, either by callback or by the return value
    of `hook`.
    """
    ...


unhook_key = unhook


def unhook_all() -> None:
    """
    Removes all keyboard hooks in use, including hotkeys, abbreviations, word
    listeners, `record`ers and `wait`s.
    """
    ...


def block_key(key) -> typing.Callable[[], None]:
    """
    Suppresses all key events of the given key, regardless of modifiers.
    """
    ...


unblock_key = unhook_key


def remap_key(src, dst) -> typing.Callable[[], None]:
    """
    Whenever the key `src` is pressed or released, regardless of modifiers,
    press or release the hotkey `dst` instead.
    """
    ...


unremap_key = unhook_key


def parse_hotkey_combinations(hotkey) -> tuple[tuple[tuple[Unknown, ...], ...], ...]:
    """
    Parses a user-provided hotkey. Differently from `parse_hotkey`,
    instead of each step being a list of the different scan codes for each key,
    each step is a list of all possible combinations of those scan codes.
    """
    ...


_hotkeys: dict


def add_hotkey(hotkey, callback: Callback, args=..., suppress=..., timeout=..., trigger_on_release=...) -> typing.Callable[[], None]:
    """
    Invokes a callback every time a hotkey is pressed. The hotkey must
    be in the format `ctrl+shift+a, s`. This would trigger when the user holds
    ctrl, shift and "a" at once, releases, and then presses "s". To represent
    literal commas, pluses, and spaces, use their names ('comma', 'plus',
    'space').

    - `args` is an optional list of arguments to passed to the callback during
    each invocation.
    - `suppress` defines if successful triggers should block the keys from being
    sent to other programs.
    - `timeout` is the amount of seconds allowed to pass between key presses.
    - `trigger_on_release` if true, the callback is invoked on key release instead
    of key press.

    The event handler function is returned. To remove a hotkey call
    `remove_hotkey(hotkey)` or `remove_hotkey(handler)`.
    before the hotkey state is reset.

    Note: hotkeys are activated when the last key is *pressed*, not released.
    Note: the callback is executed in a separate thread, asynchronously. For an
    example of how to use a callback synchronously, see `wait`.

    Examples:

        # Different but equivalent ways to listen for a spacebar key press.
        add_hotkey(' ', print, args=['space was pressed'])
        add_hotkey('space', print, args=['space was pressed'])
        add_hotkey('Space', print, args=['space was pressed'])
        # Here 57 represents the keyboard code for spacebar; so you will be
        # pressing 'spacebar', not '57' to activate the print function.
        add_hotkey(57, print, args=['space was pressed'])

        add_hotkey('ctrl+q', quit)
        add_hotkey('ctrl+alt+enter, space', some_callback)
    """
    ...


register_hotkey = add_hotkey


def remove_hotkey(hotkey_or_callback) -> None:
    """
    Removes a previously hooked hotkey. Must be called with the value returned
    by `add_hotkey`.
    """
    ...


unregister_hotkey = clear_hotkey = remove_hotkey


def unhook_all_hotkeys() -> None:
    """
    Removes all keyboard hotkeys in use, including abbreviations, word listeners,
    `record`ers and `wait`s.
    """
    ...


unregister_all_hotkeys = remove_all_hotkeys = clear_all_hotkeys = unhook_all_hotkeys


def remap_hotkey(src, dst, suppress=..., trigger_on_release=...) -> typing.Callable[[], None]:
    """
    Whenever the hotkey `src` is pressed, suppress it and send
    `dst` instead.

    Example:

        remap('alt+w', 'ctrl+up')
    """
    ...


unremap_hotkey = remove_hotkey


def stash_state() -> list[Unknown]:
    """
    Builds a list of all currently pressed scan codes, releases them and returns
    the list. Pairs well with `restore_state` and `restore_modifiers`.
    """
    ...


def restore_state(scan_codes) -> None:
    """
    Given a list of scan_codes ensures these keys, and only these keys, are
    pressed. Pairs well with `stash_state`, alternative to `restore_modifiers`.
    """
    ...


def restore_modifiers(scan_codes) -> None:
    """
    Like `restore_state`, but only restores modifier keys.
    """
    ...


def write(text, delay=..., restore_state_after=..., exact=...):
    """
    Sends artificial keyboard events to the OS, simulating the typing of a given
    text. Characters not available on the keyboard are typed as explicit unicode
    characters using OS-specific functionality, such as alt+codepoint.

    To ensure text integrity, all currently pressed keys are released before
    the text is typed, and modifiers are restored afterwards.

    - `delay` is the number of seconds to wait between keypresses, defaults to
    no delay.
    - `restore_state_after` can be used to restore the state of pressed keys
    after the text is typed, i.e. presses the keys that were released at the
    beginning. Defaults to True.
    - `exact` forces typing all characters as explicit unicode (e.g.
    alt+codepoint or special events). If None, uses platform-specific suggested
    value.
    """
    ...


def wait(hotkey=..., suppress=..., trigger_on_release=...) -> None:
    """
    Blocks the program execution until the given hotkey is pressed or,
    if given no parameters, blocks forever.
    """
    ...


def get_hotkey_name(names=...) -> str:
    """
    Returns a string representation of hotkey from the given key names, or
    the currently pressed keys if not given.  This function:

    - normalizes names;
    - removes "left" and "right" prefixes;
    - replaces the "+" key name with "plus" to avoid ambiguity;
    - puts modifier keys first, in a standardized order;
    - sort remaining keys;
    - finally, joins everything with "+".

    Example:

        get_hotkey_name(['+', 'left ctrl', 'shift'])
        # "ctrl+shift+plus"
    """
    ...


def read_event(suppress: bool = ...) -> KeyboardEvent:
    """
    Blocks until a keyboard event happens, then returns that event.
    """
    ...


def read_key(suppress=...):
    """
    Blocks until a keyboard event happens, then returns that event's name or,
    if missing, its scan code.
    """
    ...


def read_hotkey(suppress=...) -> str:
    """
    Similar to `read_key()`, but blocks until the user presses and releases a
    hotkey (or single key), then returns a string representing the hotkey
    pressed.

    Example:

        read_hotkey()
        # "ctrl+shift+p"
    """
    ...


def get_typed_strings(events, allow_backspace=...):
    """
    Given a sequence of events, tries to deduce what strings were typed.
    Strings are separated when a non-textual key is pressed (such as tab or
    enter). Characters are converted to uppercase according to shift and
    capslock status. If `allow_backspace` is True, backspaces remove the last
    character typed.

    This function is a generator, so you can pass an infinite stream of events
    and convert them to strings in real time.

    Note this functions is merely an heuristic. Windows for example keeps per-
    process keyboard state such as keyboard layout, and this information is not
    available for our hooks.

        get_type_strings(record()) #-> ['This is what', 'I recorded', '']
    """
    ...


_recording: typing.Optional[tuple[Unknown | _queue.Queue[Unknown], typing.Callable[[], None]]]


def start_recording(recorded_events_queue=...) -> tuple[Unknown | _queue.Queue[Unknown], typing.Callable[[], None]]:
    """
    Starts recording all keyboard events into a global variable, or the given
    queue if any. Returns the queue of events and the hooked function.

    Use `stop_recording()` or `unhook(hooked_function)` to stop.
    """
    ...


def stop_recording() -> list[Unknown | typing.Any]:
    """
    Stops the global recording of events and returns a list of the events
    captured.
    """
    ...


def record(until=..., suppress=..., trigger_on_release=...) -> list[Unknown | typing.Any]:
    """
    Records all keyboard events from all keyboards until the user presses the
    given hotkey. Then returns the list of events recorded, of type
    `keyboard.KeyboardEvent`. Pairs well with
    `play(events)`.

    Note: this is a blocking function.
    Note: for more details on the keyboard hook and events see `hook`.
    """
    ...


def play(events, speed_factor=...):
    """
    Plays a sequence of recorded events, maintaining the relative time
    intervals. If speed_factor is <= 0 then the actions are replayed as fast
    as the OS allows. Pairs well with `record()`.

    Note: the current keyboard state is cleared at the beginning and restored at
    the end of the function.
    """
    ...


replay = play
_word_listeners: dict


def add_word_listener(word, callback: Callback, triggers=..., match_suffix=..., timeout=...) -> typing.Callable[[], None]:
    """
    Invokes a callback every time a sequence of characters is typed (e.g. 'pet')
    and followed by a trigger key (e.g. space). Modifiers (e.g. alt, ctrl,
    shift) are ignored.

    - `word` the typed text to be matched. E.g. 'pet'.
    - `callback` is an argument-less function to be invoked each time the word
    is typed.
    - `triggers` is the list of keys that will cause a match to be checked. If
    the user presses some key that is not a character (len>1) and not in
    triggers, the characters so far will be discarded. By default the trigger
    is only `space`.
    - `match_suffix` defines if endings of words should also be checked instead
    of only whole words. E.g. if true, typing 'carpet'+space will trigger the
    listener for 'pet'. Defaults to false, only whole words are checked.
    - `timeout` is the maximum number of seconds between typed characters before
    the current word is discarded. Defaults to 2 seconds.

    Returns the event handler created. To remove a word listener use
    `remove_word_listener(word)` or `remove_word_listener(handler)`.

    Note: all actions are performed on key down. Key up events are ignored.
    Note: word matches are **case sensitive**.
    """
    ...


def remove_word_listener(word_or_handler) -> None:
    """
    Removes a previously registered word listener. Accepts either the word used
    during registration (exact string) or the event handler returned by the
    `add_word_listener` or `add_abbreviation` functions.
    """
    ...


def add_abbreviation(source_text, replacement_text, match_suffix=..., timeout=...) -> typing.Callable[[], None]:
    """
    Registers a hotkey that replaces one typed text with another. For example

        add_abbreviation('tm', u'™')

    Replaces every "tm" followed by a space with a ™ symbol (and no space). The
    replacement is done by sending backspace events.

    - `match_suffix` defines if endings of words should also be checked instead
    of only whole words. E.g. if true, typing 'carpet'+space will trigger the
    listener for 'pet'. Defaults to false, only whole words are checked.
    - `timeout` is the maximum number of seconds between typed characters before
    the current word is discarded. Defaults to 2 seconds.

    For more details see `add_word_listener`.
    """
    ...


register_word_listener = add_word_listener
register_abbreviation = add_abbreviation
remove_abbreviation = remove_word_listener