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
		AbilityScores map[string]abilities.AbilityScore `toml:"ability_scores"`
		Class         map[string]d20.Class              `toml:"class"`
		Features      []string                          `toml:"features"`
		Skills        []string                          `toml:"skills"`
	}
}
