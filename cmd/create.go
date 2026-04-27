/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"fmt"
	"log"
	"os"
	"strings"

	"tasha/d20"
	"tasha/record"

	"github.com/BurntSushi/toml"
	"github.com/spf13/cobra"
)

var cmdCreate = &cobra.Command{
	Use:   "create",
	Short: "Create a new character",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
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
		// Collect character data
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
		// Confirm, save to toml file
		if ConfirmMenu("Export this character") {
			characterName := strings.ToLower(strings.ReplaceAll(assignedName, " ", "_"))
			fp, err := os.Create(fmt.Sprintf("%s.toml", characterName))
			if err != nil {
				log.Fatalf("Failed to create character sheet: %v", err)
			}
			defer fp.Close()
			if err := toml.NewEncoder(fp).Encode(schema); err != nil {
				log.Fatalf("Failed to encode toml data: %v", err)
			}
		}
	},
}

func init() {
	cmdRoot.AddCommand(cmdCreate)
}
