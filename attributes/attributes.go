/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package attributes

import (
	"math/rand"
	"slices"

	"tasha/utils"
)

type AbilityScore struct {
	Score    int
	Modifier int
}

/*
Drops the lowest value, then adds the remaining three values.
*/
func add_three() int {
	results := roll_four()
	smallest_int := utils.Min(results)
	smallest_int_found := false
	total := 0
	for _, n := range results {
		if n == smallest_int && !smallest_int_found {
			smallest_int_found = true
			continue
		}
		total += n
	}
	return total
}

/*
Returns four numbers between 1 and 6.
*/
func roll_four() []int {
	var rolls []int
	for i := 1; i < 5; i++ {
		rolls = append(rolls, rand.Intn(6)+1)
	}
	return rolls
}

/*
Returns six results of add_three().
*/
func roll_six() []int {
	var results []int
	for i := 1; i < 7; i++ {
		results = append(results, add_three())
	}
	return results
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
	var dice_rolls []int
	for {
		dice_rolls = roll_six()
		if utils.Min(dice_rolls) >= 8 && utils.Max(dice_rolls) >= 15 {
			break
		}
	}
	slices.Sort(dice_rolls)
	slices.Reverse(dice_rolls)
	return dice_rolls
}
