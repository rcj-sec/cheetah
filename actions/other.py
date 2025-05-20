import pyperclip
import os

from utils.db_manager import db_manager, requires_db

from ui import prettier_cli as cli


def clear_screen():
    os.system("clear")


@requires_db
def copy_to_clipboard(id: str):
    if not id.isdigit():
        cli.cout("Error: id not a positive integer", cli.MsgType.BAD_INPUT)
        return

    entry = db_manager.get_command_by_id(id)

    if not entry:
        cli.cout(f"Error: id {id} does not exist.", cli.MsgType.BAD_INPUT)
    else:
        pyperclip.copy(f"{entry['tool']} {entry['arguments']}")
        cli.cout("Copied!", cli.MsgType.SUCCESS)
