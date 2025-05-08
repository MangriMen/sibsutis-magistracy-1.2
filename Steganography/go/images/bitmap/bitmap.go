package bitmap

import (
	"encoding/json"
	"errors"
	"fmt"
	"math"

	"example.com/utils/binary"
	types "example.com/utils/types"
)

const (
	BMPSignature         uint16 = 0x4D42
	RGBQuadElementsCount int    = 4
	FileHeaderSize       int    = 14
	FileInfoSize         int    = 40
	RowAlignmentBytes    int    = 4
	RowAlignmentBits     int    = RowAlignmentBytes * binary.BitsPerByte
)

var (
	SignatureBounds            = types.Bounds{Begin: 0, End: 2}
	SizeHeaderBounds           = types.Bounds{Begin: 2, End: 6}
	Reserved1Bounds            = types.Bounds{Begin: 6, End: 8}
	Reserved2Bounds            = types.Bounds{Begin: 8, End: 10}
	OffsetBounds               = types.Bounds{Begin: 10, End: 14}
	SizeInfoBounds             = types.Bounds{Begin: 14, End: 18}
	WidthBounds                = types.Bounds{Begin: 18, End: 22}
	HeightBounds               = types.Bounds{Begin: 22, End: 26}
	PlanesBounds               = types.Bounds{Begin: 26, End: 28}
	BitCountBounds             = types.Bounds{Begin: 28, End: 30}
	CompressionBounds          = types.Bounds{Begin: 30, End: 34}
	SizeImageBounds            = types.Bounds{Begin: 34, End: 38}
	HorizontalResolutionBounds = types.Bounds{Begin: 38, End: 42}
	VerticalResolutionBounds   = types.Bounds{Begin: 42, End: 46}
	ColorUsedBounds            = types.Bounds{Begin: 46, End: 50}
	ColorImportantBounds       = types.Bounds{Begin: 50, End: 54}
	BitmapFileHeaderBounds     = types.Bounds{Begin: 0, End: FileHeaderSize}
	BitmapFileInfoBounds       = types.Bounds{Begin: FileHeaderSize, End: FileHeaderSize + FileInfoSize}
)

type BitmapFileHeader struct {
	Signature uint16
	Size      uint32
	Reserved1 uint16
	Reserved2 uint16
	Offset    uint32
}

type BitmapFileInfo struct {
	Size                 uint32
	Width                int32
	Height               int32
	Planes               uint16
	BitCount             uint16
	Compression          uint32
	SizeImage            uint32
	HorizontalResolution int32
	VerticalResolution   int32
	ColorUsed            uint32
	ColorImportant       uint32
}

type BMPMeta struct {
	BitsPerPixel      int
	BytesPerColor     int
	WidthAligned      int32
	WidthAlignedBytes int32
}

type BMPImage struct {
	FileHeader      BitmapFileHeader
	FileInfo        BitmapFileInfo
	RGBQuad         []types.RGBQuad
	ColorIndexArray []byte
	Meta            BMPMeta
}

func newBitmapFileHeader(data []byte) (BitmapFileHeader, error) {
	header := BitmapFileHeader{
		Signature: binary.MustBytesToUInt16(data[SignatureBounds.Begin:SignatureBounds.End]),
		Size:      binary.MustBytesToUInt32(data[SizeHeaderBounds.Begin:SizeHeaderBounds.End]),
		Reserved1: binary.MustBytesToUInt16(data[Reserved1Bounds.Begin:Reserved1Bounds.End]),
		Reserved2: binary.MustBytesToUInt16(data[Reserved2Bounds.Begin:Reserved2Bounds.End]),
		Offset:    binary.MustBytesToUInt32(data[OffsetBounds.Begin:OffsetBounds.End]),
	}

	if header.Signature != BMPSignature {
		return header, errors.New("unsupported format: signature does not match BMP format")
	}

	return header, nil
}

func (h BitmapFileHeader) toBytes() []byte {
	data := make([]byte, 0, FileHeaderSize)
	data = append(data, binary.UInt16ToBytes(h.Signature)...)
	data = append(data, binary.UInt32ToBytes(h.Size)...)
	data = append(data, binary.UInt16ToBytes(h.Reserved1)...)
	data = append(data, binary.UInt16ToBytes(h.Reserved2)...)
	data = append(data, binary.UInt32ToBytes(h.Offset)...)
	return data
}

