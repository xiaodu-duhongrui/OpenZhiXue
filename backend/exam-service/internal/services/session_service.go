package services

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/repositories"
)

var (
	ErrSessionNotFound      = errors.New("exam session not found")
	ErrSessionAlreadyExists = errors.New("exam session already exists")
	ErrSessionExpired       = errors.New("exam session has expired")
	ErrSessionSubmitted     = errors.New("exam session already submitted")
	ErrExamNotPublished     = errors.New("exam is not published")
	ErrExamNotStarted       = errors.New("exam has not started")
	ErrExamEnded            = errors.New("exam has ended")
)

type SessionService struct {
	sessionRepo *repositories.SessionRepository
	examRepo    *repositories.ExamRepository
	answerRepo  *repositories.AnswerRepository
	questionRepo *repositories.QuestionRepository
}

func NewSessionService(
	sessionRepo *repositories.SessionRepository,
	examRepo *repositories.ExamRepository,
	answerRepo *repositories.AnswerRepository,
	questionRepo *repositories.QuestionRepository,
) *SessionService {
	return &SessionService{
		sessionRepo:  sessionRepo,
		examRepo:     examRepo,
		answerRepo:   answerRepo,
		questionRepo: questionRepo,
	}
}

func (s *SessionService) StartExam(ctx context.Context, examID, studentID uuid.UUID, req *models.SessionStartRequest) (*models.ExamSession, error) {
	exam, err := s.examRepo.GetByID(ctx, examID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrExamNotFound
		}
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}

	if exam.Status != models.ExamStatusPublished && exam.Status != models.ExamStatusOngoing {
		return nil, ErrExamNotPublished
	}

	now := time.Now()
	if now.Before(exam.StartTime) {
		return nil, ErrExamNotStarted
	}
	if now.After(exam.EndTime) {
		return nil, ErrExamEnded
	}

	existingSession, err := s.sessionRepo.GetByExamAndStudent(ctx, examID, studentID)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		return nil, fmt.Errorf("failed to check existing session: %w", err)
	}
	if existingSession != nil {
		if existingSession.Status == models.SessionStatusSubmitted || existingSession.Status == models.SessionStatusGraded {
			return nil, ErrSessionSubmitted
		}
		return existingSession, nil
	}

	session := models.NewExamSession(examID, studentID, exam.Duration)
	session.IPAddress = req.IPAddress
	session.UserAgent = req.UserAgent

	if err := s.sessionRepo.Create(ctx, session); err != nil {
		return nil, fmt.Errorf("failed to create session: %w", err)
	}

	questions, err := s.questionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, fmt.Errorf("failed to get questions: %w", err)
	}

	for _, q := range questions {
		answer := models.NewExamAnswer(session.ID, q.ID, "", q.Score)
		if err := s.answerRepo.Create(ctx, answer); err != nil {
			return nil, fmt.Errorf("failed to initialize answer: %w", err)
		}
	}

	return session, nil
}

func (s *SessionService) GetSession(ctx context.Context, sessionID uuid.UUID) (*models.ExamSession, error) {
	session, err := s.sessionRepo.GetByID(ctx, sessionID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrSessionNotFound
		}
		return nil, fmt.Errorf("failed to get session: %w", err)
	}
	return session, nil
}

func (s *SessionService) GetSessionByExamAndStudent(ctx context.Context, examID, studentID uuid.UUID) (*models.ExamSession, error) {
	session, err := s.sessionRepo.GetByExamAndStudent(ctx, examID, studentID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrSessionNotFound
		}
		return nil, fmt.Errorf("failed to get session: %w", err)
	}
	return session, nil
}

func (s *SessionService) GetSessionWithQuestions(ctx context.Context, sessionID uuid.UUID) (*models.SessionResponse, error) {
	session, err := s.GetSession(ctx, sessionID)
	if err != nil {
		return nil, err
	}

	exam, err := s.examRepo.GetByID(ctx, session.ExamID)
	if err != nil {
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}

	questions, err := s.questionRepo.GetByExamIDWithoutAnswers(ctx, session.ExamID)
	if err != nil {
		return nil, fmt.Errorf("failed to get questions: %w", err)
	}

	answers, err := s.answerRepo.GetBySessionID(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get answers: %w", err)
	}

	answerMap := make(map[uuid.UUID]models.ExamAnswer)
	for _, a := range answers {
		answerMap[a.QuestionID] = a
	}

	questionResponses := make([]models.QuestionResponse, len(questions))
	for i, q := range questions {
		questionResponses[i] = models.QuestionResponse{
			Question: q,
		}
		if a, ok := answerMap[q.ID]; ok {
			questionResponses[i].StudentAnswer = a.Answer
		}
	}

	return &models.SessionResponse{
		ExamSession:   *session,
		Exam:          exam,
		RemainingTime: session.RemainingTime(),
		Questions:     questionResponses,
	}, nil
}

func (s *SessionService) SubmitAnswer(ctx context.Context, sessionID uuid.UUID, req *models.AnswerSubmitRequest) error {
	session, err := s.GetSession(ctx, sessionID)
	if err != nil {
		return err
	}

	if session.Status != models.SessionStatusInProgress {
		return ErrSessionSubmitted
	}

	if session.IsExpired() {
		return ErrSessionExpired
	}

	questionID, err := uuid.Parse(req.QuestionID)
	if err != nil {
		return fmt.Errorf("invalid question id: %w", err)
	}

	answer, err := s.answerRepo.GetBySessionAndQuestion(ctx, sessionID, questionID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return ErrQuestionNotFound
		}
		return fmt.Errorf("failed to get answer: %w", err)
	}

	answer.Answer = req.Answer
	answer.UpdatedAt = time.Now()

	return s.answerRepo.Update(ctx, answer)
}

func (s *SessionService) SubmitAnswers(ctx context.Context, sessionID uuid.UUID, req *models.AnswerBatchSubmitRequest) error {
	for _, a := range req.Answers {
		if err := s.SubmitAnswer(ctx, sessionID, &a); err != nil {
			return err
		}
	}
	return nil
}

func (s *SessionService) SubmitExam(ctx context.Context, sessionID uuid.UUID, force bool) error {
	session, err := s.GetSession(ctx, sessionID)
	if err != nil {
		return err
	}

	if session.Status != models.SessionStatusInProgress {
		return ErrSessionSubmitted
	}

	if session.IsExpired() && !force {
		return ErrSessionExpired
	}

	return s.sessionRepo.Submit(ctx, sessionID, 0)
}

func (s *SessionService) GetSessionsByExam(ctx context.Context, examID uuid.UUID) ([]models.ExamSession, error) {
	return s.sessionRepo.GetByExamID(ctx, examID)
}

func (s *SessionService) UpdateElapsedTime(ctx context.Context, sessionID uuid.UUID, elapsedSeconds int) error {
	session, err := s.GetSession(ctx, sessionID)
	if err != nil {
		return err
	}

	session.ElapsedTime = elapsedSeconds
	return s.sessionRepo.Update(ctx, session)
}
