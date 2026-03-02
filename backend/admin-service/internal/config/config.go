package config

import (
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Server   ServerConfig   `yaml:"server"`
	Database DatabaseConfig `yaml:"database"`
	JWT      JWTConfig      `yaml:"jwt"`
	Crypto   CryptoConfig   `yaml:"crypto"`
	Import   ImportConfig   `yaml:"import"`
	Log      LogConfig      `yaml:"log"`
}

type ServerConfig struct {
	Host string `yaml:"host"`
	Port int    `yaml:"port"`
	Mode string `yaml:"mode"`
}

type DatabaseConfig struct {
	Driver       string `yaml:"driver"`
	Host         string `yaml:"host"`
	Port         int    `yaml:"port"`
	Username     string `yaml:"username"`
	Password     string `yaml:"password"`
	DBName       string `yaml:"dbname"`
	SSLMode      string `yaml:"sslmode"`
	MaxIdleConns int    `yaml:"max_idle_conns"`
	MaxOpenConns int    `yaml:"max_open_conns"`
}

type JWTConfig struct {
	Secret            string `yaml:"secret"`
	Issuer            string `yaml:"issuer"`
	AccessTokenExpire int    `yaml:"access_token_expire"`
}

type CryptoConfig struct {
	AESKey             string `yaml:"aes_key"`
	RSAPrivateKeyPath  string `yaml:"rsa_private_key_path"`
	RSAPublicKeyPath   string `yaml:"rsa_public_key_path"`
}

type ImportConfig struct {
	UploadDir   string `yaml:"upload_dir"`
	MaxFileSize int64  `yaml:"max_file_size"`
}

type LogConfig struct {
	Level  string `yaml:"level"`
	Format string `yaml:"format"`
}

func Load(configPath string) (*Config, error) {
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}

	return &cfg, nil
}
