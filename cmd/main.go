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
)

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func Tasha(cmd *cobra.Command, args []string) {
	// Assign your species
	assignedSpecies := Menu("Select your species", d20.GetD20Species()).(string)
	assignedSize := d20.GetSizeBySpecies(assignedSpecies)
	assignedSpeed := d20.GetSpeedBySpecies(assignedSpecies)
	assignedTraits := d20.GetTraitsBySpecies(assignedSpecies)
	// Assign your gender
	assignedGender := Menu("Select your gender", []string{"Female", "Male"}).(string)
	// Assign your background
	assignedBackground := Menu("Select your background", d20.GetD20Backgrounds()).(string)
	assignedFeats := d20.GetFeatByBackground(assignedBackground)
	// Assign your ability scores
	assignedAbilityScores := AssignAbilityScores(assignedBackground)
	// Assign your class, features, proficiencies, and skills
	assignedClass, assignedFeatures, assignedArmors, assignedTools, assignedWeapons, assignedSkills := AssignCharacterClass(assignedBackground, assignedAbilityScores)
	// Collect data, save to toml file
	assignedName := strings.TrimSpace(args[0])
	var schema record.CharacterSheetTOMLSchema
	schema.PC.Name = assignedName
	schema.PC.Species = assignedSpecies
	schema.PC.Size = assignedSize
	schema.PC.Speed = assignedSpeed
	schema.PC.Traits = assignedTraits
	schema.PC.Gender = assignedGender
	schema.PC.Background = assignedBackground
	schema.PC.Abilities = assignedAbilityScores
	schema.PC.Class = assignedClass
	schema.PC.Level = d20.GetTotalLevel(assignedClass)
	schema.PC.Features = assignedFeatures
	schema.PC.Armors = assignedArmors
	schema.PC.Tools = assignedTools
	schema.PC.Weapons = assignedWeapons
	schema.PC.Skills = assignedSkills
	schema.PC.Feats = assignedFeats
	characterName := strings.ToLower(strings.Replace(assignedName, " ", "_", 1))
	if ConfirmMenu("Export this character") {
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
}

func init() {
	rootCmd.AddCommand(newCmd)
	rootCmd.AddCommand(versionCmd)
}

/*
Assign ability scores applying ability score bonuses by background b.
*/
func AssignAbilityScores(b string) map[string]abilities.AbilityScore {
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
	backgroundAbilities := d20.GetAssociatedAbilitiesByBackground(b)
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
Assign character's ability score bonuses.
*/
func AssignASIAbilityScoreBonus(s map[string]abilities.AbilityScore) map[string]abilities.AbilityScore {
	abilityOptions := []string{
		"Strength",
		"Dexterity",
		"Constitution",
		"Intelligence",
		"Wisdom",
		"Charisma",
	}
	asiBonus := Menu("Choose your bonus", []string{"2", "1"})
	bonusValue, _ := strconv.Atoi(asiBonus.(string))
	if bonusValue == 2 {
		ability := Menu(fmt.Sprintf("Which ability do you want to upgrade by +%d", bonusValue), abilityOptions).(string)
		newScore := s[ability].Score + bonusValue
		abilities.UpdateAbilityScore(s, ability, newScore)
		fmt.Printf("A +%d bonus was applied to your %s ability score.\n", bonusValue, ability)
	} else {
		for i := 1; i <= 2; i++ {
			ability := Menu(fmt.Sprintf("Which ability do you want to upgrade by +%d", bonusValue), abilityOptions).(string)
			abilityOptions = OmitNeedleFromHaystack(abilityOptions, ability)
			new_score := s[ability].Score + 1
			abilities.UpdateAbilityScore(s, ability, new_score)
			fmt.Printf("A +1 bonus was applied to your %s ability score.\n", ability)
		}
	}
	return s
}

/*
Assign upgrades based upon the instances of "Ability Score Improvement" in class features f.
*/
func AssignASIBonus(f []string, s map[string]abilities.AbilityScore) map[string]abilities.AbilityScore {
	for i := 1; i < d20.GetAllottedFeats(f); i++ {
		selection := Menu("Choose your bonus", []string{"Add Feat", "Upgrade Ability"})
		switch selection {
		case "Add Feat":
			fmt.Println("Add additional feat.")
		case "Upgrade Ability":
			fmt.Println("Upgrade ability score.")
			s = AssignASIAbilityScoreBonus(s)
		}
	}
	return s
}

/*
Assign PC's class using the specified background b and ability scores s.

Returns the following PC details:

	character class or classes
	class features
	armor proficiencies
	tool proficiencies
	weapon proficiencies
	skills
*/
func AssignCharacterClass(b string, s map[string]abilities.AbilityScore) (map[string]d20.Class, []string, []string, []string, []string, []string) {
	var assignedClass string
	assignedArmors := []string{}
	assignedClasses := make(map[string]d20.Class)
	assignedFeatures := []string{}
	assignedSkills := []string{}
	assignedWeapons := []string{}
	assignedTools := []string{}
	isMulticlassed := false
	maxLevel := 20
	multiClassOptions := []string{}
	singleClassOptions := d20.GetD20Classes()
	// Populate multiClassOptions, if applicable
	if len(multiClassOptions) == 0 {
		multiClassOptions = d20.GetValidMulticlassOptions(s)
	}
	// Select your class(es)
	for {
		if !isMulticlassed {
			assignedClass = Menu("Select your class", singleClassOptions).(string)
			singleClassOptions = OmitNeedleFromHaystack(singleClassOptions, assignedClass)
		} else {
			assignedClass = Menu("Select your additional class", multiClassOptions).(string)
			multiClassOptions = OmitNeedleFromHaystack(multiClassOptions, assignedClass)
		}
		// Set the class level
		assignedLevel := Menu("What level are you", d20.GetLevelSlices(maxLevel)).(int)
		// Decrement level for the chosen class from max level
		maxLevel -= assignedLevel
		// Apply subclass, if applicable
		assignedSubclass := ""
		if assignedLevel >= 3 {
			assignedSubclass = Menu("What is your subclass", d20.GetSubclassesByClass(assignedClass)).(string)
		}
		assignedClasses[assignedClass] = d20.Class{
			Level:    assignedLevel,
			Subclass: assignedSubclass,
		}
		// Assign armor profiencies
		assignedArmors = append(assignedArmors, d20.GetArmorsByClass(assignedClass)...)
		// Assign your class features
		assignedFeatures = append(assignedFeatures, d20.GetFeaturesByClass(assignedClass, assignedLevel)...)
		// Assign weapon profiencies
		assignedWeapons = append(assignedWeapons, d20.GetWeaponsByClass(assignedClass)...)
		// Assign your class skills, tool proficiencies
		if !isMulticlassed {
			assignedSkills = AssignClassSkills(assignedClass, d20.GetSkillsByBackground(b), true)
			assignedTools = append(assignedTools, AssignToolProficiencies(assignedClass, d20.GetToolsByClass(assignedClass), true)...)
		} else {
			assignedSkills = AssignClassSkills(assignedClass, assignedSkills, false)
			assignedTools = append(assignedTools, AssignToolProficiencies(assignedClass, d20.GetToolsByClass(assignedClass), false)...)
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
	return assignedClasses, assignedFeatures, assignedArmors, assignedTools, assignedWeapons, assignedSkills
}

/*
Assign PC class skills by class c, exluding possessed skills s.
*/
func AssignClassSkills(c string, s []string, p bool) []string {
	assignedSkills := s
	classSkillList := d20.GetSkillsByClass(c)
	// Remove skills that are already known to the player.
	for _, omitted_skill := range s {
		if slices.Contains(classSkillList, omitted_skill) {
			classSkillList = OmitNeedleFromHaystack(classSkillList, omitted_skill)
			fmt.Printf("The skill %s was omitted.", omitted_skill)
		}
	}
	// Select class skills from a list of applicable skills.
	for i := 1; i <= d20.GetSkillPointsByClass(c, p); i++ {
		skill := Menu("Choose a class skill", classSkillList).(string)
		assignedSkills = append(assignedSkills, skill)
		classSkillList = OmitNeedleFromHaystack(classSkillList, skill)
	}
	slices.Sort(assignedSkills)
	return assignedSkills
}

/*
Assign tool proficiencies by class c assigning tool proficiencies t.
*/
func AssignToolProficiencies(c string, t []string, p bool) []string {
	switch c {
	case "Bard":
		var num_of_bonuses int
		if p {
			num_of_bonuses = 3
		} else {
			num_of_bonuses = 1
		}
		tt := []string{}
		for i := 1; i <= num_of_bonuses; i++ {
			proficiency := Menu("Choose a bonus Musical Instrument", t)
			tt = append(tt, proficiency.(string))
			if num_of_bonuses == 3 {
				t = OmitNeedleFromHaystack(t, proficiency.(string))
			}
		}
		t = tt
	case "Monk":
		if p {
			proficiency := Menu("Choose a bonus Artisan Tool or Musical Instrument", t)
			t = []string{proficiency.(string)}
		}
	}
	slices.Sort(t)
	return t
}

/*
Confirm menu wrapper.
*/
func ConfirmMenu(l string) bool {
	prompt := promptui.Select{
		Label: l,
		Items: []string{"Yes", "No"},
	}
	_, selection, _ := prompt.Run()
	switch selection {
	case "Yes":
		return true
	default:
		return false
	}
}

/*
Select wrapper function which accepts slices of strings or intergers.
*/
func Menu[T comparable](l string, o []T) any {
	prompt := promptui.Select{
		Label: l,
		Items: o,
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
Returns the given haystack h minus the first instance of needle n.
*/
func OmitNeedleFromHaystack[T comparable](h []T, n T) []T {
	needleFound := false
	updatedHaystack := []T{}
	for _, obj := range h {
		if !needleFound && n == obj {
			needleFound = true
		} else {
			updatedHaystack = append(updatedHaystack, obj)
		}
	}
	return updatedHaystack
}
