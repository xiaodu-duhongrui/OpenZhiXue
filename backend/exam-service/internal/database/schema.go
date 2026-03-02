package database

const Schema = `
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    subject_ids TEXT[] DEFAULT '{}',
    class_ids TEXT[] DEFAULT '{}',
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    total_score DECIMAL(10,2) DEFAULT 0,
    pass_score DECIMAL(10,2) DEFAULT 60,
    description TEXT,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    options JSONB DEFAULT '[]',
    answer TEXT NOT NULL,
    score DECIMAL(10,2) NOT NULL,
    question_order INTEGER NOT NULL,
    analysis TEXT,
    difficulty INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exam_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    submit_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started',
    total_score DECIMAL(10,2) DEFAULT 0,
    elapsed_time INTEGER DEFAULT 0,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exam_id, student_id)
);

CREATE TABLE IF NOT EXISTS exam_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    answer TEXT NOT NULL,
    score DECIMAL(10,2) DEFAULT 0,
    max_score DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    graded_by UUID,
    graded_at TIMESTAMP WITH TIME ZONE,
    feedback TEXT,
    auto_graded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_exams_status ON exams(status);
CREATE INDEX IF NOT EXISTS idx_exams_start_time ON exams(start_time);
CREATE INDEX IF NOT EXISTS idx_exams_created_by ON exams(created_by);
CREATE INDEX IF NOT EXISTS idx_questions_exam_id ON questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_questions_order ON questions(exam_id, question_order);
CREATE INDEX IF NOT EXISTS idx_sessions_exam_id ON exam_sessions(exam_id);
CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON exam_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON exam_sessions(status);
CREATE INDEX IF NOT EXISTS idx_answers_session_id ON exam_answers(session_id);
CREATE INDEX IF NOT EXISTS idx_answers_question_id ON exam_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_answers_status ON exam_answers(status);
`

func Migrate(db Queryer) error {
	_, err := db.Exec(context.Background(), Schema)
	return err
}

type Queryer interface {
	Exec(ctx context.Context, sql string, arguments ...interface{}) (interface{}, error)
}
