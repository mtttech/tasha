/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

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
