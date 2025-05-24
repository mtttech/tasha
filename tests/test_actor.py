from tasha.actor import PlayerCharacter


oPC = PlayerCharacter(
    alignment="Chaotic Good",
    gender="Male",
    name="Woldor the Barbarian",
    species="Human",
)


def test_player_character():
    assert oPC


def test_player_alignment():
    assert oPC.alignment


def test_player_gender():
    assert oPC.gender


def test_player_name():
    assert oPC.name


def test_player_species():
    assert oPC.species
