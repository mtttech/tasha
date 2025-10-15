/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package utils

/*
Returns the given items minus the first instance of needle.
*/
func OmitItem[T comparable](items []T, needle T) []T {
	newSlice := []T{}
	needleFound := false
	for _, item := range items {
		if !needleFound && needle == item {
			needleFound = true
		} else {
			newSlice = append(newSlice, item)
		}
	}
	return newSlice
}
