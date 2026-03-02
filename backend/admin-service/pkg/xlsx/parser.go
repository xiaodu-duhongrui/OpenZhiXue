package xlsx

import (
	"errors"
	"fmt"
	"strconv"

	"github.com/xuri/excelize/v2"
)

var (
	ErrEmptyFile     = errors.New("empty file")
	ErrInvalidFormat = errors.New("invalid format")
)

type UserImportData struct {
	Row      int    `json:"row"`
	Username string `json:"username"`
	Password string `json:"password"`
	RealName string `json:"real_name"`
	Role     string `json:"role"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	ClassID  uint   `json:"class_id"`
	Errors   string `json:"errors,omitempty"`
}

type Parser struct {
	file *excelize.File
}

func NewParser() *Parser {
	return &Parser{}
}

func (p *Parser) Open(data []byte) error {
	file, err := excelize.OpenReader(excelize.NewReader(data))
	if err != nil {
		return fmt.Errorf("failed to open xlsx file: %w", err)
	}
	p.file = file
	return nil
}

func (p *Parser) OpenFile(path string) error {
	file, err := excelize.OpenFile(path)
	if err != nil {
		return fmt.Errorf("failed to open xlsx file: %w", err)
	}
	p.file = file
	return nil
}

func (p *Parser) Close() error {
	if p.file != nil {
		return p.file.Close()
	}
	return nil
}

func (p *Parser) ParseUsers(sheetName string) ([]*UserImportData, error) {
	if p.file == nil {
		return nil, ErrEmptyFile
	}

	rows, err := p.file.GetRows(sheetName)
	if err != nil {
		return nil, fmt.Errorf("failed to get rows: %w", err)
	}

	if len(rows) < 2 {
		return nil, ErrEmptyFile
	}

	headerMap := make(map[string]int)
	for i, cell := range rows[0] {
		headerMap[cell] = i
	}

	requiredColumns := []string{"username", "password", "realName", "role"}
	for _, col := range requiredColumns {
		if _, ok := headerMap[col]; !ok {
			return nil, fmt.Errorf("%w: missing required column: %s", ErrInvalidFormat, col)
		}
	}

	var users []*UserImportData
	for i, row := range rows[1:] {
		user := &UserImportData{Row: i + 2}

		if idx, ok := headerMap["username"]; ok && idx < len(row) {
			user.Username = row[idx]
		}
		if idx, ok := headerMap["password"]; ok && idx < len(row) {
			user.Password = row[idx]
		}
		if idx, ok := headerMap["realName"]; ok && idx < len(row) {
			user.RealName = row[idx]
		}
		if idx, ok := headerMap["role"]; ok && idx < len(row) {
			user.Role = row[idx]
		}
		if idx, ok := headerMap["email"]; ok && idx < len(row) {
			user.Email = row[idx]
		}
		if idx, ok := headerMap["phone"]; ok && idx < len(row) {
			user.Phone = row[idx]
		}
		if idx, ok := headerMap["classId"]; ok && idx < len(row) {
			if classID, err := strconv.ParseUint(row[idx], 10, 32); err == nil {
				user.ClassID = uint(classID)
			}
		}

		if err := p.validateUser(user); err != nil {
			user.Errors = err.Error()
		}

		users = append(users, user)
	}

	return users, nil
}

func (p *Parser) validateUser(user *UserImportData) error {
	if user.Username == "" {
		return errors.New("username is required")
	}
	if user.Password == "" {
		return errors.New("password is required")
	}
	if user.RealName == "" {
		return errors.New("realName is required")
	}
	if user.Role == "" {
		return errors.New("role is required")
	}
	validRoles := map[string]bool{
		"student": true,
		"teacher": true,
		"admin":   true,
	}
	if !validRoles[user.Role] {
		return fmt.Errorf("invalid role: %s", user.Role)
	}
	return nil
}

func (p *Parser) GetSheetNames() []string {
	if p.file == nil {
		return nil
	}
	return p.file.GetSheetList()
}

func GenerateTemplate() ([]byte, error) {
	f := excelize.NewFile()
	defer f.Close()

	sheet := "Sheet1"
	headers := []string{"username", "password", "realName", "role", "email", "phone", "classId"}

	for i, header := range headers {
		cell, _ := excelize.CoordinatesToCellName(i+1, 1)
		f.SetCellValue(sheet, cell, header)
	}

	exampleData := [][]string{
		{"student1", "password123", "张三", "student", "student1@example.com", "13800138001", "1"},
		{"teacher1", "password123", "李四", "teacher", "teacher1@example.com", "13800138002", ""},
	}

	for rowIdx, row := range exampleData {
		for colIdx, value := range row {
			cell, _ := excelize.CoordinatesToCellName(colIdx+1, rowIdx+2)
			f.SetCellValue(sheet, cell, value)
		}
	}

	for i := range headers {
		col, _ := excelize.ColumnNumberToName(i + 1)
		f.SetColWidth(sheet, col, col, 15)
	}

	return f.WriteToBuffer()
}
