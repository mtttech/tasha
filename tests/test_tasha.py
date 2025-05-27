from tasha.tasha import assign_ability_scores, calculate_modifier


def test_assign_ability_scores():
    assert type(assign_ability_scores()) == dict


def test_calculate_modifier():
    assert calculate_modifier(18) == 4
