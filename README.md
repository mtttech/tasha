# Tasha

**Tasha** is a tool for creating player characters for the 5th edition *Dungeons & Dragons (2024)* tabletop game.

### Supported rulebooks

Below is a list of rulebooks incorporated into the program (more may be added as they become available).

  * [Player's Handbook 2024](https://www.amazon.com/Dungeons-Dragons-Players-Handbook-Rulebook/dp/0786969512/ref=sr_1_1?crid=Q5CVDF9LEKCR&dib=eyJ2IjoiMSJ9.KggBZNS4k50B6gIGZykwyAllHlDPYc0OKbcSPRUnOeaf7xarl1Qh75B-svm690jDc5Ubb8NE7-FQlF93zPqJ4nzpY9hKrLipiAh3VdIXeklwDRgL2xhQ4qlb6L5frqXVCqZ5F1owxNa8HJ0u-NuittVd-wUBE2oeEdJ71qed1yNp4NM-Xmo6BZeInTeROhQtepObqQHkIYTsFvWXlIEA_iVEtS8JKbZkLz0AxGnJY9U.zsuk-fEv2n0ZfuKE8fzhKVaVLpChNEwjNZm2S8lZZIk&dib_tag=se&keywords=players%2Bhandbook%2B5e%2B2024&qid=1727028562&sprefix=players%2Caps%2C149&sr=8-1&th=1)


## Dependencies

The following dependencies are required.

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
tasha
```

The program will send a series of prompts that will be used to generate your character.

Saved characters are saved as a TOML file within your *HOME* directory *~/.config/tasha/characters*.

Below is an example of such a character.

```
alignment = "Chaotic Good"
armors = [ "Light", "Medium", "Shield",]
background = "Entertainer"
cantrips = 4
feats = [ "Magic Initiate", "Chef",]
gender = "Female"
hit_points = 33
languages = [ "Common", "Draconic", "Elvish",]
level = 5
name = "Khrista"
proficiency_bonus = 3
savingthrows = [ "Charisma", "Wisdom",]
size = "Medium"
skills = [ "Acrobatics", "Performance", "History", "Religion",]
species = "Elf"
speed = 30
spell_slots = [ 4, 3, 2,]
tools = [ "Musical Instrument - Dulcimer",]
traits = [ "Darkvision", "Elven Lineage", "Fey Ancestry", "Keen Senses", "Trance",]
weapons = [ "Simple",]

[bonus]
Strength = 2
Dexterity = 0
Constitution = 0
Intelligence = 0
Wisdom = 0
Charisma = 1

[features]
Cleric = [ "Divine Order", "Spellcasting", "Channel Divinity", "Cleric Subclass", "Ability Score Improvement", "Sear Undead",]

[prepared_spells]
Cleric = [ "Bestow Curse", "Continual Flame", "Create Food and Water", "Ceremony", "Blindness/Deafness", "Spirit Guardians", "Healing Word", "Cure Wounds", "Silence",]

[attributes.Strength]
score = 19
modifier = 4

[attributes.Dexterity]
score = 14
modifier = 2

[attributes.Constitution]
score = 13
modifier = 1

[attributes.Intelligence]
score = 13
modifier = 1

[attributes.Wisdom]
score = 18
modifier = 4

[attributes.Charisma]
score = 11
modifier = 0

[classes.Cleric]
level = 5
hit_die = 8
subclass = "Life Domain"
```
