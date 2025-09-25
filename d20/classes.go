/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

type Class struct {
	Armors       []string
	HitDie       int
	SavingThrows []string
	Features     map[int][]string
	Skills       []string
	Subclasses   []string
	Tools        []string
	Weapons      []string
}

var characterClasses = map[string]Class{
	"Barbarian": {
		Armors:       []string{"Light", "Medium", "Shield"},
		HitDie:       12,
		SavingThrows: []string{"Constitution", "Strength"},
		Skills: []string{
			"Animal Handling",
			"Athletics",
			"Intimidation",
			"Nature",
			"Perception",
			"Survival",
		},
		Subclasses: []string{
			"Path of the Berserker",
			"Path of the Wild Heart",
			"Path of the World Tree",
			"Path of the Zealot",
		},
		Tools:   []string{},
		Weapons: []string{"Simple", "Martial"},
	},
	"Bard": {
		Armors:       []string{"Light"},
		HitDie:       8,
		SavingThrows: []string{"Charisma", "Dexterity"},
		Skills: []string{
			"Acrobatics",
			"Animal Handling",
			"Arcana",
			"Athletics",
			"Deception",
			"History",
			"Insight",
			"Intimidation",
			"Investigation",
			"Medicine",
			"Nature",
			"Perception",
			"Performance",
			"Persuasion",
			"Religion",
			"Sleight of Hand",
			"Stealth",
			"Survival",
		},
		Subclasses: []string{
			"College of Dance",
			"College of Glamour",
			"College of Lore",
			"College of Valor",
		},
		Tools:   []string{},
		Weapons: []string{"Simple"},
	},
	"Cleric": {
		Armors:       []string{"Light", "Medium", "Shield"},
		HitDie:       8,
		SavingThrows: []string{"Intelligence", "Wisdom"},
		Skills: []string{
			"History",
			"Insight",
			"Medicine",
			"Persuasion",
			"Religion",
		},
		Subclasses: []string{
			"Life Domain",
			"Light Domain",
			"Trickery Domain",
			"War Domain",
		},
		Tools:   []string{},
		Weapons: []string{"Simple"},
	},
	"Druid": {
		Armors:       []string{"Light", "Shield"},
		HitDie:       8,
		SavingThrows: []string{"Intelligence", "Wisdom"},
		Skills: []string{
			"Animal Handling",
			"Arcana",
			"Insight",
			"Medicine",
			"Nature",
			"Perception",
			"Religion",
			"Survival",
		},
		Subclasses: []string{
			"Circle of the Land",
			"Circle of the Moon",
			"Circle of the Sea",
			"Circle of the Stars",
		},
		Tools:   []string{"Herbalism Kit"},
		Weapons: []string{"Simple"},
	},
	"Fighter": {
		Armors:       []string{"Light", "Medium", "Shield"},
		HitDie:       10,
		SavingThrows: []string{"Constitution", "Strength"},
		Skills: []string{
			"Acrobatics",
			"Animal Handling",
			"Athletics",
			"History",
			"Insight",
			"Intimidation",
			"Perception",
			"Survival",
		},
		Subclasses: []string{
			"Battle Master",
			"Champion",
			"Eldritch Knight",
			"Psi Warrior",
		},
		Tools:   []string{},
		Weapons: []string{"Simple", "Martial"},
	},
	"Monk": {
		Armors:       []string{},
		HitDie:       8,
		SavingThrows: []string{"Dexterity", "Strength"},
		Skills: []string{
			"Acrobatics",
			"Athletics",
			"History",
			"Insight",
			"Religion",
			"Stealth",
		},
		Subclasses: []string{
			"Warrior of Mercy",
			"Warrior of Shadow",
			"Warrior of the Elements",
			"Warrior of the Open Hand",
		},
		Tools: []string{
			"Artisan's Tools - Alchemists Supplies",
			"Artisan's Tools - Brewer's Supplies",
			"Artisan's Tools - Calligrapher's Supplies",
			"Artisan's Tools - Carpenter's Tools",
			"Artisan's Tools - Cartographer's Tools",
			"Artisan's Tools - Cobbler's Tools",
			"Artisan's Tools - Cook's utensils",
			"Artisan's Tools - Glassblower's Tools",
			"Artisan's Tools - Jeweler's Tools",
			"Artisan's Tools - Leatherworker's Tools",
			"Artisan's Tools - Mason's Tools",
			"Artisan's Tools - Painter's Supplies",
			"Artisan's Tools - Potter's Tools",
			"Artisan's Tools - Smith's Tools",
			"Artisan's Tools - Tinker's Tools",
			"Artisan's Tools - Weaver's Tools",
			"Artisan's Tools - Woodcarver's Tools",
			"Musical Instrument - Bagpipes",
			"Musical Instrument - Birdpipes",
			"Musical Instrument - Drum",
			"Musical Instrument - Dulcimer",
			"Musical Instrument - Flute",
			"Musical Instrument - Glaur",
			"Musical Instrument - Hand Drum",
			"Musical Instrument - Longhorn",
			"Musical Instrument - Lute",
			"Musical Instrument - Lyre",
			"Musical Instrument - Horn",
			"Musical Instrument - Pan flute",
			"Musical Instrument - Shawm",
			"Musical Instrument - Songhorn",
			"Musical Instrument - Tantan",
			"Musical Instrument - Thelarr",
			"Musical Instrument - Tocken",
			"Musical Instrument - Viol",
			"Musical Instrument - Wargong",
			"Musical Instrument - Yarting",
			"Musical Instrument - Zulkoon",
		},
		Weapons: []string{"Simple", "Martial (Light)"},
	},
	"Paladin": {
		Armors:       []string{"Light", "Medium", "Heavy", "Shield"},
		HitDie:       10,
		SavingThrows: []string{"Charisma", "Wisdom"},
		Skills: []string{
			"Athletics",
			"Insight",
			"Intimidation",
			"Medicine",
			"Persuasion",
			"Religion",
		},
		Subclasses: []string{
			"Oath of Devotion",
			"Oath of Glory",
			"Oath of the Ancients",
			"Oath of Vengeance",
		},
		Tools:   []string{},
		Weapons: []string{"Simple", "Martial"},
	},
	"Ranger": {
		Armors:       []string{"Light", "Medium", "Shield"},
		HitDie:       10,
		SavingThrows: []string{"Dexterity", "Strength"},
		Skills: []string{
			"Animal Handling",
			"Athletics",
			"Insight",
			"Investigation",
			"Nature",
			"Perception",
			"Sleight of Hand",
			"Stealth",
			"Survival",
		},
		Subclasses: []string{
			"Beast Master",
			"Fey Wanderer",
			"Gloom Stalker",
			"Hunter",
		},
		Tools:   []string{},
		Weapons: []string{"Simple", "Martial"},
	},
	"Rogue": {
		Armors:       []string{"Light"},
		HitDie:       8,
		SavingThrows: []string{"Dexterity", "Intelligence"},
		Skills: []string{
			"Acrobatics",
			"Athletics",
			"Deception",
			"Insight",
			"Intimidation",
			"Investigation",
			"Perception",
			"Performance",
			"Persuasion",
			"Sleight of Hand",
			"Stealth",
		},
		Subclasses: []string{
			"Arcane Trickster",
			"Assassin",
			"Soulknife",
			"Thief",
		},
		Tools:   []string{"Thieves' Tools"},
		Weapons: []string{"Simple", "Martial (Finesse, Light)"},
	},
	"Sorcerer": {
		Armors:       []string{},
		HitDie:       6,
		SavingThrows: []string{"Charisma", "Constitution"},
		Skills: []string{
			"Arcana",
			"Deception",
			"Insight",
			"Intimidation",
			"Persuasion",
			"Religion",
		},
		Subclasses: []string{
			"Aberrant Sorcery",
			"Clockwork Sorcery",
			"Draconic Sorcery",
			"Wild Magic Sorcery",
		},
		Tools:   []string{},
		Weapons: []string{"Simple"},
	},
	"Warlock": {
		Armors:       []string{"Light"},
		HitDie:       8,
		SavingThrows: []string{"Charisma", "Wisdom"},
		Skills: []string{
			"Arcana",
			"Deception",
			"History",
			"Intimidation",
			"Investigation",
			"Nature",
			"Religion",
		},
		Subclasses: []string{
			"Archfey Patron",
			"Celestial Patron",
			"Fiend Patron",
			"Great Old One Patron",
		},
		Tools:   []string{},
		Weapons: []string{"Simple"},
	},
	"Wizard": {
		Armors:       []string{},
		HitDie:       6,
		SavingThrows: []string{"Intelligence", "Wisdom"},
		Skills: []string{
			"Arcana",
			"History",
			"Insight",
			"Investigation",
			"Medicine",
			"Religion",
		},
		Subclasses: []string{
			"Abjurer",
			"Diviner",
			"Evoker",
			"Illusionist",
		},
		Tools:   []string{},
		Weapons: []string{"Simple"},
	},
}

