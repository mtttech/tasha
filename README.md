# Tasha

**Tasha** is a command-line tool used for creating 5e Dungeons & Dragons characters.

### Supported rulebooks

  * [*Player's Handbook*](https://www.amazon.com/Players-Handbook-Dungeons-Dragons-Wizards/dp/0786965606/ref=sr_1_1?crid=379ZD2GOSSXUS&keywords=player%27s+handbook+53&qid=1686513995&sprefix=players+handbook+53%2Caps%2C117&sr=8-1)
  * [*Dungeon Masters Guide*](https://www.amazon.com/Dungeons-Dragons-Dungeon-Rulebook-Roleplaying/dp/0786965622/ref=sr_1_1?crid=2OL0NVA15CCB4&keywords=dungeon%2Bmasters%2Bguide&qid=1704477505&sprefix=Dungeon%2BM%2Caps%2C110&sr=8-1&th=1)
  * [*Mordenkainen's Tome of Foes*](https://www.amazon.com/MORDENKAINENS-FOES-Accessory-Wizards-Team/dp/0786966246/ref=sr_1_1?crid=1YK3ZSKRTEC2N&keywords=mordenkainen%27s+tome+of+foes&qid=1686514034&sprefix=mordenkain%2Caps%2C135&sr=8-1)
  * [*Volo's Guide to Monsters*](https://www.amazon.com/Volos-Guide-Monsters-Wizards-Team/dp/0786966017/ref=sr_1_1?crid=9Q6IDI7KI2FH&keywords=volos+guide+to+monsters+5e&qid=1686514111&sprefix=volos%2Caps%2C122&sr=8-1)
  * [*Xanathar's Guide to Everything*](https://www.amazon.com/Xanathars-Guide-Everything-Wizards-Team/dp/0786966114/ref=sr_1_1?crid=1HQBURCPQA50W&keywords=xanathars+guide+to+everything+5e&qid=1686514138&sprefix=xa%2Caps%2C147&sr=8-1)
  * [*Tasha's Cauldron of Everything*](https://www.amazon.com/Cauldron-Everything-Expansion-Dungeons-Dragons/dp/0786967021/ref=sr_1_1?crid=3K7SU399VYTP4&keywords=tasha%27s+cauldron+of+everything+5e&qid=1686514198&sprefix=tas%2Caps%2C118&sr=8-1) - Mostly
  * [*Sword Coast Adventurer's Guide*](https://www.amazon.com/Sword-Coast-Adventurers-Guide-Accessory/dp/0786965800/ref=sr_1_1?crid=JNAGKS1F2Y2U&keywords=sword+coast+adventurer%27s+guide+5e&qid=1686514240&sprefix=sword%2Caps%2C133&sr=8-1) - Partially
  * [*The Wild Beyond the Witchlight*](https://www.amazon.com/Wild-Beyond-Witchlight-Adventure-Dungeons/dp/0786967277/ref=sr_1_1?crid=2UYG545HO9XS7&keywords=The%2BWild%2BBeyond%2Bthe%2BWitchlight&qid=1704650190&sprefix=the%2Bwild%2Bbeyond%2Bthe%2Bwitchlight%2Caps%2C102&sr=8-1&th=1) - Partially

## QUICKSTART

### Dependencies

* [dice](https://github.com/borntyping/python-dice)
* [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
* [toml](https://github.com/uiri/toml)

### Installation & Usage

#### Installation

```
# Clone the repository.
git clone https://github.com/mtttech/Tasha.git

# Install the project environment.
cd Tasha
poetry install
```

#### Usage

To begin, run the program by typing the following command ```poetry run tasha```.

From there, you must more or less run the following commands in the order they are listed. Details about each command are further laid out below.

* **roll** ***threshold***: This command performs multiple functions but primarily generates the six ability scores at a certain thresold between 60-90. For example, if you use the command ```roll 60```, Tasha will keep rolling your scores until they total or exceed 60. Once generated, you are given the option to assign your scores, choose your race/subrace (if applicable), gender, and background.
* **add class** ***class***: This command sets your character's class. Run the command again, selecting a different class to multiclass (minimum requirements are enforced). This command only works after the **roll** commmand has been run.
* **set** ***(alignment|name)*** ***value***: These commands are hopefully pretty self-explanatory. They are responsible for setting your alignment and name respectively. This command can "technically" be used at anytime but must be used before the **save** command.
* **save**: This command finalizes your character. It allows you to select a subclass (if applicable), choose skills, choose your ability score improvements (if applicable) and select spells (if applicable). Finally your character is saved to a TOML file in your ***$HOME/.config/tasha/characters*** directory. This command can only be run after the first three.
