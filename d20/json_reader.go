/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"encoding/json"
	"log"
	"os"
)

var characterBackgrounds = load_backgrounds()
var characterClasses = load_classes()
var characterFeats = load_feats()
var characterSkills = load_skills()
var characterSpecies = load_species()

type Background struct {
	Name    string   `json:"name"`
	Ability []string `json:"ability"`
	Feats   []string `json:"feats"`
	Skills  []string `json:"skills"`
	Tools   []string `json:"tools"`
}

type Class struct {
	Subclass string
	Level    int
}

type Classes struct {
	Name         string           `json:"name"`
	Armors       []string         `json:"armors"`
	Features     map[int][]string `json:"features"`
	HitDie       int              `json:"hit_die"`
	SavingThrows []string         `json:"saving_throws"`
	Subclasses   []string         `json:"subclasses"`
	Tools        []string         `json:"tools"`
	Weapons      []string         `json:"weapons"`
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

type Skills struct {
	Name    string   `json:"name"`
	Ability string   `json:"ability"`
	Classes []string `json:"classes"`
}

type Species struct {
	Name   string   `json:"name"`
	Size   string   `json:"size"`
	Speed  int      `json:"speed"`
	Traits []string `json:"traits"`
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

func load_classes() map[string]Classes {
	byteValue, err := os.ReadFile("json/classes.json")
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var classes []Classes
	err = json.Unmarshal(byteValue, &classes)
	if err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	c := make(map[string]Classes)
	for _, class := range classes {
		c[class.Name] = Classes{class.Name, class.Armors, class.Features, class.HitDie, class.SavingThrows, class.Subclasses, class.Tools, class.Weapons}
	}

	return c
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

func load_skills() map[string]Skills {
	byteValue, err := os.ReadFile("json/skills.json")
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var skills []Skills
	err = json.Unmarshal(byteValue, &skills)
	if err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	s := make(map[string]Skills)
	for _, skill := range skills {
		s[skill.Name] = Skills{skill.Name, skill.Ability, skill.Classes}
	}

	return s
}

func load_species() map[string]Species {
	byteValue, err := os.ReadFile("json/species.json")
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var species []Species
	err = json.Unmarshal(byteValue, &species)
	if err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	s := make(map[string]Species)
	for _, specie := range species {
		s[specie.Name] = Species{specie.Name, specie.Size, specie.Speed, specie.Traits}
	}

	return s
}
