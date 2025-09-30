/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"fmt"
	"maps"
	"os"
	"slices"
	"strconv"

	"tasha/actor"
	"tasha/attributes"
	"tasha/d20"
	"tasha/utils"

	"github.com/manifoldco/promptui"
	"github.com/spf13/cobra"
)

var currentVersion = "1.0.0"

var rootCmd = &cobra.Command{
	Use:   "tasha",
	Short: "Create 5.5e Dungeons & Dragons characters.",
	Long:  `Create 5.5e Dungeons & Dragons characters.`,
}

var newCmd = &cobra.Command{
	Use:   "new",
	Short: "Create a new character",
	Args:  cobra.ExactArgs(1),
	Run:   Tasha,
}

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Display the current version",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println(currentVersion)
	},
}

var Backgrounds = d20.GetD20Backgrounds()
var Genders = []string{"Female", "Male"}
var Species = d20.GetD20Species()

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func Tasha(cmd *cobra.Command, args []string) {
	// Select species
	species := MenuStr("Select your species", Species)

	// Select gender
	gender := MenuStr("Select your gender", Genders)

	// Select background
	background := MenuStr("Select your background", Backgrounds)

	// Assign ability scores
	ability_scores := AssignAbilityScores()

	// Assign classes, skills
	classes, skills := AssignCharacterClasses(background, ability_scores)

	pc := actor.PC{
		Name:          args[0],
		Species:       species,
		Gender:        gender,
		Background:    background,
		Classes:       classes,
		AbilityScores: ability_scores,
		Skills:        skills,
	}

	fmt.Println(pc.Name)
	fmt.Println(pc.Species)
	fmt.Println(pc.Gender)
	fmt.Println(pc.Background)
	fmt.Println(pc.Classes)
	fmt.Println(pc.AbilityScores)
	fmt.Println(pc.Skills)
}

func init() {
	rootCmd.AddCommand(newCmd)
	rootCmd.AddCommand(versionCmd)
}

/*
Assign ability scores.
*/
func AssignAbilityScores() map[string]attributes.AbilityScore {
	abilities := []string{
		"Strength",
		"Dexterity",
		"Constitution",
		"Intelligence",
		"Wisdom",
		"Charisma",
	}
	ability_score_map := make(map[string]attributes.AbilityScore)
	scores := attributes.GenerateScores()
	for _, ability := range abilities {
		score := MenuInt(fmt.Sprintf("Assign your %s score", ability), scores)
		ability_score_map[ability] = attributes.AbilityScore{
			Score:    score,
			Modifier: attributes.CalculateModifier(score),
		}
		scores = utils.OmitInt(scores, score)
	}

	return ability_score_map
}

/*
Assign character's classes and skills.
*/
func AssignCharacterClasses(background string, ability_scores map[string]attributes.AbilityScore) (map[string]actor.Class, []string) {
	var class string
	classes := make(map[string]actor.Class)
	single_class_options := d20.GetD20Classes()
	is_multiclassed := false
	max_level := 20
	multi_class_options := []string{}
	skills := []string{}

	// Populate multi_class_options variable, if applicable
	if len(multi_class_options) == 0 {
		multi_class_options = d20.GetValidMulticlassOptions(ability_scores)
	}

	for {
		// Select a class
		if !is_multiclassed {
			class = MenuStr("Select your class", single_class_options)
			single_class_options = utils.OmitStr(single_class_options, class)
		} else {
			class = MenuStr("Select your additional class", multi_class_options)
			multi_class_options = utils.OmitStr(multi_class_options, class)
		}

		// Set the class level
		level := MenuInt("What level are you", d20.GetLevelSlices(max_level))

		// Decrement level for the chosen class from max level
		max_level -= level

		// Apply subclass, if applicable
		subclass := ""
		if level >= 3 {
			subclass = MenuStr("What is your subclass", d20.GetSubclassesByClass(class))
		}

		classes[class] = actor.Class{
			Level:    level,
			Subclass: subclass,
		}

		// Assign class skills
		if !is_multiclassed {
			skills = AssignPrimaryClassSkills(class, d20.GetSkillsByBackground(background))
		} else {
			skills = AssignSecondaryClassSkills(class, skills)
		}

		// Clean up already selected classes for multiclassing
		for _, selected_class := range slices.Collect(maps.Keys(classes)) {
			multi_class_options = utils.OmitStr(multi_class_options, selected_class)
		}

		// Add secondary class, if applicable
		if len(multi_class_options) > 0 && max_level > 0 && ConfirmMenu(("Add another class")) {
			if !is_multiclassed {
				is_multiclassed = true
			}
			continue
		}

		break
	}

	return classes, skills
}

/*
Assign primary class skills.
*/
func AssignPrimaryClassSkills(class string, background_skills []string) []string {
	skills := background_skills
	class_skill_pool := d20.GetSkillsByClass(class)

	// Remove background skills from class skill pool, if applicable
	for _, background_skill := range background_skills {
		if slices.Contains(class_skill_pool, background_skill) {
			class_skill_pool = utils.OmitStr(class_skill_pool, background_skill)
		}
	}

	for i := 1; i <= d20.GetSkillPointsByClass(class, true); i++ {
		skill := MenuStr("Choose a class skill", class_skill_pool)
		skills = append(skills, skill)
		class_skill_pool = utils.OmitStr(class_skill_pool, skill)
	}

	return skills
}

/*
Assign secondary class skills.
*/
func AssignSecondaryClassSkills(class string, current_skills []string) []string {
	skills := current_skills
	class_skill_list := d20.GetSkillsByClass(class)

	// Remove skills already selected
	for _, current_skill := range current_skills {
		if slices.Contains(class_skill_list, current_skill) {
			class_skill_list = utils.OmitStr(class_skill_list, current_skill)
		}
	}

	// Start selecting class skills.
	for i := 1; i <= d20.GetSkillPointsByClass(class, false); i++ {
		skill := MenuStr("Choose a class skill", class_skill_list)
		skills = append(skills, skill)
		class_skill_list = utils.OmitStr(class_skill_list, skill)
	}

	return skills
}

/*
Confirm menu wrapper.
*/
func ConfirmMenu(label string) bool {
	prompt := promptui.Select{
		Label: label,
		Items: []string{"Yes", "No"},
	}
	_, selection, _ := prompt.Run()
	if selection == "Yes" {
		return true
	} else {
		return false
	}
}

/*
Select wrapper function with integers.
*/
func MenuInt(label string, items []int) int {
	prompt := promptui.Select{
		Label: label,
		Items: items,
	}
	_, selection, _ := prompt.Run()
	result, _ := strconv.Atoi(selection)
	return result
}

/*
Select wrapper function with strings.
*/
func MenuStr(label string, items []string) string {
	prompt := promptui.Select{
		Label: label,
		Items: items,
	}
	_, selection, _ := prompt.Run()
	return selection
}
