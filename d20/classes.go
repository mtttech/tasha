/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

type Class struct {
	Subclass string
	Level    int
}

type Classes struct {
	Armors       []string
	Features     map[int][]string
	HitDie       int
	SavingThrows []string
	Subclasses   []string
	Tools        []string
	Weapons      []string
}

var characterClasses = map[string]Classes{
	"Barbarian": {
		Armors: []string{"Light", "Medium", "Shield"},
		Features: map[int][]string{
			1:  {"Rage", "Unarmored Defense", "Weapon Mastery"},
			2:  {"Danger Sense", "Reckless Attack"},
			3:  {"Barbarian Subclass", "Primal Knowledge"},
			4:  {"Ability Score Improvement"},
			5:  {"Extra Attack", "Fast Movement"},
			7:  {"Feral Instinct", "Instinctive Pounce"},
			8:  {"Ability Score Improvement"},
			9:  {"Brutal Strike"},
			11: {"Relentless Rage"},
			12: {"Ability Score Improvement"},
			13: {"Improved Brutal Strike"},
			15: {"Persistent Rage"},
			16: {"Ability Score Improvement"},
			17: {"Improved Brutal Strike"},
			18: {"Indomitable Might"},
			19: {"Epic Boon"},
			20: {"Primal Champion"},
		},
		HitDie:       12,
		SavingThrows: []string{"Constitution", "Strength"},
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
		Armors: []string{"Light"},
		Features: map[int][]string{
			1:  {"Bardic Inspiration", "Spellcasting"},
			2:  {"Expertise", "Jack of All Trades"},
			3:  {"Bard Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Font of Inspiration"},
			7:  {"Countercharm"},
			8:  {"Ability Score Improvement"},
			9:  {"Expertise"},
			10: {"Magical Secrets"},
			12: {"Ability Score Improvement"},
			16: {"Ability Score Improvement"},
			18: {"Superior Inspiration"},
			19: {"Epic Boon"},
			20: {"Words of Creation"},
		},
		HitDie:       8,
		SavingThrows: []string{"Charisma", "Dexterity"},
		Subclasses: []string{
			"College of Dance",
			"College of Glamour",
			"College of Lore",
			"College of Valor",
		},
		Tools: []string{
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
		Weapons: []string{"Simple"},
	},
	"Cleric": {
		Armors: []string{"Light", "Medium", "Shield"},
		Features: map[int][]string{
			1:  {"Divine Order", "Spellcasting"},
			2:  {"Channel Divinity"},
			3:  {"Cleric Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Sear Undead"},
			7:  {"Blessed Strikes"},
			8:  {"Ability Score Improvement"},
			10: {"Divine Intervention"},
			12: {"Ability Score Improvement"},
			14: {"Improved Blessed Strikes"},
			16: {"Ability Score Improvement"},
			19: {"Epic Boon"},
			20: {"Greater Divine Intervention"},
		},
		HitDie:       8,
		SavingThrows: []string{"Intelligence", "Wisdom"},
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
		Armors: []string{"Light", "Shield"},
		Features: map[int][]string{
			1:  {"Druidic", "Primal Order", "Spellcasting"},
			2:  {"Wild Companion", "Wild Shape"},
			3:  {"Druid Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Wild Resurgence"},
			7:  {"Elemental Fury"},
			8:  {"Ability Score Improvement"},
			12: {"Ability Score Improvement"},
			15: {"Improved Elemental Fury"},
			16: {"Ability Score Improvement"},
			18: {"Beast Spells"},
			19: {"Epic Boon"},
			20: {"Archdruid"},
		},
		HitDie:       8,
		SavingThrows: []string{"Intelligence", "Wisdom"},
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
		Armors: []string{"Light", "Medium", "Shield"},
		Features: map[int][]string{
			1:  {"Fighting Style", "Second Wind", "Weapon Mastery"},
			2:  {"Action Surge (one use)", "Tactical Mind"},
			3:  {"Fighter Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Extra Attack", "Tactical Shift"},
			6:  {"Ability Score Improvement"},
			8:  {"Ability Score Improvement"},
			9:  {"Indomitable (one use)", "Tactical Master"},
			11: {"Two Extra Attacks"},
			12: {"Ability Score Improvement"},
			13: {"Indomitable (two uses)", "Studied Attacks"},
			14: {"Ability Score Improvement"},
			16: {"Ability Score Improvement"},
			17: {"Action Surge (two uses)", "Indomitable (three uses)"},
			19: {"Epic Boon"},
			20: {"Three Extra Attacks"},
		},
		HitDie:       10,
		SavingThrows: []string{"Constitution", "Strength"},
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
		Armors: []string{},
		Features: map[int][]string{
			1:  {"Martial Arts", "Unarmored Defense"},
			2:  {"Monk's Focus", "Unarmored Movement", "Uncanny Metabolism"},
			3:  {"Deflect Attacks", "Monk Subclass"},
			4:  {"Ability Score Improvement", "Slow Fall"},
			5:  {"Extra Attack", "Stunning Strike"},
			6:  {"Empowered Strikes"},
			7:  {"Evasion"},
			8:  {"Ability Score Improvement"},
			9:  {"Acrobatic Movement"},
			10: {"Heightened Focus", "Self-Restoration"},
			12: {"Ability Score Improvement"},
			13: {"Deflect Energy"},
			14: {"Disciplined Survivor"},
			15: {"Perfect Focus"},
			16: {"Ability Score Improvement"},
			18: {"Superior Defense"},
			19: {"Epic Boon"},
			20: {"Body and Mind"},
		},
		HitDie:       8,
		SavingThrows: []string{"Dexterity", "Strength"},
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
		Armors: []string{"Light", "Medium", "Heavy", "Shield"},
		Features: map[int][]string{
			1:  {"Lay on Hands", "Spellcasting", "Weapon Mastery"},
			2:  {"Fighting Style", "Paladin's Smite"},
			3:  {"Channel Divinity", "Paladin Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Extra Attack", "Faithful Steed"},
			6:  {"Aura of Protection"},
			8:  {"Ability Score Improvement"},
			9:  {"Abjure Foes"},
			10: {"Aura of Courage"},
			11: {"Radiant Strikes"},
			12: {"Ability Score Improvement"},
			14: {"Restoring Touch"},
			16: {"Ability Score Improvement"},
			18: {"Aura Expansion"},
			19: {"Epic Boon"},
		},
		HitDie:       10,
		SavingThrows: []string{"Charisma", "Wisdom"},
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
		Armors: []string{"Light", "Medium", "Shield"},
		Features: map[int][]string{
			1:  {"Favored Enemy", "Spellcasting", "Weapon Mastery"},
			2:  {"Deft Explorer", "Fighting Style"},
			3:  {"Ranger Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Extra Attack"},
			6:  {"Roving"},
			8:  {"Ability Score Improvement"},
			9:  {"Expertise"},
			10: {"Tireless"},
			12: {"Ability Score Improvement"},
			13: {"Relentless Hunter"},
			14: {"Nature's Veil"},
			16: {"Ability Score Improvement"},
			17: {"Precise Hunter"},
			18: {"Feral Senses"},
			19: {"Epic Boon"},
			20: {"Foe Slayer"},
		},
		HitDie:       10,
		SavingThrows: []string{"Dexterity", "Strength"},
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
		Armors: []string{"Light"},
		Features: map[int][]string{
			1:  {"Expertise", "Sneak Attack", "Thieves' Cant", "Weapon Mastery"},
			2:  {"Cunning Action"},
			3:  {"Rogue Subclass", "Steady Aim"},
			4:  {"Ability Score Improvement"},
			5:  {"Cunning Strike", "Uncanny Dodge"},
			7:  {"Evasion", "Reliable Talent"},
			8:  {"Ability Score Improvement"},
			10: {"Ability Score Improvement"},
			11: {"Improved Cunning Strike"},
			12: {"Ability Score Improvement"},
			14: {"Devious Strikes"},
			15: {"Slippery Mind"},
			16: {"Ability Score Improvement"},
			18: {"Elusive"},
			19: {"Epic Boon"},
			20: {"Stroke of Luck"},
		},
		HitDie:       8,
		SavingThrows: []string{"Dexterity", "Intelligence"},
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
		Armors: []string{},
		Features: map[int][]string{
			1:  {"Innate Sorcery", "Spellcasting"},
			2:  {"Font of Magic", "Metamagic"},
			3:  {"Sorcerer Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Sorcerous Restoration"},
			7:  {"Sorcery Incarnate"},
			8:  {"Ability Score Improvement"},
			12: {"Ability Score Improvement"},
			16: {"Ability Score Improvement"},
			19: {"Epic Boon"},
			20: {"Arcane Apotheosis"},
		},
		HitDie:       6,
		SavingThrows: []string{"Charisma", "Constitution"},
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
		Armors: []string{"Light"},
		Features: map[int][]string{
			1:  {"Eldritch Invocations", "Pact Magic"},
			2:  {"Magical Cunning"},
			3:  {"Warlock Subclass"},
			4:  {"Ability Score Improvement"},
			8:  {"Ability Score Improvement"},
			9:  {"Contact Patron"},
			11: {"Mystic Arcanum (level 6 spell)"},
			12: {"Ability Score Improvement"},
			13: {"Mystic Arcanum (level 7 spell)"},
			15: {"Mystic Arcanum (level 8 spell)"},
			16: {"Ability Score Improvement"},
			17: {"Mystic Arcanum (level 9 spell)"},
			19: {"Epic Boon"},
			20: {"Eldritch Master"},
		},
		HitDie:       8,
		SavingThrows: []string{"Charisma", "Wisdom"},
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
		Armors: []string{},
		Features: map[int][]string{
			1:  {"Arcane Recovery", "Ritual Adept", "Spellcasting"},
			2:  {"Scholar"},
			3:  {"Wizard Subclass"},
			4:  {"Ability Score Improvement"},
			5:  {"Memorize Spell"},
			8:  {"Ability Score Improvement"},
			12: {"Ability Score Improvement"},
			16: {"Ability Score Improvement"},
			18: {"Spell Mastery"},
			19: {"Epic Boon"},
			20: {"Signature Spells"},
		},
		HitDie:       6,
		SavingThrows: []string{"Intelligence", "Wisdom"},
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
func GetArmorsByClass(c string) []string {
	return characterClasses[c].Armors
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
Returns a slice of class features by class and level.
*/
func GetFeaturesByClass(c string, l int) []string {
	class_features := []string{}
	for level, features := range characterClasses[c].Features {
		if l >= level {
			class_features = append(class_features, features...)
		}
	}
	slices.Sort(class_features)
	return class_features
}

/*
Returns hit die by class.
*/
func GetHitDieByClass(c string) int {
	return characterClasses[c].HitDie
}

/*
Returns level slices from 1 to max.
*/
func GetLevelSlices(m int) []int {
	var levels []int
	for i := 1; i <= m; i++ {
		levels = append(levels, i)
	}
	return levels
}

/*
Returns a slice of saving throws by class.
*/
func GetSavingThrowsByClass(c string) []string {
	return characterClasses[c].Subclasses
}

/*
Gets the number of skill points by class and if primary or secondary class p.
*/
func GetSkillPointsByClass(c string, p bool) int {
	allotted_skills := 0
	switch c {
	case "Rogue":
		allotted_skills = 4
	case "Bard", "Ranger":
		if p {
			allotted_skills = 3
		} else {
			allotted_skills = 1
		}
	default:
		if p {
			allotted_skills = 2
		}
	}
	return allotted_skills
}

/*
Returns a slice of subclasses by class c.
*/
func GetSubclassesByClass(c string) []string {
	return characterClasses[c].Subclasses
}

/*
Returns a slice of tool proficiencies by class c.
*/
func GetToolsByClass(c string) []string {
	return characterClasses[c].Tools
}

/*
Returns a slice of tool proficiencies by class c.
*/
func GetTotalLevel(c map[string]Class) int {
	totalLevel := 0
	for _, class := range c {
		totalLevel += class.Level
	}
	return totalLevel
}

/*
Returns a slice of weapon proficiencies by class c.
*/
func GetWeaponsByClass(c string) []string {
	return characterClasses[c].Weapons
}
