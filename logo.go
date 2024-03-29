package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
)

func main() {
	if len(os.Args) != 3 {
		log.Fatal("Usage:", os.Args[0], "<input_file> <output_file>")
	}

	inputFile := os.Args[1]
	outputFile := os.Args[2]

	cmd := exec.Command("ffmpeg", "-i", inputFile, "-filter_complex", "drawtext=text='Utopia':fontfile='./fonts/Anurati-Regular.otf':fontsize=35:x=40:y=40:fontcolor=white", "-c:a", "copy", outputFile)

	// Redirect standard error (stderr) to capture progress information
	cmd.Stderr = os.Stdout

	err := cmd.Run()
	if err != nil {
		log.Fatal("Error:", err)
	}

	fmt.Println("Successfully processed the video.")
}

