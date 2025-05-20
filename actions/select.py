from utils.db_manager import db_manager, requires_db
from itertools import cycle

from ui import prettier_cli as cli


# main entry point for querying commands
@requires_db
def list_commands(tags: str = None, tool: str = None, id: str = None):
    if tags:
        _by_tag(tags)
        return

    if tool:
        _by_tool(tool)
        return

    if id:
        _by_id(id)
        return

    _all()


@requires_db
def list_tools():
    tools = db_manager.get_tools()

    if not tools:
        cli.cout("No tools found. Maybe sheet is empty?")
        return

    cli.cout("\nAvailable tools:")
    for tool in tools:
        cli.cout(f"    - {tool['tool']}")


@requires_db
def list_tags():
    tags = db_manager.get_tags()

    if not tags:
        cli.cout("No tags found. Maybe sheet is empty?")
        return

    cli.cout("\nAvailable tags:")
    for tag in tags:
        cli.cout(f"    #{tag['tag']}")


@requires_db
def list_tags_from_cmd(id: int):
    tags = db_manager.get_tags_from_command(id)

    cli.cout("\nTags:")
    for tag in tags:
        cli.cout(f"    #{tag['tag']}")


# > tag <tag1 tag2 tag3 ...>
def _by_tag(tags: str):
    tags = list(dict.fromkeys(tags.split()))

    entries, no_tags = db_manager.get_commands_by_tags(tags)

    colors = cycle(
        [
            color.value
            for color in cli.Colors
            if color.value and not color.value == cli.Colors.BLACK
        ]
    )

    for tag, commands in entries.items():
        cli.cout(f"\n#{tag}")
        _print_cmds(commands, fore=next(colors))

    if no_tags:
        cli.cout(f"\nTags not found: {" ".join(f"#{tag}" for tag in no_tags)}")


# > tool <tool>
def _by_tool(tool: str):
    if len(tool.split()) != 1:
        cli.cout("Error: specify only one tool.", cli.MsgType.BAD_INPUT)
        return

    commands = db_manager.get_commands_by_tool(tool)

    _print_cmds(commands)


# > ls <id>
def _by_id(id: str):
    if not id.isdigit():
        cli.cout("Error: id must be a positive integer.")
        return

    command = db_manager.get_command_by_id(id)

    _print_cmds([command])


# > ls
def _all():
    entries = db_manager.get_commands()
    _print_cmds(entries)


def _print_cmds(commands: list, fore: str = cli.Colors.DEFAULT):
    print()
    for cmd in commands:
        id = cmd["id"]
        tool = cmd["tool"]
        args = cmd["args"]
        desc = cmd["desc"]
        cli.cout(f"{id} # {tool} {args} -> {desc}", fore=fore)