/*
Returns a slice of armor proficiencies by class.
*/
func GetArmorsByClass(class string) []string {
	return characterClasses[class].Armors
}

/*
Returns a slice of DnD classes.
*/
func GetD20Classes() []string {
	classes := slices.Collect(maps.Keys(characterClasses))
	slices.Sort(classes)
	return classes
}

/*
Returns hit die by class.
*/
func GetHitDieByClass(class string) int {
	return characterClasses[class].HitDie
}

/*
Returns level slices from 1 to max.
*/
func GetLevelSlices(max int) []int {
	var levels []int
	for i := 1; i <= max; i++ {
		levels = append(levels, i)
	}
	return levels
}

/*
Returns a slice of saving throws by class.
*/
func GetSavingThrowsByClass(class string) []string {
	return characterClasses[class].Subclasses
}

/*
Gets the number of skill points by class.
*/
func GetSkillPointsByClass(class string, is_primary_class bool) int {
	var allottedSkills = 0
	switch class {
	case "Rogue":
		allottedSkills = 4
	case "Bard", "Ranger":
		if is_primary_class {
			allottedSkills = 3
		} else {
			allottedSkills = 1
		}
	default:
		if is_primary_class {
			allottedSkills = 2
		}
	}
	return allottedSkills
}

/*
Returns a slice of skills by class.
*/
func GetSkillsByClass(class string) []string {
	return characterClasses[class].Skills
}

/*
Returns a slice of subclasses by class.
*/
func GetSubclassesByClass(class string) []string {
	return characterClasses[class].Subclasses
}

/*
Returns a slice of tool proficiencies by class.
*/
func GetToolsByClass(class string) []string {
	return characterClasses[class].Tools
}

/*
Returns a slice of weapon proficiencies by class.
*/
func GetWeaponsByClass(class string) []string {
	return characterClasses[class].Weapons
}
