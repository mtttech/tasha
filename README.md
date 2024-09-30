# Tasha

**Tasha** is a tool for creating 5e Dungeons & Dragons characters.

### Supported rulebooks

  * [*Player's Handbook 2024*](https://www.amazon.com/Dungeons-Dragons-Players-Handbook-Rulebook/dp/0786969512/ref=sr_1_1?crid=Q5CVDF9LEKCR&dib=eyJ2IjoiMSJ9.KggBZNS4k50B6gIGZykwyAllHlDPYc0OKbcSPRUnOeaf7xarl1Qh75B-svm690jDc5Ubb8NE7-FQlF93zPqJ4nzpY9hKrLipiAh3VdIXeklwDRgL2xhQ4qlb6L5frqXVCqZ5F1owxNa8HJ0u-NuittVd-wUBE2oeEdJ71qed1yNp4NM-Xmo6BZeInTeROhQtepObqQHkIYTsFvWXlIEA_iVEtS8JKbZkLz0AxGnJY9U.zsuk-fEv2n0ZfuKE8fzhKVaVLpChNEwjNZm2S8lZZIk&dib_tag=se&keywords=players%2Bhandbook%2B5e%2B2024&qid=1727028562&sprefix=players%2Caps%2C149&sr=8-1&th=1)

## QUICKSTART

### Dependencies

* [dice](https://github.com/borntyping/python-dice)
* [toml](https://github.com/uiri/toml)

### Installation & Usage

```
# Clone the repository.
git clone https://github.com/mtttech/Tasha.git

# Change into the cloned repo. 
cd Tasha

# Create your virtual environment and install the requirements (if necessary).

# Run the program
python tasha.py
```

Characters created by Tasha are saved to your *HOME* directory within the *.config/tasha/characters* folder, which will be created if it doesn't already exist. Characters will be saved in the .TOML format. Below is an example of such a character.

```
alignment = "Chaotic Neutral"
armors = [ "Light",]
background = "Noble"
cantrips = "2"
feats = [ "Musician",]
features = [ "Bardic Inspiration", "Spellcasting", "Expertise", "Jack of All Trades", "Bard Subclass",]
gender = "Female"
gold = 0
hit_die = 8
hit_points = 21
initiative = 1
languages = [ "Common", "Elvish", "Draconic",]
level = 3
name = "Sierra"
prepared_spells = 6
proficiency_bonus = 2
savingthrows = [ "Charisma", "Dexterity",]
size = "Medium"
skills = [ "History", "Persuasion", "Arcana", "Animal Handling", "Insight",]
species = "Elf"
speed = 30
spell_slots = [ 4, 2,]
tools = [ "Gaming Set - Playing card Set", "Musical Instrument - Dulcimer", "Musical Instrument - Birdpipes", "Musical Instrument - Flute",]
traits = [ "Darkvision", "Elven Lineage", "Fey Ancestry", "Keen Senses", "Trance",]
weapons = [ "Simple",]

[bonus]
Strength = 1
Dexterity = 0
Constitution = 0
Intelligence = 0
Wisdom = 0
Charisma = 2

[attributes.Strength]
score = 12
modifier = 1

[attributes.Dexterity]
score = 13
modifier = 1

[attributes.Constitution]
score = 13
modifier = 1

[attributes.Intelligence]
score = 11
modifier = 0

[attributes.Wisdom]
score = 9
modifier = -1

[attributes.Charisma]
score = 18
modifier = 4

[classes.Bard]
level = 3
hit_die = 8
subclass = "College of Glamour"
```
