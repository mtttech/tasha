/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package actor

import (
	"tasha/attributes"
	"tasha/d20"
)

type Config struct {
	PlayerCharacter struct {
		Name          string                             `toml:"name"`
		Species       string                             `toml:"species"`
		Gender        string                             `toml:"gender"`
		Background    string                             `toml:"background"`
		Classes       map[string]d20.Class               `toml:"classes"`
		AbilityScores map[string]attributes.AbilityScore `toml:"ability_score"`
		Skills        []string                           `toml:"skills"`
	}
}
