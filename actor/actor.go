/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package actor

import (
	"maps"
	"slices"

	"tasha/attributes"
	"tasha/d20"
)

type PlayerCharacter struct {
	Name          string
	Species       string
	Gender        string
	Background    string
	Classes       map[string]d20.Class
	AbilityScores map[string]attributes.AbilityScore
	Skills        []string
}

func (p *PlayerCharacter) GetClasses() []string {
	return slices.Collect(maps.Keys(p.Classes))
}

func (p *PlayerCharacter) GetGender() string {
	return p.Gender
}

func (p *PlayerCharacter) GetName() string {
	return p.Name
}

func (p *PlayerCharacter) GetSpecies() string {
	return p.Species
}
