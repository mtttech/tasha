/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package utils

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
