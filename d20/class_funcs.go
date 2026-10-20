/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import (
	"maps"
	"slices"
)

/*
Returns a slice of armor proficiencies by class.
*/
func GetArmorsByClass(c string) []string {
	return characterClasses[c].Armors
}

/*
Returns a slice of DnD classes.
*/
func GetD20Classes() []string {
	classes := slices.Collect(maps.Keys(characterClasses))
	slices.Sort(classes)
	return classes
}

/*
Returns a slice of class features by class c and level l.
*/
func GetFeaturesByClass(c string, l int) []string {
	class_features := []string{}
	for level, features := range characterClasses[c].Features {
		if l >= level {
			class_features = append(class_features, features...)
		}
	}
	slices.Sort(class_features)
	return class_features
}

/*
Returns hit die by class c.
*/
func GetHitDieByClass(c string) int {
	return characterClasses[c].HitDie
}

/*
Returns level slices m from 1 to max.
*/
func GetLevelSlices(m int) []int {
	var levels []int
	for i := 1; i <= m; i++ {
		levels = append(levels, i)
	}
	return levels
}

/*
Returns a slice of saving throws by class c.
*/
func GetSavingThrowsByClass(c string) []string {
	return characterClasses[c].Subclasses
}

/*
Gets the number of skill points by class c and if primary or secondary class p.
*/
func GetSkillPointsByClass(c string, p bool) int {
	allotted_skills := 0
	switch c {
	case "Rogue":
		allotted_skills = 4
	case "Bard", "Ranger":
		if p {
			allotted_skills = 3
		} else {
			allotted_skills = 1
		}
	default:
		if p {
			allotted_skills = 2
		}
	}
	return allotted_skills
}

/*
Returns a slice of subclasses by class c.
*/
func GetSubclassesByClass(c string) []string {
	return characterClasses[c].Subclasses
}

/*
Returns a slice of tool proficiencies by class c.
*/
func GetToolsByClass(c string) []string {
	return characterClasses[c].Tools
}

/*
Returns a slice of tool proficiencies by class c.
*/
func GetTotalLevel(c map[string]Class) int {
	totalLevel := 0
	for _, class := range c {
		totalLevel += class.Level
	}
	return totalLevel
}

/*
Returns a slice of weapon proficiencies by class c.
*/
func GetWeaponsByClass(c string) []string {
	return characterClasses[c].Weapons
}
