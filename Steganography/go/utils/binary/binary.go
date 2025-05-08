package binary

const BitsPerByte = 8

// SetBit sets the bit at position pos.
func SetBit(n int, pos uint) int {
	return n | (1 << pos)
}

// ClearBit clears the bit at position pos.
func ClearBit(n int, pos uint) int {
	return n &^ (1 << pos) // idiomatic Go: AND NOT
}

// HasBit returns true if the bit at position pos is set.
func HasBit(n int, pos uint) bool {
	return (n & (1 << pos)) != 0
}

// BytesToUInt32 converts the first 4 bytes of b to a uint32.
// Returns false if there are fewer than 4 bytes.
func BytesToUInt32(b []byte) (uint32, bool) {
	if len(b) < 4 {
		return 0, false
	}
	return uint32(b[0]) |
		uint32(b[1])<<8 |
		uint32(b[2])<<16 |
		uint32(b[3])<<24, true
}

// BytesToUInt16 converts the first 2 bytes of b to a uint16.
// Returns false if there are fewer than 2 bytes.
func BytesToUInt16(b []byte) (uint16, bool) {
	if len(b) < 2 {
		return 0, false
	}
	return uint16(b[0]) | uint16(b[1])<<8, true
}

// UInt32ToBytes converts a uint32 to a 4-byte slice (little-endian).
func UInt32ToBytes(n uint32) []byte {
	return []byte{
		byte(n),
		byte(n >> 8),
		byte(n >> 16),
		byte(n >> 24),
	}
}

// UInt16ToBytes converts a uint16 to a 2-byte slice (little-endian).
func UInt16ToBytes(n uint16) []byte {
	return []byte{
		byte(n),
		byte(n >> 8),
	}
}

// MustBytesToUInt32 converts 4 bytes to uint32 or panics if input is invalid.
func MustBytesToUInt32(b []byte) uint32 {
	if len(b) < 4 {
		panic("binary: MustBytesToUInt32 requires at least 4 bytes")
	}
	val, _ := BytesToUInt32(b)
	return val
}

// MustBytesToUInt16 converts 2 bytes to uint16 or panics if input is invalid.
func MustBytesToUInt16(b []byte) uint16 {
	if len(b) < 2 {
		panic("binary: MustBytesToUInt16 requires at least 2 bytes")
	}
	val, _ := BytesToUInt16(b)
	return val
}
