/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package record

import (
	"tasha/abilities"
	"tasha/d20"
)

type CharacterSheetTOMLSchema struct {
	PC struct {
		Name          string                            `toml:"name"`
		Species       string                            `toml:"species"`
		Gender        string                            `toml:"gender"`
		Background    string                            `toml:"background"`
		Classes       map[string]d20.Class              `toml:"classes"`
		AbilityScores map[string]abilities.AbilityScore `toml:"ability_scores"`
		Skills        []string                          `toml:"skills"`
	}
}
