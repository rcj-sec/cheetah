from utils.db_manager import db_manager, requires_db


from ui import prettier_cli as cli


@requires_db
def insert_command(sheet):
    tool = cli.cin(f"\n{sheet} / add / tool", words=1, allow_empty=False)
    args = cli.cin(f"\n{sheet} / add / args")
    desc = cli.cin(f"\n{sheet} / add / desc")
    tags = cli.cin(f"\n{sheet} / add / tag", type=cli.CinType.LIST) + [tool]

    db_manager.add_command(tool, desc, tags, args)
