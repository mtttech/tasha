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
	"strings"

	"tasha/abilities"
	"tasha/d20"
	"tasha/record"

	"github.com/BurntSushi/toml"
	"github.com/manifoldco/promptui"
	"github.com/spf13/cobra"
)

var (
	Version = "1.0.0"
	rootCmd = &cobra.Command{
		Use:   "tasha",
		Short: "Create 5.5e Dungeons & Dragons characters.",
		Long:  `Create 5.5e Dungeons & Dragons characters.`,
	}

	newCmd = &cobra.Command{
		Use:   "new",
		Short: "Create a new character",
		Args:  cobra.ExactArgs(1),
		Run:   Tasha,
	}

	versionCmd = &cobra.Command{
		Use:   "version",
		Short: "Display the current version",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println(Version)
		},
	}

	Backgrounds = d20.GetD20Backgrounds()
	Genders     = []string{"Female", "Male"}
	Species     = d20.GetD20Species()
)

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
	ability_scores := AssignAbilityScores(background)

	// Assign classes, skills
	classes, skills := AssignCharacterClasses(background, ability_scores)

	// Collect data, save to toml file
	name := strings.TrimSpace(args[0])

	var schema record.CharacterSheetTOMLSchema
	schema.PC.Name = name
	schema.PC.Species = species
	schema.PC.Gender = gender
	schema.PC.Background = background
	schema.PC.Classes = classes
	schema.PC.AbilityScores = ability_scores
	schema.PC.Skills = skills

	cs_filename := strings.ToLower(strings.Replace(name, " ", "_", 1))
	f, err := os.Create(fmt.Sprintf("%s.toml", cs_filename))
	if err != nil {
		panic(err)
	}
	defer f.Close()

	err = toml.NewEncoder(f).Encode(schema)
	if err != nil {
		panic(err)
	}
}

func init() {
	rootCmd.AddCommand(newCmd)
	rootCmd.AddCommand(versionCmd)
}

/*
Assign ability scores.
*/
func AssignAbilityScores(background string) map[string]abilities.AbilityScore {
	ability_options := []string{
		"Strength",
		"Dexterity",
		"Constitution",
		"Intelligence",
		"Wisdom",
		"Charisma",
	}
	ability_score_map := make(map[string]abilities.AbilityScore)
	scores := abilities.GenerateScores()
	for _, ability := range ability_options {
		score := MenuInt(fmt.Sprintf("Assign your %s score", ability), scores)
		scores = OmitItemFromHaystack(scores, score)
		abilities.UpdateAbilityScore(ability_score_map, ability, score)
	}

	// Apply background ability bonuses
	background_bonus := MenuStr("Choose your background bonus array", []string{"2/1", "1/1/1"})
	background_abilities := d20.GetAbilitiesByBackground(background)
	if background_bonus == "2/1" {
		bonus_value := 2
		for i := 1; i <= 2; i++ {
			ability := MenuStr(fmt.Sprintf("Choose your bonus ability +%d", bonus_value), background_abilities)
			background_abilities = OmitItemFromHaystack(background_abilities, ability)
			new_score := ability_score_map[ability].Score + bonus_value
			abilities.UpdateAbilityScore(ability_score_map, ability, new_score)
			fmt.Printf("A +%d bonus was applied to your %s ability score.\n", bonus_value, ability)
			bonus_value -= 1
		}
	} else {
		for _, ability := range background_abilities {
			new_score := ability_score_map[ability].Score + 1
			abilities.UpdateAbilityScore(ability_score_map, ability, new_score)
			fmt.Printf("A +1 bonus was applied to your %s ability score.\n", ability)
		}
	}

	return ability_score_map
}

/*
Assign character's classes and skills.
*/
func AssignCharacterClasses(background string, ability_scores map[string]abilities.AbilityScore) (map[string]d20.Class, []string) {
	var class string
	classes := make(map[string]d20.Class)
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
			single_class_options = OmitItemFromHaystack(single_class_options, class)
		} else {
			class = MenuStr("Select your additional class", multi_class_options)
			multi_class_options = OmitItemFromHaystack(multi_class_options, class)
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

		classes[class] = d20.Class{
			Level:    level,
			Subclass: subclass,
		}

		// Assign class skills
		if !is_multiclassed {
			skills = AssignClassSkills(class, d20.GetSkillsByBackground(background), true)
		} else {
			skills = AssignClassSkills(class, skills, false)
		}

		// Clean up already selected classes for multiclassing
		for _, selected_class := range slices.Collect(maps.Keys(classes)) {
			multi_class_options = OmitItemFromHaystack(multi_class_options, selected_class)
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
Assign class skills.
*/
func AssignClassSkills(class string, omitted_skills []string, is_primary_class bool) []string {
	skills := omitted_skills
	class_skill_list := d20.GetSkillsByClass(class)

	// Remove omitted skills.
	for _, omitted_skill := range omitted_skills {
		if slices.Contains(class_skill_list, omitted_skill) {
			class_skill_list = OmitItemFromHaystack(class_skill_list, omitted_skill)
			fmt.Printf("The skill %s was omitted.", omitted_skill)
		}
	}

	// Select class skills.
	for i := 1; i <= d20.GetSkillPointsByClass(class, is_primary_class); i++ {
		skill := MenuStr("Choose a class skill", class_skill_list)
		skills = append(skills, skill)
		class_skill_list = OmitItemFromHaystack(class_skill_list, skill)
	}

	slices.Sort(skills)
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

/*
Returns the given haystack minus the first instance of needle.
*/
func OmitItemFromHaystack[T comparable](haystack []T, needle T) []T {
	updated_haystack := []T{}
	needleFound := false
	for _, item := range haystack {
		if !needleFound && needle == item {
			needleFound = true
		} else {
			updated_haystack = append(updated_haystack, item)
		}
	}
	return updated_haystack
}
