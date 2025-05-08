package types

import "errors"

// Bounds represents a range [Begin, End).
type Bounds struct {
	Begin, End int
}

const RGBQuadElementsCount = 4

// RGBQuad represents a 4-byte RGB value with reserved byte (used in BMP formats).
type RGBQuad struct {
	RGBBlue     byte
	RGBGreen    byte
	RGBRed      byte
	RGBReserved byte
}

// NewRGBQuad constructs an RGBQuad from a 4-byte slice.
// Returns an error if the slice is too short.
func NewRGBQuad(data []byte) (RGBQuad, error) {
	if len(data) < RGBQuadElementsCount {
		return RGBQuad{}, errors.New("types: data must be at least 4 bytes")
	}
	return RGBQuad{
		RGBBlue:     data[0],
		RGBGreen:    data[1],
		RGBRed:      data[2],
		RGBReserved: data[3],
	}, nil
}

// MustNewRGBQuad constructs an RGBQuad from a 4-byte slice.
// Panics if the slice is too short.
func MustNewRGBQuad(data []byte) RGBQuad {
	if len(data) < RGBQuadElementsCount {
		panic("types: MustNewRGBQuad requires at least 4 bytes")
	}
	rgb, _ := NewRGBQuad(data)
	return rgb
}

// RGBQuadToBytes converts an RGBQuad to a 4-byte slice.
func RGBQuadToBytes(rgb RGBQuad) []byte {
	return []byte{
		rgb.RGBBlue,
		rgb.RGBGreen,
		rgb.RGBRed,
		rgb.RGBReserved,
	}
}

const RGBTripleElementsCount = 3

// RGBTriple represents a 3-byte RGB value (without reserved byte).
type RGBTriple struct {
	RGBTBlue  byte
	RGBTGreen byte
	RGBTRed   byte
}

// NewRGBTriple constructs an RGBTriple from a 3-byte slice.
// Returns an error if the slice is too short.
func NewRGBTriple(data []byte) (RGBTriple, error) {
	if len(data) < RGBTripleElementsCount {
		return RGBTriple{}, errors.New("types: data must be at least 3 bytes")
	}
	return RGBTriple{
		RGBTBlue:  data[0],
		RGBTGreen: data[1],
		RGBTRed:   data[2],
	}, nil
}

// MustNewRGBTriple constructs an RGBTriple from a 3-byte slice.
// Panics if the slice is too short.
func MustNewRGBTriple(data []byte) RGBTriple {
	if len(data) < RGBTripleElementsCount {
		panic("types: MustNewRGBTriple requires at least 3 bytes")
	}
	rgb, _ := NewRGBTriple(data)
	return rgb
}

// RGBTripleToBytes converts an RGBTriple to a 3-byte slice.
func RGBTripleToBytes(rgb RGBTriple) []byte {
	return []byte{
		rgb.RGBTBlue,
		rgb.RGBTGreen,
		rgb.RGBTRed,
	}
}
