from utils.db_manager import db_manager, requires_db

from ui import prettier_cli as cli


# > create <sheet>
def create_sheet(sheet: str) -> str:

    if len(sheet.split()) != 1:
        cli.cout(f"Error: Specify 1 sheet.", cli.MsgType.BAD_INPUT)
        return None

    if not db_manager.create(sheet):
        cli.cout("Error: sheet already exists", cli.MsgType.BAD_INPUT)
        return None

    cli.cout(f"\nCreated sheet '{sheet}'.")

    return f"{sheet} "


# > select <sheet>
def select_sheet(new_sheet: str) -> str:

    if len(new_sheet.split()) != 1:
        cli.cout(f"Error: Specify 1 sheet.", cli.MsgType.BAD_INPUT)
        return None

    if not db_manager.change_database(new_sheet):
        cli.cout("Error: sheet does not exist.", cli.MsgType.BAD_INPUT)
        show_available()
        return None

    cli.cout(f"\nSwitched to {new_sheet} sheet.", cli.MsgType.SUCCESS)

    return f"{new_sheet} "


# > sheets
def show_available():
    sheets = db_manager.list_databases()

    if not sheets:
        cli.cout(f"\nNo sheets found in {db_manager.vault_path}")
        return

    cli.cout("\nAvailable sheets:")
    for sheet in sheets:
        cli.cout(f"    - {sheet.stem}")
