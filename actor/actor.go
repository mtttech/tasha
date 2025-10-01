/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package actor

import (
	"tasha/attributes"
	"tasha/classes"
)

type PC struct {
	Name          string
	Species       string
	Gender        string
	Background    string
	Classes       map[string]classes.Class
	AbilityScores map[string]attributes.AbilityScore
	Skills        []string
}