func newBitmapFileInfo(data []byte) BitmapFileInfo {
	return BitmapFileInfo{
		Size:                 binary.MustBytesToUInt32(data[SizeInfoBounds.Begin:SizeInfoBounds.End]),
		Width:                int32(binary.MustBytesToUInt32(data[WidthBounds.Begin:WidthBounds.End])),
		Height:               int32(binary.MustBytesToUInt32(data[HeightBounds.Begin:HeightBounds.End])),
		Planes:               binary.MustBytesToUInt16(data[PlanesBounds.Begin:PlanesBounds.End]),
		BitCount:             binary.MustBytesToUInt16(data[BitCountBounds.Begin:BitCountBounds.End]),
		Compression:          binary.MustBytesToUInt32(data[CompressionBounds.Begin:CompressionBounds.End]),
		SizeImage:            binary.MustBytesToUInt32(data[SizeImageBounds.Begin:SizeImageBounds.End]),
		HorizontalResolution: int32(binary.MustBytesToUInt32(data[HorizontalResolutionBounds.Begin:HorizontalResolutionBounds.End])),
		VerticalResolution:   int32(binary.MustBytesToUInt32(data[VerticalResolutionBounds.Begin:VerticalResolutionBounds.End])),
		ColorUsed:            binary.MustBytesToUInt32(data[ColorUsedBounds.Begin:ColorUsedBounds.End]),
		ColorImportant:       binary.MustBytesToUInt32(data[ColorImportantBounds.Begin:ColorImportantBounds.End]),
	}
}

func (i BitmapFileInfo) toBytes() []byte {
	data := make([]byte, 0, FileInfoSize)
	data = append(data, binary.UInt32ToBytes(i.Size)...)
	data = append(data, binary.UInt32ToBytes(uint32(i.Width))...)
	data = append(data, binary.UInt32ToBytes(uint32(i.Height))...)
	data = append(data, binary.UInt16ToBytes(i.Planes)...)
	data = append(data, binary.UInt16ToBytes(i.BitCount)...)
	data = append(data, binary.UInt32ToBytes(i.Compression)...)
	data = append(data, binary.UInt32ToBytes(i.SizeImage)...)
	data = append(data, binary.UInt32ToBytes(uint32(i.HorizontalResolution))...)
	data = append(data, binary.UInt32ToBytes(uint32(i.VerticalResolution))...)
	data = append(data, binary.UInt32ToBytes(i.ColorUsed)...)
	data = append(data, binary.UInt32ToBytes(i.ColorImportant)...)
	return data
}

func NewMeta(bitCount uint16, width int32) BMPMeta {
	bitsPerPixel := getBitsPerPixel(int(bitCount))
	bytesPerColor := int(bitCount) / binary.BitsPerByte

	bitsInRow := int(width) * int(bitCount)
	widthAlignedBytes := int32(RowAlignmentBytes) * int32(math.Ceil(float64(bitsInRow)/float64(RowAlignmentBits)))

	var widthAligned int32
	if bitCount < uint16(binary.BitsPerByte) {
		widthAligned = widthAlignedBytes * int32(bitsPerPixel)
	} else {
		widthAligned = widthAlignedBytes / int32(bytesPerColor)
	}

	return BMPMeta{
		BitsPerPixel:      bitsPerPixel,
		BytesPerColor:     bytesPerColor,
		WidthAligned:      widthAligned,
		WidthAlignedBytes: widthAlignedBytes,
	}
}

func newRGBQuadPalette(data []byte) []types.RGBQuad {
	palette := make([]types.RGBQuad, len(data)/RGBQuadElementsCount)
	for i := 0; i < len(palette); i++ {
		start := i * RGBQuadElementsCount
		end := start + RGBQuadElementsCount
		palette[i] = types.MustNewRGBQuad(data[start:end])
	}
	return palette
}

func (img BMPImage) paletteToBytes() []byte {
	data := make([]byte, 0, len(img.RGBQuad)*RGBQuadElementsCount)
	for _, color := range img.RGBQuad {
		data = append(data, types.RGBQuadToBytes(color)...)
	}
	return data
}

func FromBytes(data []byte) BMPImage {
	fileHeader, _ := newBitmapFileHeader(data[:BitmapFileHeaderBounds.End])
	fileInfo := newBitmapFileInfo(data[:BitmapFileInfoBounds.End])
	rgbQuad := newRGBQuadPalette(data[BitmapFileInfoBounds.End:fileHeader.Offset])
	colorIndexArray := data[fileHeader.Offset:]
	meta := NewMeta(fileInfo.BitCount, fileInfo.Width)

	return BMPImage{
		FileHeader:      fileHeader,
		FileInfo:        fileInfo,
		RGBQuad:         rgbQuad,
		ColorIndexArray: colorIndexArray,
		Meta:            meta,
	}
}

func (img BMPImage) ToBytes() []byte {
	data := make([]byte, 0, img.FileHeader.Size)
	data = append(data, img.FileHeader.toBytes()...)
	data = append(data, img.FileInfo.toBytes()...)
	data = append(data, img.paletteToBytes()...)
	data = append(data, img.ColorIndexArray...)
	return data
}

