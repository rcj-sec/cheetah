from utils.db_manager import db_manager, requires_db
from utils.settings_manager import settings
from ui import prettier_cli as cli
from actions import select, help


@requires_db
def edit_command(args: str):
    def edit_base_attributes():
        for attr in attrs:
            if attr not in default_attrs:
                cli.cout(
                    f"\nNo such attribute '{attr}' ('tool', 'args', 'desc', 'tags')"
                )
                continue
            prompt = f"\n{settings.active_sheet} / edit / {id} / {attr}"
            line = cli.cin(prompt, allow_edit=command[attr], fore=cli.Colors.ORANGE)
            if line != command[attr]:
                updates[attr] = line

    if not args:
        cli.cout("Error: specify the id of the command.")
        cli.cout("Optional: specify attributes to edit (tool, args, desc, tags)")
        return

    default_attrs = ["tool", "args", "desc", "tags"]

    id, *attrs = args.split()

    if not id.isdigit():
        cli.cout("Error: id not a positive integer")
        return

    command = db_manager.get_command_by_id(id)

    if not command:
        cli.cout(f"Error: no command with id {id}", cli.MsgType.BAD_INPUT)
        return

    attrs = list(dict.fromkeys(default_attrs if not attrs else attrs))

    # if 'tags' was specified as an attribute to edit, pop it in tags var
    # because it is a special case
    # else tags = None and special case won't trigger
    tags = None if "tags" not in attrs else attrs.pop(attrs.index("tags"))

    updates = {}

    edit_base_attributes()

    if tags:
        _edit_tags(id, settings.active_sheet)

    if updates:
        db_manager.update_command(updates, id)

    select.list_commands(id=str(id))


def _edit_tags(id: int, sheet: str):
    while True:
        prompt = f"\n{sheet} / edit / {id} / tags (h for help)"
        action, *tags = cli.cin(prompt, fore=cli.Colors.ORANGE, split=1)
        if action == "h":
            help.edit_tags_help()

        elif action == "rm":
            db_manager.delete_tag_from_command(id, tags)

        elif action == "add":
            db_manager.add_tags_to_commands(id, tags)

        elif action == "ls":
            select.list_tags_from_cmd(id)

        elif not action:
            break

        else:
            cli.cout("Error: specify add/rm followed by tag(s)")
