# Tasha

## QUICKSTART

### Dependencies

* [dice](https://github.com/borntyping/python-dice)
* [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu)
* [toml](https://github.com/uiri/toml)

### Installation & Usage

#### Installation

```
# Clone the repository.
git clone https://github.com/mtttech/Tasha.git

# Change into the cloned repo directory. 
cd Tasha

# Create your virtual environment and install the dependencies (if necessary).
```

#### Usage

Run the following command ```python tasha.py``` to begin.

When started, the program will run a series of prompts that construct your character.

When generating attributes, you select a threshold value between 60-90. This will prompt the application to keep rolling the six ability scores until they total or exceed this value.

Completed characters are saved as a TOML file, using the name of the character as its file name. They can be found in your ***$HOME/.config/tasha/characters*** directory.