func (img BMPImage) Copy() BMPImage {
	return BMPImage{
		FileHeader:      img.FileHeader,
		FileInfo:        img.FileInfo,
		RGBQuad:         append([]types.RGBQuad(nil), img.RGBQuad...),
		ColorIndexArray: append([]byte(nil), img.ColorIndexArray...),
		Meta:            img.Meta,
	}
}

func getBitsPerPixel(bitCount int) int {
	if bitCount < binary.BitsPerByte {
		return binary.BitsPerByte / bitCount
	}
	return 1
}

func (img BMPImage) getPixelIndex(i, j int) int {
	invertedI := (int(img.FileInfo.Height) - i - 1)

	var row, column int
	if img.FileInfo.BitCount >= uint16(binary.BitsPerByte) {
		row = invertedI * int(img.Meta.WidthAlignedBytes)
		column = j * img.Meta.BytesPerColor
	} else {
		row = invertedI * int(img.Meta.WidthAligned) / img.Meta.BitsPerPixel
		column = j / img.Meta.BitsPerPixel
	}

	return row + column
}

func (img BMPImage) getPixelBounds(j int) (int, int) {
	if img.FileInfo.BitCount == uint16(binary.BitsPerByte) {
		return 0, binary.BitsPerByte
	}

	startBit := int(img.FileInfo.BitCount) - (j%img.Meta.BitsPerPixel)*int(img.FileInfo.BitCount)
	endBit := startBit + int(img.FileInfo.BitCount)
	return startBit, endBit
}

func (img BMPImage) SetPixelColorIndex(i, j int, colorIndex uint8) {
	index := img.getPixelIndex(i, j)
	startBit, endBit := img.getPixelBounds(j)

	for bit, shift := startBit, 0; bit < endBit; bit, shift = bit+1, shift+1 {
		img.ColorIndexArray[index] = byte(binary.ClearBit(int(img.ColorIndexArray[index]), uint(bit)))
		if binary.HasBit(int(colorIndex), uint(shift)) {
			img.ColorIndexArray[index] = byte(binary.SetBit(int(img.ColorIndexArray[index]), uint(bit)))
		}
	}
}

func (img BMPImage) GetPixelColorIndex(i, j int) uint8 {
	index := img.getPixelIndex(i, j)
	startBit, endBit := img.getPixelBounds(j)

	var colorIndex uint8
	for bit, shift := startBit, 0; bit < endBit; bit, shift = bit+1, shift+1 {
		if binary.HasBit(int(img.ColorIndexArray[index]), uint(bit)) {
			colorIndex = byte(binary.SetBit(int(colorIndex), uint(shift)))
		}
	}

	return colorIndex
}

func (img BMPImage) getPixel(i, j int) types.RGBQuad {
	index := img.getPixelIndex(i, j)
	color := types.RGBQuad{
		RGBBlue:     img.ColorIndexArray[index],
		RGBGreen:    img.ColorIndexArray[index+1],
		RGBRed:      img.ColorIndexArray[index+2],
		RGBReserved: 0,
	}

	if img.FileInfo.BitCount == 32 {
		color.RGBReserved = img.ColorIndexArray[index+3]
	}

	return color
}

func (img BMPImage) setPixel(i, j int, color types.RGBQuad) {
	index := img.getPixelIndex(i, j)
	img.ColorIndexArray[index] = color.RGBBlue
	img.ColorIndexArray[index+1] = color.RGBGreen
	img.ColorIndexArray[index+2] = color.RGBRed

	if img.FileInfo.BitCount == 32 {
		img.ColorIndexArray[index+3] = color.RGBReserved
	}
}

func (img BMPImage) GetPixelColor(i, j int) types.RGBQuad {
	if img.FileInfo.BitCount <= uint16(binary.BitsPerByte) {
		colorIndex := img.GetPixelColorIndex(i, j)
		return img.RGBQuad[colorIndex]
	}
	return img.getPixel(i, j)
}

func (img BMPImage) SetPixelColor(i, j int, color types.RGBQuad) {
	img.setPixel(i, j, color)
}

func (img BMPImage) PrintStructure() {
	prefix := ""
	indent := "  "

	header, _ := json.MarshalIndent(img.FileHeader, prefix, indent)
	info, _ := json.MarshalIndent(img.FileInfo, prefix, indent)
	rgbQuad, _ := json.MarshalIndent(img.RGBQuad, prefix, indent)

	fmt.Printf("File header: %s\n", header)
	fmt.Printf("File info: %s\n", info)
	fmt.Printf("Palette: %s\n", rgbQuad)
}
