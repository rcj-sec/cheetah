from ui import prettier_cli as cli


def main_help(cmd: str = None):

    if cmd:
        cli.cout(f"\nInvalid command: {cmd}", cli.MsgType.BAD_INPUT)

    cli.cout("\nICheetah help")

    cli.cout("\nSheet management")
    cli.cout("    - sheets                     list available sheets")
    cli.cout("    - <sheet>                    select a sheet")
    cli.cout("    - create <sheet>             create an empty sheet")

    cli.cout("\nEntries")
    cli.cout("    - ls                         list all commands from sheet")
    cli.cout("    - tool <tool>                list commands from tool")
    cli.cout("    - tag <tag1> <tag2> ...      list commands from tags")
    cli.cout("    - add                        add a command to sheet")
    cli.cout("    - delete <id1> <id2> ...     delete commands by id")
    cli.cout("    - cp <id>                    copy command to clipboard")

    cli.cout("\nTags")
    cli.cout("    - tags                       list available tags")

    cli.cout("\nTools")
    cli.cout("    - tools                      list available tools")


def edit_tags_help():
    cli.cout("\nEdit tags help")

    cli.cout("    - remove <tag> <tag> ...     remove tags from from command")
    cli.cout("    - add <tag> <tag> ...        add tags to from command")
    cli.cout("    - ls                         show current tags of command")
    cli.cout("\nEnter empty line to confirm changes.")
