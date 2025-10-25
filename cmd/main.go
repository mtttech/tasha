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
	curVersion = "1.0.0"

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
			fmt.Println(curVersion)
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
	// Select assignedSpecies
	assignedSpecies := Menu("Select your species", Species).(string)
	// Select assignedGender
	assignedGender := Menu("Select your gender", Genders).(string)
	// Select assignedBackground
	assignedBackground := Menu("Select your background", Backgrounds).(string)
	// Assign ability scores
	assignedAbilityScores := AssignAbilityScores(assignedBackground)
	// Assign assignedClass, assignedSkills
	assignedClass, assignedSkills := AssignCharacterClass(assignedBackground, assignedAbilityScores)
	// Collect data, save to toml file
	assignedName := strings.TrimSpace(args[0])
	var schema record.CharacterSheetTOMLSchema
	schema.PC.Name = assignedName
	schema.PC.Species = assignedSpecies
	schema.PC.Gender = assignedGender
	schema.PC.Background = assignedBackground
	schema.PC.Class = assignedClass
	schema.PC.AbilityScores = assignedAbilityScores
	schema.PC.Skills = assignedSkills
	characterName := strings.ToLower(strings.Replace(assignedName, " ", "_", 1))
	fp, err := os.Create(fmt.Sprintf("%s.toml", characterName))
	if err != nil {
		panic(err)
	}
	defer fp.Close()
	err = toml.NewEncoder(fp).Encode(schema)
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
	abilityOptions := []string{
		"Strength",
		"Dexterity",
		"Constitution",
		"Intelligence",
		"Wisdom",
		"Charisma",
	}
	abilityScoreMap := make(map[string]abilities.AbilityScore)
	generatedScores := abilities.GenerateScores()
	for _, ability := range abilityOptions {
		score := Menu(fmt.Sprintf("Assign your %s score", ability), generatedScores).(int)
		generatedScores = OmitNeedleFromHaystack(generatedScores, score)
		abilities.UpdateAbilityScore(abilityScoreMap, ability, score)
	}
	// Apply background ability bonuses
	backgroundBonus := Menu("Choose your background bonus array", []string{"2/1", "1/1/1"})
	backgroundAbilities := d20.GetAbilitiesByBackground(background)
	if backgroundBonus == "2/1" {
		bonusValue := 2
		for i := 1; i <= 2; i++ {
			ability := Menu(fmt.Sprintf("Choose your bonus ability +%d", bonusValue), backgroundAbilities).(string)
			backgroundAbilities = OmitNeedleFromHaystack(backgroundAbilities, ability)
			newScore := abilityScoreMap[ability].Score + bonusValue
			abilities.UpdateAbilityScore(abilityScoreMap, ability, newScore)
			fmt.Printf("A +%d bonus was applied to your %s ability score.\n", bonusValue, ability)
			bonusValue -= 1
		}
	} else {
		for _, ability := range backgroundAbilities {
			new_score := abilityScoreMap[ability].Score + 1
			abilities.UpdateAbilityScore(abilityScoreMap, ability, new_score)
			fmt.Printf("A +1 bonus was applied to your %s ability score.\n", ability)
		}
	}
	return abilityScoreMap
}

/*
Assign character's classes and skills.
*/
func AssignCharacterClass(background string, ability_scores map[string]abilities.AbilityScore) (map[string]d20.Class, []string) {
	var assignedClass string
	assignedClasses := make(map[string]d20.Class)
	assignedSkills := []string{}
	isMulticlassed := false
	maxLevel := 20
	multiClassOptions := []string{}
	singleClassOptions := d20.GetD20Classes()
	// Populate multi_class_options variable, if applicable
	if len(multiClassOptions) == 0 {
		multiClassOptions = d20.GetValidMulticlassOptions(ability_scores)
	}
	for {
		// Select a class
		if !isMulticlassed {
			assignedClass = Menu("Select your class", singleClassOptions).(string)
			singleClassOptions = OmitNeedleFromHaystack(singleClassOptions, assignedClass)
		} else {
			assignedClass = Menu("Select your additional class", multiClassOptions).(string)
			multiClassOptions = OmitNeedleFromHaystack(multiClassOptions, assignedClass)
		}
		// Set the class assignedLevel
		assignedLevel := Menu("What level are you", d20.GetLevelSlices(maxLevel)).(int)
		// Decrement level for the chosen class from max level
		maxLevel -= assignedLevel
		// Apply the assigned subclass, if applicable
		assignedSubclass := ""
		if assignedLevel >= 3 {
			assignedSubclass = Menu("What is your subclass", d20.GetSubclassesByClass(assignedClass)).(string)
		}
		assignedClasses[assignedClass] = d20.Class{
			Level:    assignedLevel,
			Subclass: assignedSubclass,
		}
		// Assign your class skills
		if !isMulticlassed {
			assignedSkills = AssignClassSkills(assignedClass, d20.GetSkillsByBackground(background), true)
		} else {
			assignedSkills = AssignClassSkills(assignedClass, assignedSkills, false)
		}
		// Clean up selected classes for multiclassing
		for _, selected_class := range slices.Collect(maps.Keys(assignedClasses)) {
			multiClassOptions = OmitNeedleFromHaystack(multiClassOptions, selected_class)
		}
		// Add secondary class, if applicable
		if len(multiClassOptions) > 0 && maxLevel > 0 && ConfirmMenu(("Add another class")) {
			if !isMulticlassed {
				isMulticlassed = true
			}
			continue
		}
		break
	}
	return assignedClasses, assignedSkills
}

/*
Assign class skills.
*/
func AssignClassSkills(class string, omitted_skills []string, is_primary_class bool) []string {
	assignedSkills := omitted_skills
	classSkillList := d20.GetSkillsByClass(class)
	// Remove omitted skills.
	for _, omitted_skill := range omitted_skills {
		if slices.Contains(classSkillList, omitted_skill) {
			classSkillList = OmitNeedleFromHaystack(classSkillList, omitted_skill)
			fmt.Printf("The skill %s was omitted.", omitted_skill)
		}
	}
	// Select class skills.
	for i := 1; i <= d20.GetSkillPointsByClass(class, is_primary_class); i++ {
		skill := Menu("Choose a class skill", classSkillList).(string)
		assignedSkills = append(assignedSkills, skill)
		classSkillList = OmitNeedleFromHaystack(classSkillList, skill)
	}
	slices.Sort(assignedSkills)
	return assignedSkills
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
Select wrapper function which accepts slices of strings or intergers.
*/
func Menu[T comparable](label string, options []T) any {
	prompt := promptui.Select{
		Label: label,
		Items: options,
	}
	_, selection, _ := prompt.Run()
	result, err := strconv.Atoi(selection)
	if err == nil {
		return result
	} else {
		return selection
	}
}

/*
Returns the given haystack minus the first instance of needle.
*/
func OmitNeedleFromHaystack[T comparable](haystack []T, needle T) []T {
	needleFound := false
	updatedHaystack := []T{}
	for _, obj := range haystack {
		if !needleFound && needle == obj {
			needleFound = true
		} else {
			updatedHaystack = append(updatedHaystack, obj)
		}
	}
	return updatedHaystack
}
