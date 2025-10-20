/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import "slices"

type Skills struct {
	Ability string
	Classes []string
}

var characterSkills = map[string]Skills{
	"Acrobatics": {
		Ability: "Dexterity",
		Classes: []string{"Bard", "Fighter", "Monk", "Rogue"},
	},
	"Animal Handling": {
		Ability: "Wisdom",
		Classes: []string{"Barbarian", "Bard", "Druid", "Fighter", "Ranger"},
	},
	"Arcana": {
		Ability: "Intelligence",
		Classes: []string{"Bard", "Druid", "Sorcerer", "Warlock", "Wizard"},
	},
	"Athletics": {
		Ability: "Strength",
		Classes: []string{"Barbarian", "Bard", "Fighter", "Paladin", "Ranger", "Rogue"},
	},
	"Deception": {
		Ability: "Charisma",
		Classes: []string{"Bard", "Rogue", "Sorcerer", "Warlock"},
	},
	"History": {
		Ability: "Intelligence",
		Classes: []string{"Bard", "Cleric", "Fighter", "Monk", "Warlock", "Wizard"},
	},
	"Insight": {
		Ability: "Wisdom",
		Classes: []string{"Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Wizard"},
	},
	"Intimidation": {
		Ability: "Charisma",
		Classes: []string{"Barbarian", "Bard", "Fighter", "Paladin", "Rogue", "Sorcerer", "Warlock"},
	},
	"Investigation": {
		Ability: "Intelligence",
		Classes: []string{"Bard", "Ranger", "Rogue", "Warlock", "Wizard"},
	},
	"Medicine": {
		Ability: "Wisdom",
		Classes: []string{"Bard", "Cleric", "Druid", "Paladin", "Wizard"},
	},
	"Nature": {
		Ability: "Wisdom",
		Classes: []string{"Barbarian", "Bard", "Druid", "Ranger", "Warlock"},
	},
	"Perception": {
		Ability: "Wisdom",
		Classes: []string{"Barbarian", "Bard", "Druid", "Fighter", "Ranger", "Rogue"},
	},
	"Performance": {
		Ability: "Charisma",
		Classes: []string{"Bard", "Rogue"},
	},
	"Persuasion": {
		Ability: "Charisma",
		Classes: []string{"Bard", "Cleric", "Paladin", "Rogue", "Sorcerer"},
	},
	"Religion": {
		Ability: "Intelligence",
		Classes: []string{"Bard", "Cleric", "Druid", "Monk", "Paladin", "Sorcerer", "Warlock", "Wizard"},
	},
	"Sleight of Hand": {
		Ability: "Dexterity",
		Classes: []string{"Bard", "Ranger", "Rogue"},
	},
	"Stealth": {
		Ability: "Dexterity",
		Classes: []string{"Bard", "Monk", "Ranger", "Rogue"},
	},
}

/*
Returns a slice of skills by class.
*/
func GetSkillsForClass(class string) []string {
	class_skills := []string{}
	for skill := range characterSkills {
		if slices.Contains(characterSkills[skill].Classes, class) {
			class_skills = append(class_skills, skill)
		}
	}

	slices.Sort(class_skills)
	return class_skills
}
