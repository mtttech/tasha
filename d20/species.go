/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

type Species struct {
	Size   string
	Speed  int
	Traits []string
}

var characterSpecies = map[string]Species{
	"Aasimar": {
		Size:  "Medium",
		Speed: 30,
		Traits: []string{
			"Celestial Resistance",
			"Celestial Revelation",
			"Darkvision",
			"Healing Hands",
			"Heavenly Wings",
			"Inner Radiance",
			"Light Bearer",
			"Necrotic Shroud",
		},
	},
	"Dragonborn": {
		Size:  "Medium",
		Speed: 30,
		Traits: []string{
			"Breath Weapon",
			"Damage Resistance",
			"Darkvision",
			"Draconic Ancestry",
			"Draconic Flight",
		},
	},
	"Dwarf": {
		Size:  "Medium",
		Speed: 30,
		Traits: []string{
			"Darkvision",
			"Dwarven Resilience",
			"Dwarven Toughness",
			"Stonecunning",
		},
	},
	"Elf": {
		Size:  "Medium",
		Speed: 30,
		Traits: []string{
			"Darkvision",
			"Elven Lineage",
			"Fey Ancestry",
			"Keen Senses",
			"Trance",
		},
	},
	"Gnome": {
		Size:   "Small",
		Speed:  30,
		Traits: []string{"Darkvision", "Gnomish Cunning", "Gnomish Lineage"},
	},
	"Goliath": {
		Size:  "Medium",
		Speed: 35,
		Traits: []string{
			"Giant Ancestry",
			"Large Form",
			"Powerful Build",
		},
	},
	"Halfling": {
		Size:  "Small",
		Speed: 30,
		Traits: []string{
			"Brave",
			"Halfling Nimbleness",
			"Luck",
			"Naturally Stealthy",
		},
	},
	"Human": {
		Size:   "Medium",
		Speed:  30,
		Traits: []string{"Resourceful", "Skillful", "Versatile"},
	},
	"Orc": {
		Size:  "Medium",
		Speed: 30,
		Traits: []string{
			"Adrenaline Rush",
			"Darkvision",
			"Relentless Endurance",
		},
	},
	"Tiefling": {
		Size:  "Medium",
		Speed: 30,
		Traits: []string{
			"Darkvision",
			"Fiendish Legacy",
			"Otherworldly Presence",
		},
	},
}

/*
Returns a slice of DnD species.
*/
func GetD20Species() []string {
	species := slices.Collect(maps.Keys(characterSpecies))
	slices.Sort(species)
	return species
}

/*
Returns size str by species.
*/
func GetSizeBySpecies(species string) string {
	return characterSpecies[species].Size
}

/*
Returns speed int by species.
*/
func GetSpeedBySpecies(species string) int {
	return characterSpecies[species].Speed
}

/*
Returns a slice of traits by species.
*/
func GetTraitsBySpecies(species string) []string {
	return characterSpecies[species].Traits
}
