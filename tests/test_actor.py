from tasha.actor import PlayerCharacter


def player_character():
    return PlayerCharacter(
        alignment="Chaotic Good",
        gender="Male",
        name="Woldor the Barbarian",
        species="Human",
    )


def test_player_character():
    assert player_character()


def test_player_alignment():
    assert player_character().alignment


def test_player_gender():
    assert player_character().gender


def test_player_name():
    assert player_character().name


def test_player_species():
    assert player_character().species
