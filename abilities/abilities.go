/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package abilities

import (
	"math/rand"
	"slices"
)

type AbilityScore struct {
	Score    int
	Modifier int
}

/*
Drops the lowest value, then adds the remaining three values.
*/
func add_three() int {
	isSmallestIntFound := false
	rollFourResults := roll_four()
	smallestInt := slices.Min(rollFourResults)
	totalValue := 0
	for _, n := range rollFourResults {
		if n == smallestInt && !isSmallestIntFound {
			isSmallestIntFound = true
			continue
		}
		totalValue += n
	}
	return totalValue
}

/*
Returns four numbers between 1 and 6.
*/
func roll_four() []int {
	var rolledValues []int
	for i := 1; i < 5; i++ {
		rolledValues = append(rolledValues, rand.Intn(6)+1)
	}
	return rolledValues
}

/*
Returns six results of add_three().
*/
func roll_six() []int {
	var rolledValues []int
	for i := 1; i < 7; i++ {
		rolledValues = append(rolledValues, add_three())
	}
	return rolledValues
}

/*
Calculates modifier value for the specified score.

Formula: score - 10 / 2
*/
func CalculateModifier(score int) int {
	return (score - 10) / 2
}

/*
Generates six random attributes.

Will automatically reroll the results if one of the following is true:

 1. If the smallest attribute < 8
 2. If the largest attribute < 15
*/
func GenerateScores() []int {
	var generatedScores []int
	for {
		generatedScores = roll_six()
		if slices.Min(generatedScores) >= 8 && slices.Max(generatedScores) >= 15 {
			break
		}
	}
	slices.Sort(generatedScores)
	slices.Reverse(generatedScores)
	return generatedScores
}

/*
Updates ability score/modifier in the specified map.
*/
func UpdateAbilityScore(ability_score_map map[string]AbilityScore, ability string, new_score int) {
	ability_score_map[ability] = AbilityScore{
		Score:    new_score,
		Modifier: CalculateModifier(new_score),
	}
}
