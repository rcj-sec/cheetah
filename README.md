# 🐆 Cheetah CLI 
# 💻 Terminal-Based Cheatsheet Manager

Cheetah CLI is a fast, minimal, and powerful command-line tool that helps you manage personal cheatsheets for commands, tools, and workflows. Designed for developers and sysadmins who live in the terminal.

## ✨ Features

- Create, tag, and organize command snippets
- Search by tags or tools
- Edit, copy to clipboard, and delete commands
- Supports multiple sheets (profiles)
- Friendly CLI with colored output


## 📦 Installation

### 1. Download

```bash
git clone https://github.com/rcj-sec/cheetah.git
```

- Clone the repository and move to your preferred location
- Main entry point is `cheetah/cheetah.py`, so feel free to create an alias run it.

### 2. Install dependencies

Cheetah uses the following dependencies:
- `rich` for coloured output
- `pyperclip` to copy contents to clipboard
- `prompt-toolkit` for the editable prompts 

```bash
pip install -r requirements.txt
```

### 3. Configuration

- All that Cheetah requires is the file `.config/cheetah/settings.chh`
- This file contains some configuration variables. So for there is only one (`VAULT`) but hopefully in the future there will be more
- File `.config/cheetah/settings.chh` follow a key-value pair structure:

```bash
VARIABLE_NAME VALUE
```

- So far the only variables are:
    - `VAULT`: path to directories where sheets will be stored (as sqlite3 .db files)

> **Do not worry:** when Cheetah does not find `settings.chh`, you will be prompted to enter the values

### 4. Run Cheetah

- After installing the requirements, simply run Cheetay as you would with any other Python file

```bash
python cheetah
```

## Usage Guide

- To create a sheet:

```bash
    ICheetah
 🐾 create android_eng
```

- Once you create a sheet, it will become the active sheet.
- To switch to another sheet, type its name:

```bash
    android_eng
 🐾 neovim

    neovim
 🐾 |
```

- Once you have a sheet selected, you can start adding commands

```bash
    android_eng
 🐾 add
```

- This will trigger a series of prompts:

```bash
    android_eng / add / tool  # tool used in the command
 🐾 apktool
 
    android_eng / add / args  # arguments used by the tool
 🐾 d target_file.apk

    android_eng / add / desc  # brief description of command
 🐾 reverse apk file into smali

    android_eng / add / tag 1  # first tag associated to command
 🐾 smali
    
    android_eng / add / tag 2  # second tag associated to command
 🐾 reverse

    ...
```

- Enter an empty string to finish.


- You can also list commands by one or many tags

```bash
    android_eng
 🐾 tag smali reverse provider
```

- This will list all commands associated to the tags `smali`, `reverse`, and `provider`
    - The output will be grouped by tags as well

- If you don't know what tags you have in your sheet, you can list them with:

```bash
    android_eng
 🐾 tags
```

- Similarly, you can see the tools you have used in this sheet

```bash
    android_eng
 🐾 tools
```

- Or list commands for a specific tool:

```bash
    android_eng
 🐾 tool apktool
```

- If you want to remove a command from the sheet, use `rm` with the command id

```bash
    android_eng
 🐾 rm 8
```

- If you want to edit a command, use `edit` with the command id and the attributes to modify
- Attributes can be `tool`, `args`, `desc`, and `desc`
    - If you want to edit them all, do not specify any attribute: `edit 1`

```bash
    android_eng
 🐾 edit 12 desc

    android_eng / edit / 12 / desc
 🐾 reverse apk file into smali with 

    android_eng
 🐾 |
```

> **Note:** field prompts will be prefilled with its current values

- You can also copy a command to your clipboard with `cp`
    - It will only copy the tool and the arguments used

```bash
    android_eng
 🐾 cp 12
```
