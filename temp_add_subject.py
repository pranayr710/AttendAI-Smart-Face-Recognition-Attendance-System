from app.attendance_db import init_db, add_subject
init_db()
add_subject('DSA101', 'Data Structures')
print("Subject added")
