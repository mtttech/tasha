/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package utils

/*
Returns the largest int within a sequence.
*/
func Max(seq []int) int {
	largest_integer := seq[0]
	for _, n := range seq {
		if n >= largest_integer {
			largest_integer = n
		}
	}
	return largest_integer
}

/*
Returns the smallest int within a sequence.
*/
func Min(seq []int) int {
	smallest_integer := seq[0]
	for _, n := range seq {
		if n <= smallest_integer {
			smallest_integer = n
		}
	}
	return smallest_integer
}

/*
Returns the given items sequence minus the first instance of needle.
*/
func OmitInt(items []int, needle int) []int {
	newIntArray := []int{}
	needleFound := false
	for _, item := range items {
		if !needleFound && needle == item {
			needleFound = true
		} else {
			newIntArray = append(newIntArray, item)
		}
	}
	return newIntArray
}

/*
Returns the given items sequence minus the instance of needle.
*/
func OmitStr(items []string, needle string) []string {
	newStrArray := []string{}
	for _, item := range items {
		if needle != item {
			newStrArray = append(newStrArray, item)
		}
	}
	return newStrArray
}
