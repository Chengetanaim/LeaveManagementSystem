<h1>Leave Management System</h1>

Fastapi project for managing employee leave.<br>
Run *uvicorn app.main:app --reload* to start server<br>

<h2>Database schema:</h2>
<li>Employee {full name, email, department_id , gender, position}</li>
<li>User {email, password, role}</li>
<li>Grade {id, grade, no of leave days}</li>
<li>EmployeeeGrade {id, grade_id, employee_id}</li>
<li>Leave{id, start_date, days, employee_id,  leave_type}</li>
<li>Department {id, department}</li>
<li>Clocking {id, clock_in_time, clock_out, employee_id}</li>
