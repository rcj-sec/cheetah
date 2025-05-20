from actions import help, insert, other, select, sheets, delete, update

from ui import prettier_cli as cli

from utils.settings_manager import settings

import sys

COMMANDS_MAP = {
    "help": lambda args: help.main_help(),
    "h": lambda args: help.main_help(),
    "sheets": lambda args: sheets.show_available(),
    "create": lambda args: settings.switch_sheets(sheets.create_sheet(args)),
    "ls": lambda args: select.list_commands(),
    "tag": lambda args: select.list_commands(tags=args),
    "tool": lambda args: select.list_commands(tool=args),
    "tools": lambda args: select.list_tools(),
    "tags": lambda args: select.list_tags(),
    "add": lambda args: insert.insert_command(args),
    "rm": lambda args: delete.delete_command(args),
    "edit": lambda args: update.edit_command(args),
    "cp": lambda args: other.copy_to_clipboard(args),
    "clear": lambda args: other.clear_screen(),
    "exit": lambda args: close(),
}


def close():
    cli.cout("\n🐆💨💨 Bye!")
    sys.exit()


def cheetah():
    global COMMANDS_MAP

    welcome = "\nWelcome to Cheetah CLI 🐾! (type 'help' or 'h' for available actions, 'exit' to quit)"
    cli.cout(welcome)

    while True:
        try:
            action, args = cli.cin(
                f"\n{settings.active_sheet}", fore=cli.Colors.ORANGE, split=1
            )

            if not action:
                continue

            func = COMMANDS_MAP.get(action)

            if func:
                func(args)
            else:
                settings.switch_sheets(sheets.select_sheet(action))

        except (KeyboardInterrupt, EOFError):
            close()


if __name__ == "__main__":
    cheetah()
