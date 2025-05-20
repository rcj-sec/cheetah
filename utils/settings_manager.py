import json
import sys

from pathlib import Path
from os.path import expandvars

from ui import prettier_cli as cli


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._load()
        return cls._instance

    def switch_sheets(self, new_sheet):
        self.active_sheet = new_sheet or self.active_sheet

    @classmethod
    def _load(cls):
        default_settings = Path(expandvars("$HOME/.config/cheetah/settings"))

        if not default_settings.exists():
            cli.cout("\nNo settings file found in '.config/cheetah/setting'. You will proceed with the setup.")
            vault_path = cli.cin("\nWhere is your vault located?", allow_empty=False, type=cli.CinType.PATH)
            vault_path = Path(vault_path)
            vault_path.mkdir(parents=True, exist_ok=True)
            default_settings.parent.mkdir(parents=True, exist_ok=True)
            default_settings.write_text(f"VAULT {vault_path}")

        variables = {}
        for line in default_settings.read_text().splitlines():
            if not line.strip():
                continue
            if " " not in line:
                cli.cout("\nMalformed line in .config/cheetah/settings: {line}.", cli.MsgType.FATAL_ERROR)
                sys.exit(1)
            key, value = line.split(" ", 1)
            variables[key] = value.strip()


        cls._instance.vault_path = expandvars(variables["VAULT"])
        cls._instance.active_sheet = "ICheetah"


settings = SettingsManager()
