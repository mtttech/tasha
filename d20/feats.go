/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"

	"tasha/abilities"
)

type AbilityScoreRequirements struct {
	Ability string
	Score   int
}

type Feat struct {
	Ability  []AbilityScoreRequirements
	Armors   []string
	Category string
	Features []string
	Level    int
	Tools    []string
	Weapons  []string
}

var characterFeats = map[string]Feat{
	"Ability Score Improvement": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Actor": {
		Ability:  []AbilityScoreRequirements{{Ability: "Charisma", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Alert": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Archery": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Athlete": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}, {Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Blind Fighting": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Combat Prowess": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Dimensional Travel": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Energy Resistance": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Fate": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Fortitude": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Irresistible Offense": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Recovery": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Skill": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Speed": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Spell Recall": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{"Spellcasting"},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of the Night Spirit": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Boon of Truesight": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Epic Boon",
		Features: []string{},
		Level:    19,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Charger": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}, {Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Chef": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Crafter": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Crossbow Expert": {
		Ability:  []AbilityScoreRequirements{{Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Crusher": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Defense": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Defensive Duelist": {
		Ability:  []AbilityScoreRequirements{{Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Dual Wielder": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}, {Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Dueling": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Durable": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Elemental Adept": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{"Pact Magic", "Spellcasting"},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Fey-Touched": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Grappler": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}, {Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Great Weapon Fighting": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Great Weapon Master": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Healer": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Heavily Armored": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{"Medium"},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Heavy Armor Master": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{"Heavy"},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Inspiring Leader": {
		Ability:  []AbilityScoreRequirements{{Ability: "Wisdom", Score: 13}, {Ability: "Charisma", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Interception": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Keen Mind": {
		Ability:  []AbilityScoreRequirements{{Ability: "Intelligence", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Lightly Armored": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{"Light", "Shields"},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Lucky": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Mage Slayer": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Magic Initiate": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Martial Weapon Training": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Medium Armor Master": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{"Medium"},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Moderately Armored": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{"Light"},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Mounted Combatant": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Musician": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Observant": {
		Ability:  []AbilityScoreRequirements{{Ability: "Intelligence", Score: 13}, {Ability: "Wisdom", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Piercer": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Poisoner": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Polearm Master": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}, {Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Protection": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Resilient": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Ritual Caster": {
		Ability:  []AbilityScoreRequirements{{Ability: "Intelligence", Score: 13}, {Ability: "Wisdom", Score: 13}, {Ability: "Charisma", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{"Pact Magic", "Spellcasting"},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Savage Attacker": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Sentinel": {
		Ability:  []AbilityScoreRequirements{{Ability: "Strength", Score: 13}, {Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Shadow-Touched": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Sharpshooter": {
		Ability:  []AbilityScoreRequirements{{Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Shield Master": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{"Shield"},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Skilled": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Skill Expert": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Skulker": {
		Ability:  []AbilityScoreRequirements{{Ability: "Dexterity", Score: 13}},
		Armors:   []string{},
		Features: []string{},
		Category: "General",
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Slasher": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Speedy": {
		Ability:  []AbilityScoreRequirements{{Ability: "Dexterity", Score: 13}, {Ability: "Constitution", Score: 13}},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Spell Sniper": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{"Spellcasting", "Pact Magic"},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Tavern Brawler": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Origin",
		Features: []string{},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Telekinetic": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Telepathic": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Thrown Weapon Fighting": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Tough": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Features: []string{},
		Category: "Origin",
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Two-Weapon Fighting": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Unarmed Fighting": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "Fighting Style",
		Features: []string{"Fighting Style"},
		Level:    1,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"War Caster": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{"Spellcasting", "Pact Magic"},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
	"Weapon Master": {
		Ability:  []AbilityScoreRequirements{},
		Armors:   []string{},
		Category: "General",
		Features: []string{},
		Level:    4,
		Tools:    []string{},
		Weapons:  []string{},
	},
}

/*
Returns a map of ability/score requirements by feat.
*/
func GetAbilityScoreRequirementsByFeat(feat string) map[string]int {
	requirements := make(map[string]int)
	required_abilities := characterFeats[feat].Ability
	if len(required_abilities) > 0 {
		for _, values := range required_abilities {
			requirements[values.Ability] = values.Score
		}
	}
	return requirements
}

/*
Returns a slice of DnD feats.
*/
func GetD20Feats(level int, ability_scores map[string]abilities.AbilityScore, known_feats []string) []string {
	feats := []string{}
	for _, feat := range slices.Collect(maps.Keys(characterFeats)) {
		// Already possesses this feat
		if feat != "Ability Score Improvement" && slices.Contains(known_feats, feat) {
			continue
		}
		// Check ability score requirements
		ability_requirements := GetAbilityScoreRequirementsByFeat(feat)
		if len(ability_requirements) != 0 {
			switch feat {
			case "Athlete", "Charger", "Dual Wielder", "Grappler", "Polearm Master", "Sentinel":
				if ability_scores["Dexterity"].Score < ability_requirements["Dexterity"] && ability_scores["Strength"].Score < ability_requirements["Strength"] {
					continue
				}
			case "Inspiring Leader":
				if ability_scores["Charisma"].Score < ability_requirements["Charisma"] && ability_scores["Wisdom"].Score < ability_requirements["Wisdom"] {
					continue
				}
			case "Observant":
				if ability_scores["Intelligence"].Score < ability_requirements["Intelligence"] && ability_scores["Wisdom"].Score < ability_requirements["Wisdom"] {
					continue
				}
			case "Ritual Caster":
				if ability_scores["Charisma"].Score < ability_requirements["Charisma"] && ability_scores["Intelligence"].Score < ability_requirements["Intelligence"] && ability_scores["Wisdom"].Score < ability_requirements["Wisdom"] {
					continue
				}
			case "Speedy":
				if ability_scores["Dexterity"].Score < ability_requirements["Dexterity"] && ability_scores["Constitution"].Score < ability_requirements["Constitution"] {
					continue
				}
			default:
				for _, ability := range slices.Collect(maps.Keys(ability_requirements)) {
					if ability_scores[ability].Score < ability_requirements[ability] {
						continue
					}
				}
			}
		}
		// Check character level requirements
		if level < characterFeats[feat].Level {
			continue
		}
		feats = append(feats, feat)
	}
	slices.Sort(feats)
	return feats
}
