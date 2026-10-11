/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"encoding/json"
	"log"
	"maps"
	"os"
	"slices"

	"tasha/abilities"
)

type AbilityScoreRequirements struct {
	Ability string
	Score   int
}

type Feat struct {
	Name     string                     `json:"name"`
	Ability  []AbilityScoreRequirements `json:"ability"`
	Armors   []string                   `json:"armors"`
	Category string                     `json:"category"`
	Features []string                   `json:"features"`
	Level    int                        `json:"level"`
	Tools    []string                   `json:"tools"`
	Weapons  []string                   `json:"weapons"`
}

func load_feats() map[string]Feat {
	byteValue, err := os.ReadFile("json/feats.json")
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var feats []Feat
	err = json.Unmarshal(byteValue, &feats)
	if err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	f := make(map[string]Feat)
	for _, feat := range feats {
		f[feat.Name] = Feat{feat.Name, feat.Ability, feat.Armors, feat.Category, feat.Features, feat.Level, feat.Tools, feat.Weapons}
	}

	return f
}

var characterFeats = load_feats()

/*
Returns true if the class feature f is found in the slice of class features k.
*/
func has_feature(f string, k []string) bool {
	for _, feature := range characterFeats[f].Features {
		if slices.Contains(k, feature) {
			return true
		}
	}
	return false
}

/*
Returns a map of ability requirements by feat f.
*/
func GetAbilityScoreRequirementsByFeat(f string) map[string]int {
	requirements := make(map[string]int)
	required_abilities := characterFeats[f].Ability
	if len(required_abilities) > 0 {
		for _, values := range required_abilities {
			requirements[values.Ability] = values.Score
		}
	}
	return requirements
}

/*
Calculates the number of allotted feats by specified class features f.
*/
func GetAllottedFeats(f []string) int {
	numberOfFeats := 0
	for _, feature := range f {
		if feature == "Ability Score Improvement" {
			numberOfFeats += 1
		}
	}
	return numberOfFeats
}

/*
Returns a slice of feats by level l, checking ability scores s, feats f and class features c requirements.
*/
func GetD20Feats(l int, s map[string]abilities.AbilityScore, f []string, c []string) []string {
	feats := []string{}
	for _, feat := range slices.Collect(maps.Keys(characterFeats)) {
		// Ignore the Ability Score Improvement feat or already possesses the feat
		if feat != "Ability Score Improvement" && slices.Contains(f, feat) {
			continue
		}
		// Check ability score requirements
		ability_requirements := GetAbilityScoreRequirementsByFeat(feat)
		if len(ability_requirements) != 0 {
			switch feat {
			case "Athlete", "Charger", "Dual Wielder", "Grappler", "Polearm Master", "Sentinel":
				if s["Dexterity"].Score < ability_requirements["Dexterity"] && s["Strength"].Score < ability_requirements["Strength"] {
					continue
				}
			case "Inspiring Leader":
				if s["Charisma"].Score < ability_requirements["Charisma"] && s["Wisdom"].Score < ability_requirements["Wisdom"] {
					continue
				}
			case "Observant":
				if s["Intelligence"].Score < ability_requirements["Intelligence"] && s["Wisdom"].Score < ability_requirements["Wisdom"] {
					continue
				}
			case "Ritual Caster":
				if s["Charisma"].Score < ability_requirements["Charisma"] && s["Intelligence"].Score < ability_requirements["Intelligence"] && s["Wisdom"].Score < ability_requirements["Wisdom"] {
					continue
				}
			case "Speedy":
				if s["Dexterity"].Score < ability_requirements["Dexterity"] && s["Constitution"].Score < ability_requirements["Constitution"] {
					continue
				}
			default:
				for _, ability := range slices.Collect(maps.Keys(ability_requirements)) {
					if s[ability].Score < ability_requirements[ability] {
						continue
					}
				}
			}
		}
		// Check features requirements
		if !has_feature(feat, c) {
			continue
		}
		// Check character level requirements
		if l < characterFeats[feat].Level {
			continue
		}
		feats = append(feats, feat)
	}
	slices.Sort(feats)
	return feats
}
