import readline
import os
import glob

from rich.console import Console
from prompt_toolkit import prompt
from enum import Enum

rich_console = Console()


class Colors(str, Enum):
    DEFAULT = ""
    BLACK = "black"
    RED = "red1"
    GREEN = "green1"
    YELLOW = "yellow1"
    BLUE = "blue1"
    MAGENTA = "magenta1"
    CYAN = "cyan1"
    WHITE = "bright_white"
    ORANGE = "orange1"

    def __str__(self):
        return self.value


class MsgType(str, Enum):
    FATAL_ERROR = Colors.RED
    BAD_INPUT = Colors.YELLOW
    WARNING = Colors.ORANGE
    SUCCESS = Colors.GREEN

    def __str__(self):
        return self.value


class CinType(str, Enum):
    LINE = 0
    LIST = 1
    PATH = 2

    def __str__(self):
        return self.value


_completer_cache = {"text": None, "matches": []}


def cout(
    text: str = "",
    msg_type: str = None,
    bold: bool = True,
    fore: str = Colors.DEFAULT,
    back: str = Colors.DEFAULT,
    endl: str = "\n",
):
    fore = msg_type if msg_type else fore
    style = _style(bold, fore, back)
    _print(text, style, endl)


def cin(
    text: str = "",
    bold: bool = True,
    fore: str = Colors.DEFAULT,
    back: str = Colors.DEFAULT,
    symbol: str = "🐾",
    words: int = 0,
    type: int = CinType.LINE,
    allow_empty: bool = True,
    allow_edit: str = None,
    split: int = 0,
):
    if type == CinType.LIST:
        return _cin_list(text, bold, fore, back, symbol)

    cout(text, None, bold, fore, back)

    if type == CinType.PATH:
        return _cin_path(symbol)

    if allow_edit:
        line = prompt(f" {symbol} ", default=allow_edit)
    else:
        line = input(f" {symbol} ")  # use input to allow up and down arrow keys cycling

    if not allow_empty and not line:  # do not allow for empty lines
        cout("Error: cannot provide an empty value.", MsgType.BAD_INPUT)
        return cin(text, bold, fore, back, symbol, words, allow_empty=allow_empty)

    if words and len(line.split()) != words:  # check if matches specifed words
        cout(f"Error: introduce exactly {words} word(s).", MsgType.BAD_INPUT)
        return cin(text, bold, fore, back, symbol, words, allow_empty=allow_empty)

    # check if input must be split
    if not split:
        return line

    parts = line.split(maxsplit=split)
    while len(parts) < split + 1:
        parts.append(None)

    return tuple(parts)


def _cin_path(symbol):
    readline.set_completer(_path_completer)
    readline.parse_and_bind("tab: menu-complete")
    readline.parse_and_bind('"\\e[Z": menu-complete-backward')

    try:
        file_path = input(f" {symbol} ")
        return file_path
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled")


def _path_completer(text, state):
    global _completer_cache

    # only reload options if input has changed
    if state == 0 or text != _completer_cache["text"]:
        line = readline.get_line_buffer()
        if not line:
            return None

        expanded_line = os.path.expanduser((os.path.expandvars(line)))
        dirname = os.path.dirname(expanded_line)
        prefix = os.path.basename(expanded_line)

        if not dirname:
            dirname = "."

        try:
            if line.endswith("."):  # if aiming for hidden file only load hidden files
                entries = os.listdir(dirname)
            else:  # if not aiming for hidden file do not load hidden files
                entries = [entry for entry in os.listdir(dirname) if not entry.startswith(".")]
        except FileNotFoundError:
            _completer_cache["matches"] = []
            return None

        matches = [entry for entry in entries if entry.startswith(prefix)]

        # if there is only one match and it's a dir, append / to enter dir
        if len(matches) == 1 and os.path.isdir(f"{dirname}/{matches[0]}"):
            if not matches[0].endswith("/"):
                matches[0] += "/"

        _completer_cache["text"] = text
        _completer_cache["matches"] = matches

    try:
        return _completer_cache["matches"][state]
    except IndexError:
        return None


def _cin_list(text, bold, fore, back, symbol):

    lst = []

    counter = 1

    item = cin(f"{text} {counter}", bold, fore, back, symbol)

    while item:
        lst.append(item)
        counter += 1
        item = cin(f"{text} {counter}", bold, fore, back, symbol)

    return lst


def _style(bold: bool = True, fore: str = Colors.DEFAULT, back: str = Colors.DEFAULT):
    parts = []
    if bold:
        parts.append("bold")
    if fore:
        parts.append(fore)
    if back:
        parts.append(f"on {back}")

    return " ".join(parts)


def _adjust_padding(text: str):
    padding = " " * 4
    i = text.rfind("\n")
    if i != -1:
        text = text[: i + 1] + padding + text[i + 1 :]
    else:
        text = padding + text
    return text


def _print(text: str, style: str, endl: str):
    text = _adjust_padding(text)
    rich_console.print(f"[{style}]{text}[/{style}]", end=endl)
