import sqlite3

from contextlib import contextmanager
from collections import defaultdict
from functools import wraps
from pathlib import Path

from utils.settings_manager import settings

from ui import prettier_cli as cli


class DatabaseManager:

    _instance = None

    def __new__(cls, schema="schema1"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls.vault_path = Path(settings.vault_path)
            cls.schema_path = Path(".") / f"{schema}.sql"
            cls.database_path = None
            cls.connection = None
        return cls._instance

    # > <sheet>
    def change_database(self, database: str) -> bool:
        """Change path of current active DB.
        Looks for the existence of <database>.db file in vault dir.

        Args:
            database (str): name of the DB (excluding .db)

        Returns:
            bool: True if <database>.db in vault dir exists.
        """
        if not self._database_exists(database):
            return False

        self.database_path = self.vault_path / f"{database}.db"

        return True

    # > create <sheet>
    def create(self, database: str) -> bool:
        """Create DB. Does not overwrite if it already exists

        Args:
            database (str): DB name (excluding .db)

        Returns:
            bool: True if DB was created successfully
        """
        if self._database_exists(database):
            return False

        self.database_path = self.vault_path / f"{database}.db"
        self._execute_schema()

        return True

    # > add
    def add_command(self, tool: str, args: str, desc: str, tags: list):
        """Add entry to command to DB with its tags.

        Args:
            tool (str): tool used
            args (str): arguments for the tool
            desc (str): brief description of command
            tags (list): list of tags associated to the command
        """
        self._connect()
        with self.session() as conn:
            with conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    insert into commands (tool, args, desc) 
                    values (?, ?, ?)
                    """,
                    (tool, args, desc),
                )
                command_id = cursor.lastrowid

        self.add_tags_to_commands(command_id, tags)

    # add_command and _edit_tags
    def add_tags_to_commands(self, command_id: int, tags: str):
        """Associate a list of tags to a command

        Args:
            command_id: id of the command
            tags: list of tags (not tag ids)
        """
        with self.session() as conn:
            with conn:
                cursor = conn.cursor()

                cursor.executemany(  # insert tags in case there are new tags
                    f"""
                    insert or ignore into tags (tag)
                    values (?)
                    """,
                    [(tag,) for tag in tags],
                )

                placeholders = ", ".join("?" * len(tags))
                cursor.execute(  # select ids of tags to later insert in joint table
                    f"""
                    select id
                    from tags
                    where tag in ({placeholders})
                    """,
                    tags,
                )

                cursor.executemany(  # insert command_id and tag ids in joint table
                    """
                    insert or ignore into command_tags
                    values (?, ?)
                    """,
                    [(command_id, tag_id["id"]) for tag_id in cursor],
                )

    # > tool <tool>
    def get_commands_by_tool(self, tool: str) -> list:
        """Get commands where tool is used.

        Args:
            tool: name of the tool (in cmd)

        Returns:
            list: commands with tool.
        """
        with self.session() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                select c.id, c.tool, c.args, c.desc
                from commands c
                where c.tool = ?
                """,
                (tool,),
            )

            commands = cursor.fetchall()

        return [dict(command) for command in commands]

    # > tag <tag1> <tag2> <tag3> ...
    def get_commands_by_tags(self, tags: list) -> tuple[dict, list]:
        """Get commands associated to tags

        Args:
            tags: list of tags to filter commands by

        Returns:
            dict: commands by tag. Key is the tag and value is a list of commands.
            list: list of tags with no commands
        """
        tag_entries = defaultdict(list)
        empty_tags = set(tags)
        placeholders = ", ".join("?" for _ in tags)
        with self.session() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                select c.id, c.tool, c.args, c.desc, t.tag
                from commands c
                join command_tags ct on c.id = ct.command_id
                join tags t on ct.tag_id = t.id
                where t.tag in ({placeholders})
                order by c.tool
                """,
                tags,
            )

            for command in cursor:
                tag = command["tag"]
                empty_tags.discard(tag)
                tag_entries[tag].append(dict(command))

        return dict(tag_entries), list(empty_tags)

    # > cp <id> and edit <id>
    def get_command_by_id(self, id: int) -> dict:
        """Get command by id

        Args:
            id: id of the command

        Returns:
            dict: command as a dict
        """
        with self.session() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                select *
                from commands c
                where c.id = ?
                """,
                (id,),
            )
            command = cursor.fetchone()

        return command

    # > ls
    def get_commands(self) -> list:
        """Get all commands in sheet

        Returns:
            list: all commands in sheet
        """
        with self.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select c.id, c.tool, c.args, c.desc
                from commands c
                order by c.tool
                """
            )
            entries = cursor.fetchall()

        return entries

    # > tags
    def get_tags(self) -> list:
        """Get all tags in the sheet

        Returns:
            list: all tags in the sheet
        """
        with self.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select tag 
                from tags 
                order by tag
                """
            )
            entries = cursor.fetchall()

        return entries

    # _edit_tags
    def get_tags_from_command(self, id: int) -> list:
        """Get all tags associated to command with id

        Args:
            id: command id

        Returns:
            list: tags associated to command
        """
        with self.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select t.tag
                from tags t
                join command_tags ct on t.id = ct.tag_id
                where ct.command_id = ?
                order by t.tag
                """,
                (id,),
            )
            entries = cursor.fetchall()

        return entries

    # > tools
    def get_tools(self) -> list:
        """Get all tools in sheet

        Returns:
            list: tools in the sheet
        """
        with self.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                select distinct tool
                from commands
                order by tool
                """
            )
            entries = cursor.fetchall()

        return entries

    # rm <id> <id> ...
    def delete_command(self, ids: list) -> int:
        """Delete commands by ids

        Args:
            ids: list of ids of commands to delete

        Returns:
            int: number of commands deleted
        """
        placeholders = ", ".join("?" * len(ids))
        with self.session() as conn:
            with conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.execute(
                    f"""
                    delete from commands
                    where id in ({placeholders})
                    """,
                    ids,
                )

                rowcount = cursor.rowcount

        return rowcount

    # > edit <id>
    def delete_tag_from_command(self, id: int, tags: str) -> int:
        """Remove tag from command

        Args:
            id: command id
            tags: list of tags to remove from command

        Returns:
            int: number of tags removed from command
        """
        with self.session() as conn:
            with conn:
                cursor = conn.executemany(
                    f"""
                    delete from command_tags
                    where command_id = ?
                    and tag_id in (select id from tags where tag in (?))
                    """,
                    [(id, tag) for tag in tags],
                )

                rowcount = cursor.rowcount

        return rowcount

    # > edit <id>
    def update_command(self, updates: dict, command_id: int):
        """Update command fields

        Args:
            updates: updated fields
            command_id: id of command to update
        """
        placeholders = ", ".join(f"{key} = ?" for key in updates)
        values = list(updates.values()) + [command_id]
        with self.session() as conn:
            with conn:
                cursor = conn.execute(
                    f"""
                    update commands
                    set {placeholders}
                    where id = ?
                    """,
                    values,
                )

                rowcount = cursor.rowcount

        return rowcount

    # > sheets
    def list_databases(self) -> list:
        """List available DB files in vault

        Returns:
            list: list of db files, including .db extension.
        """
        return list(self.vault_path.glob("*.db"))

    # checks if a DB is selected and can therefore operate
    def is_on(self) -> str:
        """Check if a database is selected

        Returns:
            str: DB name if a DB is selected. None if otherwise.
        """
        return None if not self.database_path else self.database_path.stem

    # connects to db
    def _connect(self):
        """Closes existing connection (if any) and connect to new database.

        Args:
            database (str): database name (not path)
        """
        if self.connection:
            self.connection.close()

        if not self.database_path:
            cli.cout(f"No database selected", cli.MsgType.FATAL_ERROR)
            raise ValueError

        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row

    # disconnects from
    def _disconnect(self):
        """Disconnect from database if any."""
        if self.connection:
            self.connection.close()
            self.connection = None

    @contextmanager
    def session(self):
        self._connect()
        try:
            yield self.connection
        finally:
            self._disconnect()

    # creates DB from schema
    def _execute_schema(self):
        """Executa schema in self.schema_path"""
        if not self.schema_path.exists():
            cli.cout(
                f"Error: could not open schema '{self.schema_path}'",
                cli.MsgType.FATAL_ERROR,
            )
            raise FileNotFoundError

        schema_sql = self.schema_path.read_text(encoding="utf-8")

        with self.session() as conn:
            with conn:
                conn.cursor().executescript(schema_sql)

    # > create <sheet>
    def _database_exists(self, database: str):
        tmp = self.vault_path / f"{database}.db"
        return tmp.exists()


def requires_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not db_manager.is_on():
            cli.cout("Please select a sheet", cli.MsgType.BAD_INPUT)
            return
        return func(*args, **kwargs)

    return wrapper


db_manager = DatabaseManager()
