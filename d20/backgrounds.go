/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

type Background struct {
	Ability []string
	Feats   []string
	Skills  []string
	Tools   []string
}

var characterBackgrounds = map[string]Background{
	"Acolyte": {
		Ability: []string{"Intelligence", "Wisdom", "Charisma"},
		Feats:   []string{"Magic Initiate"},
		Skills:  []string{"Insight", "Religion"},
		Tools:   []string{"Artisan's Tools - Cartographer's Supplies"},
	},
	"Artisan": {
		Ability: []string{"Strength", "Dexterity", "Intelligence"},
		Feats:   []string{"Crafter"},
		Skills:  []string{"Investigation", "Persuasion"},
		Tools: []string{
			"Artisan's Tools - Alchemists supplies",
			"Artisan's Tools - Brewer's supplies",
			"Artisan's Tools - Calligrapher's supplies",
			"Artisan's Tools - Carpenter's Tools",
			"Artisan's Tools - Cartographer's Tools",
			"Artisan's Tools - Cobbler's Tools",
			"Artisan's Tools - Cook's utensils",
			"Artisan's Tools - Glassblower's Tools",
			"Artisan's Tools - Jeweler's Tools",
			"Artisan's Tools - Leatherworker's Tools",
			"Artisan's Tools - Mason's Tools",
			"Artisan's Tools - Painter's supplies",
			"Artisan's Tools - Potter's Tools",
			"Artisan's Tools - Smith's Tools",
			"Artisan's Tools - Tinker's Tools",
			"Artisan's Tools - Weaver's Tools",
			"Artisan's Tools - Woodcarver's Tools",
		},
	},
	"Charlatan": {
		Ability: []string{"Dexterity", "Constitution", "Charisma"},
		Feats:   []string{"Skilled"},
		Skills:  []string{"Deception", "Sleight of Hand"},
		Tools:   []string{"Forgery Kit"},
	},
	"Criminal": {
		Ability: []string{"Dexterity", "Constitution", "Intelligence"},
		Feats:   []string{"Alert"},
		Skills:  []string{"Deception", "Stealth"},
		Tools:   []string{"Thieves' Tools"},
	},
	"Entertainer": {
		Ability: []string{"Strength", "Dexterity", "Charisma"},
		Feats:   []string{"Musician"},
		Skills:  []string{"Acrobatics", "Performance"},
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
	},
	"Farmer": {
		Ability: []string{"Strength", "Constitution", "Wisdom"},
		Feats:   []string{"Tough"},
		Skills:  []string{"Animal Handling", "Nature"},
		Tools:   []string{"Artisan's Tools - Carpenter's Tools"},
	},
	"Guard": {
		Ability: []string{"Strength", "Intelligence", "Wisdom"},
		Feats:   []string{"Alert"},
		Skills:  []string{"Athletics", "Perception"},
		Tools: []string{
			"Gaming Set - Dice Set",
			"Gaming Set - Dragonchess Set",
			"Gaming Set - Playing card Set",
			"Gaming Set - Three-Dragon Ante Set",
		},
	},
	"Guide": {
		Ability: []string{"Dexterity", "Constitution", "Wisdom"},
		Feats:   []string{"Magic Initiate"},
		Skills:  []string{"Stealth", "Survival"},
		Tools:   []string{"Artisan's Tools - Cartographer's Tools"},
	},
	"Hermit": {
		Ability: []string{"Constitution", "Wisdom", "Charisma"},
		Feats:   []string{"Healer"},
		Skills:  []string{"Medicine", "Religion"},
		Tools:   []string{"Herbalism kit"},
	},
	"Merchant": {
		Ability: []string{"Constitution", "Intelligence", "Charisma"},
		Feats:   []string{"Lucky"},
		Skills:  []string{"Animal Handling", "Persuasion"},
		Tools:   []string{"Navigator's Tools"},
	},
	"Noble": {
		Ability: []string{"Strength", "Intelligence", "Charisma"},
		Feats:   []string{"Skilled"},
		Skills:  []string{"History", "Persuasion"},
		Tools: []string{
			"Gaming Set - Dice Set",
			"Gaming Set - Dragonchess Set",
			"Gaming Set - Playing card Set",
			"Gaming Set - Three-Dragon Ante Set",
		},
	},
	"Sage": {
		Ability: []string{"Constitution", "Intelligence", "Wisdom"},
		Feats:   []string{"Magic Initiate"},
		Skills:  []string{"Arcana", "History"},
		Tools:   []string{"Artisan's Tools - Cartographer's Supplies"},
	},
	"Sailor": {
		Ability: []string{"Strength", "Dexterity", "Wisdom"},
		Feats:   []string{"Tavern Brawler"},
		Skills:  []string{"Athletics", "Perception"},
		Tools: []string{
			"Gaming Set - Dice Set",
			"Gaming Set - Dragonchess Set",
			"Gaming Set - Playing card Set",
			"Gaming Set - Three-Dragon Ante Set",
		},
	},
	"Scribe": {
		Ability: []string{"Dexterity", "Intelligence", "Wisdom"},
		Feats:   []string{"Skilled"},
		Skills:  []string{"Investigation", "Perception"},
		Tools:   []string{"Artisan's Tools - Cartographer's Supplies"},
	},
	"Soldier": {
		Ability: []string{"Strength", "Dexterity", "Constitution"},
		Feats:   []string{"Savage Attacker"},
		Skills:  []string{"Athletics", "Intimidation"},
		Tools:   []string{"Artisan's Tools - Cartographer's Supplies"},
	},
	"Wayfarer": {
		Ability: []string{"Dexterity", "Wisdom", "Charisma"},
		Feats:   []string{"Lucky"},
		Skills:  []string{"Insight", "Stealth"},
		Tools:   []string{"Thieves' Tools"},
	},
}

/*
Returns a slice of abilities by background.
*/
func GetAbilitiesByBackground(background string) []string {
	return characterBackgrounds[background].Ability
}

/*
Returns a slice of DnD backgrounds.
*/
func GetD20Backgrounds() []string {
	backgrounds := slices.Collect(maps.Keys(characterBackgrounds))
	slices.Sort(backgrounds)
	return backgrounds
}

/*
Returns a slice of feats by background.
*/
func GetFeatByBackground(background string) []string {
	return characterBackgrounds[background].Feats
}

/*
Returns a slice of skills by background.
*/
func GetSkillsByBackground(background string) []string {
	return characterBackgrounds[background].Skills
}

/*
Returns a slice of tools by background.
*/
func GetToolsByBackground(background string) []string {
	return characterBackgrounds[background].Tools
}
