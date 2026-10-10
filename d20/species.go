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

type Species struct {
	Name   string   `json:"name"`
	Size   string   `json:"size"`
	Speed  int      `json:"speed"`
	Traits []string `json:"traits"`
}

func LoadSpecies() map[string]Species {
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

var characterSpecies = LoadSpecies()

/*
Returns a slice of DnD species.
*/
func GetD20Species() []string {
	species := slices.Collect(maps.Keys(characterSpecies))
	slices.Sort(species)
	return species
}

/*
Returns size by species s.
*/
func GetSizeBySpecies(s string) string {
	return characterSpecies[s].Size
}

/*
Returns speed by species s.
*/
func GetSpeedBySpecies(s string) int {
	return characterSpecies[s].Speed
}

/*
Returns traits by species s.
*/
func GetTraitsBySpecies(s string) []string {
	return characterSpecies[s].Traits
}
