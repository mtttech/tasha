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
)

type Background struct {
	Name    string   `json:"name"`
	Ability []string `json:"ability"`
	Feats   []string `json:"feats"`
	Skills  []string `json:"skills"`
	Tools   []string `json:"tools"`
}

func load_backgrounds() map[string]Background {
	byteValue, err := os.ReadFile("json/backgrounds.json")
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var backgrounds []Background
	err = json.Unmarshal(byteValue, &backgrounds)
	if err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	b := make(map[string]Background)
	for _, background := range backgrounds {
		b[background.Name] = Background{background.Name, background.Ability, background.Feats, background.Skills, background.Tools}
	}

	return b
}

var characterBackgrounds = load_backgrounds()

/*
Returns a slice of abilities by background b.
*/
func GetAssociatedAbilitiesByBackground(b string) []string {
	return characterBackgrounds[b].Ability
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
Returns a slice of feats by background b.
*/
func GetFeatByBackground(b string) []string {
	return characterBackgrounds[b].Feats
}

/*
Returns a slice of skills by background b.
*/
func GetSkillsByBackground(b string) []string {
	return characterBackgrounds[b].Skills
}

/*
Returns a slice of tools by background b.
*/
func GetToolsByBackground(b string) []string {
	return characterBackgrounds[b].Tools
}
