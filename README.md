# Tasha

**Tasha** is a tool for creating player characters for the 5th edition *Dungeons & Dragons (2024)* tabletop game.

### Supported rulebooks

Below is a list of rulebooks incorporated into the program (more may be added as they become available).

  * [Player's Handbook 2024](https://www.amazon.com/Dungeons-Dragons-Players-Handbook-Rulebook/dp/0786969512/ref=sr_1_1?crid=Q5CVDF9LEKCR&dib=eyJ2IjoiMSJ9.KggBZNS4k50B6gIGZykwyAllHlDPYc0OKbcSPRUnOeaf7xarl1Qh75B-svm690jDc5Ubb8NE7-FQlF93zPqJ4nzpY9hKrLipiAh3VdIXeklwDRgL2xhQ4qlb6L5frqXVCqZ5F1owxNa8HJ0u-NuittVd-wUBE2oeEdJ71qed1yNp4NM-Xmo6BZeInTeROhQtepObqQHkIYTsFvWXlIEA_iVEtS8JKbZkLz0AxGnJY9U.zsuk-fEv2n0ZfuKE8fzhKVaVLpChNEwjNZm2S8lZZIk&dib_tag=se&keywords=players%2Bhandbook%2B5e%2B2024&qid=1727028562&sprefix=players%2Caps%2C149&sr=8-1&th=1)


## Dependencies

The following dependencies are required.

* [click](https://github.com/pallets/click)
* [dice](https://github.com/borntyping/python-dice)
* [rich](https://github.com/Textualize/rich)
* [toml](https://github.com/uiri/toml)


## Installation

**Tasha** can be installed by cloning the repo, building a wheel with [poetry](https://github.com/python-poetry/poetry), and installing it with [pipx](https://github.com/pypa/pipx).

```
git clone https://github.com/mtttech/tasha.git

cd tasha

poetry build

pipx install dist/tasha-0.*.*-py3-none-any.whl
```


## Usage

Run **Tasha** by typing the following command.

```
tasha --help
Usage: tasha [OPTIONS]

Options:
  --new TEXT  Generates a new player character.
  --version   Show the version and exit.
  --help      Show this message and exit.
```

Create a character.

```
tasha --new Rowena
```

The program will send a series of prompts that will be used to generate your character.

You will be prompted to then save the finished character. Such characters will be saved as a .toml file within the same directory.

Below is an example of such a character.

```
alignment = "Chaotic Good"
armors = [ "Light", "Shield", "Heavy", "Medium",]
background = "Soldier"
feats = [ "Magic Initiate",]
gender = "Female"
hit_points = 22
languages = [ "Common", "Elvish", "Dwarvish",]
level = 3
name = "Rowena"
proficiency_bonus = 2
savingthrows = [ "Strength", "Constitution",]
size = "Medium"
skills = [ "Athletics", "Acrobatics", "Intimidation",]
species = "Elf"
speed = 30
spell_slots = [ 0,]
tools = [ "Artisan's Tools - Cartographer's Supplies",]
traits = [ "Fey Ancestry", "Darkvision", "Elven Lineage", "Trance", "Keen Senses",]
weapons = [ "Martial", "Simple",]

[bonus]
Strength = 2
Dexterity = 1
Constitution = 0
Intelligence = 0
Wisdom = 0
Charisma = 0

[cantrips]
Fighter = 0

[features]
Fighter = [ "Fighting Style", "Second Wind", "Weapon Mastery", "Action Surge (one use)", "Tactical Mind", "Fighter Subclass",]

[prepared_spells]
Fighter = [ "Sleep", "Shield", "Magic Missile",]

[attributes.Strength]
score = 17
modifier = 3

[attributes.Dexterity]
score = 14
modifier = 2

[attributes.Constitution]
score = 11
modifier = 0

[attributes.Intelligence]
score = 13
modifier = 1

[attributes.Wisdom]
score = 9
modifier = -1

[attributes.Charisma]
score = 13
modifier = 1

[classes.Fighter]
level = 3
hit_die = 10
subclass = "Eldritch Knight"
```
