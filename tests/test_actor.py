from tasha.actor import PlayerCharacter


oPC = PlayerCharacter(
    alignment="Chaotic Good",
    attributes={
        "Strength": {"score": 15, "modifier": 2},
        "Dexterity": {"score": 12, "modifier": 1},
        "Constitution": {"score": 13, "modifier": 1},
        "Intelligence": {"score": 10, "modifier": 0},
        "Wisdom": {"score": 10, "modifier": 0},
        "Charisma": {"score": 8, "modifier": -1},
    },
    gender="Male",
    name="Woldor the Barbarian",
    species="Human",
)


def test_player_character():
    assert type(oPC) == PlayerCharacter


def test_player_alignment():
    assert oPC.alignment == "Chaotic Good"


def test_player_gender():
    assert oPC.gender == "Male"


def test_player_name():
    assert oPC.name == "Woldor the Barbarian"


def test_player_species():
    assert oPC.species == "Human"
