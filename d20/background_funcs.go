/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

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
