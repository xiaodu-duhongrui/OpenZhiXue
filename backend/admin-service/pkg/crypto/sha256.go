package crypto

import (
	"crypto/sha256"
	"encoding/hex"
)

func SHA256Hash(data []byte) []byte {
	hash := sha256.Sum256(data)
	return hash[:]
}

func SHA256HashString(data []byte) string {
	hash := sha256.Sum256(data)
	return hex.EncodeToString(hash[:])
}

func SHA256HashHex(hexString string) (string, error) {
	data, err := hex.DecodeString(hexString)
	if err != nil {
		return "", err
	}
	return SHA256HashString(data), nil
}
