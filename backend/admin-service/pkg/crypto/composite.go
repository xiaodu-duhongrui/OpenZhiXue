package crypto

import (
	"crypto/rsa"
	"encoding/binary"
	"errors"
)

var (
	ErrSignatureVerification = errors.New("signature verification failed")
	ErrHashMismatch          = errors.New("hash verification failed")
)

type CompositeResult struct {
	Ciphertext []byte
	Signature  []byte
	Hash       []byte
}

func CompositeEncrypt(plaintext []byte, aesKey []byte, rsaPrivateKey *rsa.PrivateKey) (*CompositeResult, error) {
	hash := SHA256Hash(plaintext)

	ciphertext, err := AESEncrypt(plaintext, aesKey)
	if err != nil {
		return nil, err
	}

	signature, err := RSASign(ciphertext, rsaPrivateKey)
	if err != nil {
		return nil, err
	}

	return &CompositeResult{
		Ciphertext: ciphertext,
		Signature:  signature,
		Hash:       hash,
	}, nil
}

func CompositeDecrypt(ciphertext, signature []byte, aesKey []byte, rsaPublicKey *rsa.PublicKey) ([]byte, error) {
	if err := RSAVerify(ciphertext, signature, rsaPublicKey); err != nil {
		return nil, ErrSignatureVerification
	}

	plaintext, err := AESDecrypt(ciphertext, aesKey)
	if err != nil {
		return nil, err
	}

	return plaintext, nil
}

func CompositeEncryptWithHash(plaintext []byte, aesKey []byte, rsaPrivateKey *rsa.PrivateKey) ([]byte, error) {
	result, err := CompositeEncrypt(plaintext, aesKey, rsaPrivateKey)
	if err != nil {
		return nil, err
	}

	hashLen := len(result.Hash)
	sigLen := len(result.Signature)

	output := make([]byte, 4+hashLen+4+sigLen+len(result.Ciphertext))
	offset := 0

	binary.BigEndian.PutUint32(output[offset:], uint32(hashLen))
	offset += 4
	copy(output[offset:], result.Hash)
	offset += hashLen

	binary.BigEndian.PutUint32(output[offset:], uint32(sigLen))
	offset += 4
	copy(output[offset:], result.Signature)
	offset += sigLen

	copy(output[offset:], result.Ciphertext)

	return output, nil
}

func CompositeDecryptWithHash(data []byte, aesKey []byte, rsaPublicKey *rsa.PublicKey) ([]byte, error) {
	if len(data) < 8 {
		return nil, errors.New("data too short")
	}

	offset := 0

	hashLen := binary.BigEndian.Uint32(data[offset:])
	offset += 4
	if len(data) < offset+int(hashLen) {
		return nil, errors.New("invalid hash length")
	}
	storedHash := data[offset : offset+int(hashLen)]
	offset += int(hashLen)

	sigLen := binary.BigEndian.Uint32(data[offset:])
	offset += 4
	if len(data) < offset+int(sigLen) {
		return nil, errors.New("invalid signature length")
	}
	signature := data[offset : offset+int(sigLen)]
	offset += int(sigLen)

	ciphertext := data[offset:]

	plaintext, err := CompositeDecrypt(ciphertext, signature, aesKey, rsaPublicKey)
	if err != nil {
		return nil, err
	}

	computedHash := SHA256Hash(plaintext)
	if !equalHash(storedHash, computedHash) {
		return nil, ErrHashMismatch
	}

	return plaintext, nil
}

func equalHash(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
