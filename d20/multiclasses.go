/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"

	"tasha/attributes"
)

type Multiclass struct {
	Ability []string
	Armors  []string
	Tools   []string
	Weapons []string
}

var characterMulticlasses = map[string]Multiclass{
	"Barbarian": {
		Ability: []string{"Strength"},
		Armors:  []string{"Shield"},
		Tools:   []string{},
		Weapons: []string{"Martial"},
	},
	"Bard": {
		Ability: []string{"Charisma"},
		Armors:  []string{"Light"},
		Tools:   []string{},
		Weapons: []string{},
	},
	"Cleric": {
		Ability: []string{"Wisdom"},
		Armors:  []string{"Light", "Medium", "Shield"},
		Tools:   []string{},
		Weapons: []string{},
	},
	"Druid": {
		Ability: []string{"Wisdom"},
		Armors:  []string{"Light", "Shield"},
		Tools:   []string{},
		Weapons: []string{},
	},
	"Fighter": {
		Ability: []string{"Dexterity", "Strength"}, // either or
		Armors:  []string{"Light", "Medium", "Shield"},
		Tools:   []string{},
		Weapons: []string{"Martial"},
	},
	"Monk": {
		Ability: []string{"Dexterity", "Wisdom"}, // all or nothing
		Armors:  []string{},
		Tools:   []string{},
		Weapons: []string{},
	},
	"Paladin": {
		Ability: []string{"Strength", "Charisma"}, // all or nothing
		Armors:  []string{"Light", "Medium", "Shield"},
		Tools:   []string{},
		Weapons: []string{"Martial"},
	},
	"Ranger": {
		Ability: []string{"Dexterity", "Wisdom"}, // all or nothing
		Armors:  []string{"Light", "Medium", "Shield"},
		Tools:   []string{},
		Weapons: []string{"Martial"},
	},
	"Rogue": {
		Ability: []string{"Dexterity"},
		Armors:  []string{"Light"},
		Tools:   []string{"Thieves' Tools"},
		Weapons: []string{"Simple"}, // Martial weapons with Finesse or Light properties
	},
	"Sorcerer": {
		Ability: []string{"Charisma"},
		Armors:  []string{},
		Tools:   []string{},
		Weapons: []string{},
	},
	"Warlock": {
		Ability: []string{"Charisma"},
		Armors:  []string{"Light"},
		Tools:   []string{},
		Weapons: []string{"Simple"},
	},
	"Wizard": {
		Ability: []string{"Intelligence"},
		Armors:  []string{},
		Tools:   []string{},
		Weapons: []string{},
	},
}

/*
Checks if character can multiclass to the specified class.
*/
func can_multiclass_to_class(class string, ability_scores map[string]attributes.AbilityScore) bool {
	abilities := characterMulticlasses[class].Ability
	switch class {
	case "Fighter":
		if ability_scores["Strength"].Score >= 13 || ability_scores["Dexterity"].Score >= 13 {
			return true
		}
	case "Monk", "Paladin", "Ranger":
		if ability_scores[abilities[0]].Score >= 13 && ability_scores[abilities[1]].Score >= 13 {
			return true
		}
	default:
		if ability_scores[abilities[0]].Score >= 13 {
			return true
		}
	}

	return false
}

/*
Returns a slice of valid multiclass options.
*/
func GetValidMulticlassOptions(ability_scores map[string]attributes.AbilityScore) []string {
	valid_class_options := []string{}
	classes := slices.Collect(maps.Keys(characterMulticlasses))
	slices.Sort(classes)
	for _, new_class := range classes {
		if can_multiclass_to_class(new_class, ability_scores) {
			valid_class_options = append(valid_class_options, new_class)
		}
	}

	return valid_class_options
}
