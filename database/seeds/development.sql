-- Development Seed Data for AI Academic Coach
-- IMPORTANT: For local development and testing only. Do NOT run in production.

-- 1. Sample Universities
INSERT INTO universities (id, name, country, website, timezone)
VALUES 
    ('00000000-0000-4000-a000-000000000001', 'Global Academic University', 'United States', 'https://example-university.edu', 'America/New_York'),
    ('00000000-0000-4000-a000-000000000002', 'International Institute of Technology', 'United Kingdom', 'https://example-tech.ac.uk', 'Europe/London')
ON CONFLICT (name, country) DO NOTHING;

-- 2. Sample Courses
INSERT INTO courses (id, university_id, course_code, course_name, description, credit_hours)
VALUES 
    ('00000000-0000-4000-a000-000000000101', '00000000-0000-4000-a000-000000000001', 'CS101', 'Introduction to Computer Science', 'Fundamental concepts of programming, algorithms, and computational thinking.', 4),
    ('00000000-0000-4000-a000-000000000102', '00000000-0000-4000-a000-000000000001', 'MATH201', 'Multivariable Calculus', 'Vectors, partial derivatives, multiple integrals, and vector calculus.', 3),
    ('00000000-0000-4000-a000-000000000103', '00000000-0000-4000-a000-000000000002', 'SE302', 'Software Architecture', 'Design patterns, microservices, system modeling, and scalable systems.', 4)
ON CONFLICT (university_id, course_code) DO NOTHING;

-- 3. Sample Demo User & Student Profile (Fictional Test Data)
INSERT INTO users (id, email, password_hash, account_status)
VALUES 
    ('00000000-0000-4000-a000-000000000201', 'student.demo@example.edu', '$2b$12$eImiTXuWVxfM37uY4JANjO5yY8g/B.z78t0d.wN0h.c0t1e2m3s4q', 'active')
ON CONFLICT (email) DO NOTHING;

INSERT INTO student_profiles (id, user_id, full_name, university_id, program, level, semester, academic_year, timezone, country)
VALUES 
    ('00000000-0000-4000-a000-000000000301', '00000000-0000-4000-a000-000000000201', 'Demo Student', '00000000-0000-4000-a000-000000000001', 'Computer Science B.S.', 'Undergraduate', 'Fall Semester', '2026/2027', 'America/New_York', 'United States')
ON CONFLICT (user_id) DO NOTHING;

-- 4. Sample Course Enrollment
INSERT INTO course_enrollments (id, student_id, course_id, academic_year, semester, status)
VALUES 
    ('00000000-0000-4000-a000-000000000401', '00000000-0000-4000-a000-000000000301', '00000000-0000-4000-a000-000000000101', '2026/2027', 'Fall Semester', 'active')
ON CONFLICT (student_id, course_id, academic_year, semester) DO NOTHING;
