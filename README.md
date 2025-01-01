# Tasha

**Tasha** is a tool for creating characters for Dungeons & Dragons 5th edition (2024).

### Supported rulebooks

  * [*Player's Handbook 2024*](https://www.amazon.com/Dungeons-Dragons-Players-Handbook-Rulebook/dp/0786969512/ref=sr_1_1?crid=Q5CVDF9LEKCR&dib=eyJ2IjoiMSJ9.KggBZNS4k50B6gIGZykwyAllHlDPYc0OKbcSPRUnOeaf7xarl1Qh75B-svm690jDc5Ubb8NE7-FQlF93zPqJ4nzpY9hKrLipiAh3VdIXeklwDRgL2xhQ4qlb6L5frqXVCqZ5F1owxNa8HJ0u-NuittVd-wUBE2oeEdJ71qed1yNp4NM-Xmo6BZeInTeROhQtepObqQHkIYTsFvWXlIEA_iVEtS8JKbZkLz0AxGnJY9U.zsuk-fEv2n0ZfuKE8fzhKVaVLpChNEwjNZm2S8lZZIk&dib_tag=se&keywords=players%2Bhandbook%2B5e%2B2024&qid=1727028562&sprefix=players%2Caps%2C149&sr=8-1&th=1)

## QUICKSTART

### Dependencies

* [dice](https://github.com/borntyping/python-dice)
* [rich](https://github.com/Textualize/rich)
* [toml](https://github.com/uiri/toml)

### Installation

*Tasha* can be installed by cloning the repo, building a wheel file with poetry, and installing it through pip.

```
git clone https://github.com/mtttech/tasha

cd tasha

poetry build

cd dist

pipx install tasha-0.*.*-py3-none-any.whl
```

### Usage

Run *Tasha* by typing the following command.

```
tasha
```

Characters created by Tasha are saved to your *HOME* directory within the *.config/tasha/characters* folder, which will be created if it doesn't already exist. Characters will be saved in the .TOML format. Below is an example of such a character.

```
alignment = "Chaotic Neutral"
armors = [ "Light", "Medium", "Shield",]
background = "Entertainer"
cantrips = 4
feats = [ "Magic Initiate", "Chef",]
features = [ "Divine Order", "Spellcasting", "Channel Divinity", "Cleric Subclass", "Ability Score Improvement", "Sear Undead",]
gender = "Female"
hit_die = 8
hit_points = 33
initiative = 2
languages = [ "Common", "Draconic", "Elvish",]
level = 5
name = "Bekha"
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
