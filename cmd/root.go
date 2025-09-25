/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"fmt"
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
	Short: "Create a new character.",
	Args:  cobra.ExactArgs(1),
	Run:   Tasha,
}

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Display the current version.",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println(currentVersion)
	},
}

var Backgrounds = d20.GetD20Backgrounds()
var Classes = d20.GetD20Classes()
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
	classes, skills := AssignCharacterClasses(background)

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
	Abilities := []string{
		"Strength",
		"Dexterity",
		"Constitution",
		"Intelligence",
		"Wisdom",
		"Charisma",
	}
	var ability_scores = make(map[string]attributes.AbilityScore)
	abilityScores := attributes.GenerateScores()
	for _, attribute := range Abilities {
		score := MenuInt(fmt.Sprintf("Assign your %s score", attribute), abilityScores)
		ability_scores[attribute] = attributes.AbilityScore{
			Score:    score,
			Modifier: attributes.CalculateModifier(score),
		}
		abilityScores = utils.OmitInt(abilityScores, score)
	}

	return ability_scores
}

/*
Assign character classes skills.
*/
func AssignCharacterClasses(background string) (map[string]actor.Class, []string) {
	var classes = make(map[string]actor.Class)
	var is_multiclassed = false
	var max_level = 20
	var skills = []string{}

	for {
		class := MenuStr("Select your class", Classes)
		Classes = utils.OmitStr(Classes, class)
		level := MenuInt("What level are you", d20.GetLevelSlices(max_level))
		// Decrement level for chosen class from max level.
		max_level -= level
		classes[class] = actor.Class{
			Level:    level,
			Subclass: "",
		}

		if !is_multiclassed {
			skills = AssignPrimaryClassSkills(class, d20.GetSkillsByBackground(background))
		} else {
			skills = AssignSecondaryClassSkills(class, skills)
		}

		if max_level > 0 && ConfirmMenu(("Add another class")) {
			if !is_multiclassed {
				is_multiclassed = true
			}
		} else {
			break
		}
	}

	return classes, skills
}

/*
Assign primary class skills.
*/
func AssignPrimaryClassSkills(class string, background_skills []string) []string {
	var skills = []string{}
	classSkills := d20.GetSkillsByClass(class)
	// Cycle through background skills.
	for _, background_skill := range background_skills {
		if slices.Contains(classSkills, background_skill) {
			// Apply background skill to the chosen skill pool.
			skills = append(skills, background_skill)
			// Remove background skill from the list of selectable class skills.
			classSkills = utils.OmitStr(classSkills, background_skill)
			fmt.Printf("Background skill '%s' added.\n", background_skill)
		}
	}

	// Start selecting class skills.
	for i := 1; i <= d20.GetSkillPointsByClass(class, true); i++ {
		skill := MenuStr("Choose a class skill", classSkills)
		skills = append(skills, skill)
		classSkills = utils.OmitStr(classSkills, skill)
	}

	return skills
}

/*
Assign secondary class skills.
*/
func AssignSecondaryClassSkills(class string, current_skills []string) []string {
	var skills = []string{}
	classSkills := d20.GetSkillsByClass(class)
	// Cycle through current skills.
	for _, current_skill := range current_skills {
		if slices.Contains(classSkills, current_skill) {
			// Apply current skill to the chosen skill pool.
			skills = append(skills, current_skill)
			// Remove skills the character already possesses.
			classSkills = utils.OmitStr(classSkills, current_skill)
		}
	}

	// Start selecting class skills.
	for i := 1; i <= d20.GetSkillPointsByClass(class, true); i++ {
		skill := MenuStr("Choose a class skill", classSkills)
		skills = append(skills, skill)
		classSkills = utils.OmitStr(classSkills, skill)
	}

	return skills
}

/*
Select wrapper function with strings.
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
