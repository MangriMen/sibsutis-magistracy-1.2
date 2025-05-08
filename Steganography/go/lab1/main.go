package main

import (
	"flag"
	"fmt"
	"log"
	"math"
	"os"
	"path/filepath"
	"strings"

	bmp "example.com/images/bitmap"
	"example.com/utils/binary"
	"example.com/utils/file"
)

const (
	bitsPerByte = 8
	lsbBits     = 1
)

func EmbedMessageLsb(img bmp.BMPImage, message []byte) bmp.BMPImage {
	encodedImg := img.Copy()

	messageWithLength := append(binary.UInt32ToBytes(uint32(len(message))), message...)
	totalBits := len(messageWithLength) * bitsPerByte

	for i := 0; i < totalBits && i < len(encodedImg.ColorIndexArray)*lsbBits; i++ {
		byteIndex := i / bitsPerByte
		bitIndex := uint(i % bitsPerByte)
		pixelIndex := i / lsbBits

		messageBit := (messageWithLength[byteIndex] >> bitIndex) & 1
		encodedImg.ColorIndexArray[pixelIndex] = (encodedImg.ColorIndexArray[pixelIndex] & 0xFE) | messageBit
	}

	return encodedImg
}

func ExtractMessageLsb(img bmp.BMPImage) []byte {
	messageLength := 0
	for i := 0; i < 32; i++ {
		pixelIndex := i / lsbBits
		if pixelIndex >= len(img.ColorIndexArray) {
			return nil
		}

		bit := img.ColorIndexArray[pixelIndex] & 1
		messageLength |= int(bit) << uint(i%bitsPerByte)
	}

	message := make([]byte, messageLength)
	for i := 0; i < messageLength*bitsPerByte; i++ {
		pixelIndex := (32 + i) / lsbBits
		if pixelIndex >= len(img.ColorIndexArray) {
			break
		}

		byteIndex := i / bitsPerByte
		bitIndex := uint(i % bitsPerByte)
		bit := img.ColorIndexArray[pixelIndex] & 1

		message[byteIndex] |= bit << bitIndex
	}

	return message
}

func CalculateCapacity(img bmp.BMPImage) int {
	if img.FileInfo.BitCount != 8 {
		return 0
	}

	return len(img.ColorIndexArray) / bitsPerByte
}

func CalculatePSNR(original, stego bmp.BMPImage) float64 {
	var mse float64
	totalPixels := len(original.ColorIndexArray)

	for i := 0; i < totalPixels; i++ {
		diff := float64(original.ColorIndexArray[i]) - float64(stego.ColorIndexArray[i])
		mse += diff * diff
	}
	mse /= float64(totalPixels)

	if mse == 0 {
		return math.Inf(1) // Images are identical
	}

	maxPixelValue := 255.0
	return 20*math.Log10(maxPixelValue) - 10*math.Log10(mse)
}

func VisualAnalysis(original, stego bmp.BMPImage, differencePath string) {
	diff := make([]byte, len(original.ColorIndexArray))
	maxDiff := 0

	for i := 0; i < len(original.ColorIndexArray); i++ {
		d := int(original.ColorIndexArray[i]) - int(stego.ColorIndexArray[i])
		if d < 0 {
			d = -d
		}
		diff[i] = byte(d * 50) // We emphasize the differences for clarity
		if d > maxDiff {
			maxDiff = d
		}
	}

	// Generate difference image
	diffImg := original.Copy()
	diffImg.ColorIndexArray = diff
	file.Write(differencePath, diffImg.ToBytes())
	fmt.Printf("Max single pixel difference: %d\n", maxDiff)
	fmt.Printf("Difference map saved to %s", differencePath)
}

func mustAbs(path string) string {
	abs, err := filepath.Abs(path)
	if err != nil {
		log.Fatalf("Invalid path: %v", err)
	}
	return abs
}

func generateOutputName(inputPath, suffix string) string {
	ext := filepath.Ext(inputPath)
	base := strings.TrimSuffix(inputPath, ext)
	return fmt.Sprintf("%s_%s%s", base, suffix, ext)
}

