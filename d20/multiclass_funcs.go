/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"

	"tasha/abilities"
)

/*
Checks if character can multiclass to the class c with the ability scores s.
*/
func can_multiclass_to_class(c string, s map[string]abilities.AbilityScore) bool {
	abilities := characterMulticlasses[c].Ability
	switch c {
	case "Fighter":
		if s["Strength"].Score >= 13 || s["Dexterity"].Score >= 13 {
			return true
		}
	case "Monk", "Paladin", "Ranger":
		if s[abilities[0]].Score >= 13 && s[abilities[1]].Score >= 13 {
			return true
		}
	default:
		if s[abilities[0]].Score >= 13 {
			return true
		}
	}

	return false
}

/*
Returns multiclass options by met ability score requirements s.
*/
func GetValidMulticlassOptions(s map[string]abilities.AbilityScore) []string {
	valid_class_options := []string{}
	classes := slices.Collect(maps.Keys(characterMulticlasses))
	slices.Sort(classes)
	for _, new_class := range classes {
		if can_multiclass_to_class(new_class, s) {
			valid_class_options = append(valid_class_options, new_class)
		}
	}

	return valid_class_options
}
