/*
Copyright © 2025 Marcus Taylor <mtaylor9754@hotmail.com>
*/
package cmd

import (
	"fmt"
	"log"
	"os"
	"strings"

	"tasha/record"

	"github.com/BurntSushi/toml"
	"github.com/spf13/cobra"
)

var cmdRead = &cobra.Command{
	Use:   "read",
	Short: "Read an existing character sheet",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		var cs record.PC
		csFile := fmt.Sprintf("%s.toml", strings.ToLower(strings.ReplaceAll(args[0], " ", "_")))
		fp, err := os.Open(csFile)
		if err != nil {
			log.Fatalf("Failed to open character sheet: %v", err)
		}
		defer fp.Close()
		if err := toml.NewEncoder(fp).Encode(&cs); err != nil {
			log.Fatalf("Failed to encode toml data: %v", err)
		}

		fmt.Println(cs.Name)
	},
}

func init() {
	cmdRoot.AddCommand(cmdRead)
}
