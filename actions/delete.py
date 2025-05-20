from utils.db_manager import db_manager, requires_db
from ui import prettier_cli as cli


@requires_db
def delete_command(ids_str: str = None):
    ids = _parse_range(ids_str)

    del_count = db_manager.delete_command(ids)

    if len(ids) == del_count:
        cli.cout(f"Deleted {del_count} rows.", cli.MsgType.SUCCESS)
    else:
        cli.cout(f"Deleted {del_count} rows out of {len(ids)}.", cli.MsgType.WARNING)


def _parse_range(string: str):
    def add_nums(nums):
        for num in nums:
            if num not in seen:
                seen.add(num)
                result.append(num)

    result = []
    seen = set()

    for part in string.split():
        if "-" in part:
            start_str, end_str = part.split("-", maxsplit=1)
            if not start_str.isdigit() or not end_str.isdigit():
                return _bad_range_msg(part)
            start, end = int(start_str), int(end_str)
            if start > end:
                return _bad_range_msg(part)
            add_nums(range(start, end + 1))
        else:
            if not part.isdigit():
                return _bad_range_msg(part)
            add_nums([int(part)])

    return result


def _bad_range_msg(part: int):
    msg = f"\nError: invalid id '{part}'.Specify <int> or <int>-<int>."
    cli.cout(msg, cli.MsgType.BAD_INPUT)
    return False
