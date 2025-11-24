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
		Name       string                            `toml:"name"`
		Species    string                            `toml:"species"`
		Size       string                            `toml:"size"`
		Speed      int                               `toml:"speed"`
		Traits     []string                          `toml:"traits"`
		Gender     string                            `toml:"gender"`
		Abilities  map[string]abilities.AbilityScore `toml:"abilities"`
		Background string                            `toml:"background"`
		Class      map[string]d20.Class              `toml:"class"`
		Level      int                               `toml:"level"`
		Armors     []string                          `toml:"armors"`
		Features   []string                          `toml:"features"`
		Weapons    []string                          `toml:"weapons"`
		Skills     []string                          `toml:"skills"`
		Feats      []string                          `toml:"feats"`
	}
}
