/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var (
	currentVer = "1.0.0"
	cmdVersion = &cobra.Command{
		Use:   "version",
		Short: "Gets the current version of the program",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("%s", currentVer)
		},
	}
)

func init() {
	cmdRoot.AddCommand(cmdVersion)
}
