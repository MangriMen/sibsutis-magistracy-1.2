package file

import (
	"os"
	"path/filepath"
	"strings"
)

// Read reads the contents of a file at the given path.
// Returns the file data and any read error.
func Read(path string) ([]byte, error) {
	return os.ReadFile(path)
}

// Write removes any existing file at the path and writes new data.
// Returns an error if removal or writing fails.
func Write(path string, data []byte) error {
	if err := os.RemoveAll(path); err != nil {
		return err
	}
	return os.WriteFile(path, data, 0644)
}

// GetFilenameWithoutExt returns the file name without extension from the given path.
func GetFilenameWithoutExt(path string) string {
	base := filepath.Base(path)
	ext := filepath.Ext(base)
	return strings.TrimSuffix(base, ext)
}
