/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var cmdRoot = &cobra.Command{
	Use:   "tasha",
	Short: "Create 5.5e Dungeons & Dragons characters.",
	Long:  `Create 5.5e Dungeons & Dragons characters.`,
}

func Execute() {
	if err := cmdRoot.Execute(); err != nil {
		fmt.Println("Oops. An error occured while executing tasha")
		os.Exit(1)
	}
}
