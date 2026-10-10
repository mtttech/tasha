/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"os"
	"strings"

	"tasha/abilities"
	"tasha/d20"

	"github.com/spf13/cobra"
)

type PC struct {
	Name             string                            `json:"name"`
	Species          string                            `json:"species"`
	Size             string                            `json:"size"`
	Speed            int                               `json:"speed"`
	Traits           []string                          `json:"traits"`
	Gender           string                            `json:"gender"`
	AbilityScores    map[string]abilities.AbilityScore `json:"ability_scores"`
	Background       string                            `json:"background"`
	Class            map[string]d20.Class              `json:"class"`
	Level            int                               `json:"level"`
	ProficiencyBonus int                               `json:"proficiency_bonus"`
	Armors           []string                          `json:"armors"`
	Tools            []string                          `json:"tools"`
	Weapons          []string                          `json:"weapons"`
	Features         []string                          `json:"features"`
	Skills           []string                          `json:"skills"`
	Feats            []string                          `json:"feats"`
}

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
		var pc PC
		pc.Name = assignedName
		pc.Species = assignedSpecies
		pc.Size = assignedSize
		pc.Speed = assignedSpeed
		pc.Traits = assignedTraits
		pc.Gender = assignedGender
		pc.Background = assignedBackground
		pc.AbilityScores = assignedAbilityScores
		pc.Class = assignedClass
		pc.Level = d20.GetTotalLevel(assignedClass)
		pc.ProficiencyBonus = int(math.Ceil(float64(pc.Level) / float64(4)))
		pc.Features = assignedFeatures
		pc.Armors = assignedArmors
		pc.Tools = assignedTools
		pc.Weapons = assignedWeapons
		pc.Skills = assignedSkills
		pc.Feats = assignedFeats
		// Confirm, save to toml file
		if ConfirmMenu("Export this character") {
			csFileName := fmt.Sprintf("%s.json", strings.ToLower(strings.ReplaceAll(assignedName, " ", "_")))
			fp, err := os.Create(csFileName)
			if err != nil {
				log.Fatalf("Failed to create character sheet: %v", err)
			}
			defer fp.Close()

			encoder := json.NewEncoder(fp)
			encoder.SetIndent("", "		")

			if err := encoder.Encode(pc); err != nil {
				log.Fatalf("Failed to encode toml data: %v", err)
			}
		}
	},
}

func init() {
	cmdRoot.AddCommand(cmdCreate)
}