func encodeCmd(messageFile, inputImage, outputImage string) {
	if outputImage == "" {
		outputImage = generateOutputName(inputImage, "encoded")
	}

	imageData, err := file.Read(mustAbs(inputImage))
	if err != nil {
		log.Fatalf("Can't read image data: %s", err)
	}

	message, err := file.Read(mustAbs(messageFile))
	if err != nil {
		log.Fatalf("Can't read message data: %s", err)
	}

	img := bmp.FromBytes(imageData)
	if img.FileInfo.BitCount != 8 {
		log.Fatal("Only 8-bit BMP images are supported for LSB encoding")
	}

	capacity := CalculateCapacity(img)
	if len(message) > capacity {
		log.Fatalf("Message too large. Capacity: %d bytes, message: %d bytes", capacity, len(message))
	}

	encodedImg := EmbedMessageLsb(img, message)

	fmt.Println("\nEmbedding analysis:")
	fmt.Printf("- Capacity: %d bytes\n", capacity)
	fmt.Printf("- Message size: %d bytes (%.1f%% of capacity)\n",
		len(message), float64(len(message))/float64(capacity)*100)

	psnr := CalculatePSNR(img, encodedImg)
	fmt.Printf("- PSNR: %.2f dB\n", psnr)

	differencePath := filepath.Join(filepath.Dir(mustAbs(outputImage)), fmt.Sprintf("%s_difference.bmp", filepath.Base(outputImage)))
	VisualAnalysis(img, encodedImg, differencePath)

	file.Write(outputImage, encodedImg.ToBytes())
	fmt.Printf("\nStego image saved to %s\n", outputImage)

}

func decodeCmd(inputImage, outputText string) {
	if outputText == "" {
		outputText = generateOutputName(inputImage, "decoded") + ".txt"
	}

	imageData, err := file.Read(mustAbs(inputImage))
	if err != nil {
		log.Fatalf("Can't read image data: %s", err)
	}

	img := bmp.FromBytes(imageData)

	if img.FileInfo.BitCount != 8 {
		log.Fatal("Only 8-bit BMP images are supported for LSB decoding")
	}

	extracted := ExtractMessageLsb(img)
	file.Write(outputText, extracted)

	fmt.Printf("Message successfully extracted to '%s'\n", outputText)
}

func usage() {
	fmt.Printf("Usage: %s <command> [options]\n", os.Args[0])
	fmt.Println("Commands:")
	fmt.Println("  encode - encode message into image")
	fmt.Println("    Example: encode -m secret.txt -i input.bmp [-o output.bmp]")
	fmt.Println("  decode - decode message from image")
	fmt.Println("    Example: decode -i encoded.bmp [-o message.txt]")
	fmt.Println("\nOptions:")
	fmt.Println("  -m, --message  Text file with message to encode (required for encode)")
	fmt.Println("  -i, --input    Input image file (required)")
	fmt.Println("  -o, --output   Output file (optional, will be generated if not specified)")
	fmt.Println("  -h, --help     Show this help message")
	os.Exit(1)
}

func main() {
	if len(os.Args) < 2 {
		usage()
	}

	if strings.HasPrefix(os.Args[1], "-") {
		fmt.Println("Error: command must be specified before flags")
		fmt.Println("Example: go run main.go encode -m secret.txt -i input.bmp")
		usage()
	}

	command := os.Args[1]
	if command == "help" || command == "-h" || command == "--help" {
		usage()
	}

	fs := flag.NewFlagSet(command, flag.ExitOnError)

	messageFile := fs.String("message", "", "Text file with message to encode")
	inputImage := fs.String("input", "", "Input image file")
	outputFile := fs.String("output", "", "Output file (optional)")

	fs.StringVar(messageFile, "m", "", "Short form of --message")
	fs.StringVar(inputImage, "i", "", "Short form of --input")
	fs.StringVar(outputFile, "o", "", "Short form of --output")

	err := fs.Parse(os.Args[2:])
	if err != nil {
		log.Fatal(err)
	}

	switch command {
	case "encode":
		if *messageFile == "" || *inputImage == "" {
			fmt.Println("Error: encode command requires -m and -i parameters")
			usage()
		}
		encodeCmd(*messageFile, *inputImage, *outputFile)
	case "decode":
		if *inputImage == "" {
			fmt.Println("Error: decode command requires -i parameter")
			usage()
		}
		decodeCmd(*inputImage, *outputFile)
	default:
		fmt.Printf("Unknown command: %s\n\n", command)
		usage()
	}
}
