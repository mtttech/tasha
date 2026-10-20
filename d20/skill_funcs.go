/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package d20

import "slices"

/*
Returns skills by class c.
*/
func GetSkillsByClass(c string) []string {
	classSkills := []string{}
	for skill := range characterSkills {
		if slices.Contains(characterSkills[skill].Classes, c) {
			classSkills = append(classSkills, skill)
		}
	}

	slices.Sort(classSkills)
	return classSkills
}
