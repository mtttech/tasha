/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

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
		Ability: []string{"Strength", "Charisma"},
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
