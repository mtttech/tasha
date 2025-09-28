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
		Ability: []string{"Dexterity", "Wisdom"},
		Armors:  []string{},
		Tools:   []string{},
		Weapons: []string{},
	},
	"Paladin": {
		Ability: []string{"Strength", "Charisma"}, // either or
		Armors:  []string{"Light", "Medium", "Shield"},
		Tools:   []string{},
		Weapons: []string{"Martial"},
	},
	"Ranger": {
		Ability: []string{"Dexterity", "Wisdom"},
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
	for _, ability := range abilities {
		if ability_scores[ability].Score >= 17 {
			return true
		}
	}
	return false
}

/*
Returns a slice of valid multiclass options.
*/
func GetValidMulticlassOptions(ability_scores map[string]attributes.AbilityScore) []string {
	valid_classes := []string{}
	classes := slices.Collect(maps.Keys(characterMulticlasses))
	slices.Sort(classes)
	for _, class := range classes {
		if can_multiclass_to_class(class, ability_scores) {
			valid_classes = append(valid_classes, class)
		}
	}
	return valid_classes
}
