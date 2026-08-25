from app.database.connection import engine
from sqlalchemy import text

def main():
    with engine.connect() as conn:
        print("=== USERS TABLE ===")
        users = conn.execute(text("SELECT id, email, account_status, created_at FROM users")).fetchall()
        print(users)

        print("\n=== STUDENT PROFILES TABLE ===")
        profiles = conn.execute(text("SELECT id, user_id, full_name, university_id, onboarding_completed FROM student_profiles")).fetchall()
        print(profiles)

        print("\n=== COURSE ENROLLMENTS TABLE ===")
        enrollments = conn.execute(text("SELECT id, student_id, course_id, status FROM course_enrollments")).fetchall()
        print(enrollments)

if __name__ == "__main__":
    main()

