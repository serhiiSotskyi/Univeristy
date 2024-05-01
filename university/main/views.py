from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

logger = logging.getLogger(__name__)

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT course_id, course_name FROM courses")
        courses = cursor.fetchall()
        cursor.execute("SELECT department_id, department_name FROM departments")
        departments = cursor.fetchall()
    return render(request, 'main/index.html', {'courses' : courses, 'departments' : departments})

def index2(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT department_id, department_name FROM departments")
        departments = cursor.fetchall()
    return render(request, 'main/index2.html', {'departments' : departments})

def index3(request):
    return render(request, 'main/index3.html')

def get_data_from_database(request):
    selected_table = request.GET.get('table', '')
    
    if selected_table:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {selected_table}")
            data = cursor.fetchall()
        return JsonResponse({'data': data})
    else:
        return JsonResponse({'error': 'No table selected'})

def get_student_data(request):
    student_id = request.GET.get('student_id', '')
    
    if student_id:
        with connection.cursor() as cursor:
            cursor.execute("SELECT student_name, student_surname, student_enrollment_status FROM students WHERE student_id = %s", [student_id])
            row = cursor.fetchone()
            if row:
                enrollment_status = row[2]
                student_name = row[0]
                student_surname = row[1]
                return JsonResponse({'student_id': student_id, 'student_name' : student_name, 'student_surname' : student_surname,  'enrollment_status': enrollment_status})
            else:
                return JsonResponse({'error': 'Student not found'})
    else:
        return JsonResponse({'error': 'No student ID provided'})

def count_enrollments(request):
    selected_course = request.GET.get('course','')

    if selected_course:
        with connection.cursor() as cursor:
            cursor.execute("SELECT enrollments.course_id, courses.course_name,  COUNT(enrollments.student_id) AS enrolled_students FROM enrollments INNER JOIN courses ON enrollments.course_id=courses.course_id WHERE enrollments.course_id = %s GROUP BY courses.course_id, courses.course_name;" , [selected_course])
            row = cursor.fetchone()
            if row: 
                course_id = row[0]
                course_name = row[1]
                enrolled_students = row[2]
                return JsonResponse({'course_id' : course_id, 'course_name' : course_name, 'enrolled_students' : enrolled_students})
            else:
                return JsonResponse({'error': 'Course not found'})
    else:
        return JsonResponse({'error': 'No course provided'})
    
def highest_grade(request):
    selected_course = request.GET.get('course_grade','')

    if selected_course:
        with connection.cursor() as cursor:
            cursor.execute("SELECT students.student_id, students.student_name, students.student_surname, courses.course_name, MAX(grades.grade) AS highest_grade FROM University.students INNER JOIN University.grades ON students.student_id = grades.student_id INNER JOIN University.courses ON grades.course_id = courses.course_id WHERE grades.course_id = %s GROUP BY students.student_id, students.student_name, students.student_surname, courses.course_name;", [selected_course])
            row = cursor.fetchone()
            if row:
                student_id = row[0]
                student_name = row[1]
                student_surname = row[2]
                course_name = row[3]
                highest_grade = row[4]
                return JsonResponse({'student_id' : student_id, 'student_name' : student_name, 'student_surname' : student_surname, 'course_name' : course_name, 'highest_grade' : highest_grade})
            else:
                return JsonResponse({'error': 'Course not found'})
    else:
        return JsonResponse({'error': 'No course provided'})
    
def average_grade(request):
    selected_course = request.GET.get('average_grade','')

    if selected_course:
        with connection.cursor() as cursor:
            cursor.execute("SELECT course_name, ROUND(AVG(grade), 0) as average_grade FROM grades INNER JOIN courses ON grades.course_id = courses.course_id WHERE grades.course_id = %s GROUP BY course_name;", [selected_course])
            row = cursor.fetchone()
            if row:
                course_name = row[0]
                average_grade = row[1]
                return JsonResponse({'course_name' : course_name, 'average_grade' : average_grade})
            else:
                return JsonResponse({'error': 'Course not found'})
    else:
        return JsonResponse({'error': 'No course provided'})
    
def number_of_instructors(request):
    selected_department = request.GET.get('number_of_instructors','')

    if selected_department:
        with connection.cursor() as cursor:
            cursor.execute("SELECT department_name, COUNT(*) as num_instructors FROM instructors JOIN departments ON instructors.department_id = departments.department_id WHERE departments.department_id = %s;", [selected_department])
            row = cursor.fetchone()
            if row:
                department_name = row[0]
                num_instructors = row[1]
                return JsonResponse({'department_name' : department_name, 'num_instructors' : num_instructors})
            else:
                return JsonResponse({'error': 'Department not found'})
    else:
        return JsonResponse({'error': 'No department provided'})
    


def add_student(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Extract data from JSON
        student_name = data.get('student_name', None)
        student_surname = data.get('student_surname', None)
        student_major = data.get('student_major', None)
        student_email = data.get('student_email', None)
        student_phone_number = data.get('student_phone_number', None)
        student_dob = data.get('student_dob', None)
        student_gender = data.get('student_gender', None)
        student_enrollment_status = data.get('student_enrollment_status', None)
        
        # Check if required data is provided
        if not student_name or not student_surname or not student_phone_number:
            return JsonResponse({'error': 'Required fields missing'}, status=400)
        
        # Insert data into database
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO students (student_name, student_surname, student_major, student_email, student_phone_number, student_dob, student_gender, student_enrollment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [student_name, student_surname, student_major, student_email, student_phone_number, student_dob, student_gender, student_enrollment_status])
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def add_instructor(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        instructor_name = data.get('instructor_name', None)
        instructor_surname = data.get('instructor_surname', None)
        department = data.get('department', None)

        if not instructor_name or not instructor_surname:
            return JsonResponse({'error': 'Required fields missing'}, status=400)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO instructors (instructor_name, instructor_surname, department_id)
                VALUES (%s, %s, %s);
                """, [instructor_name, instructor_surname, department])
            
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    




def search_page(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT department_id, department_name FROM departments")
        departments = cursor.fetchall()
    return render(request, "main/search.html", {'departments' : departments})
       
def search_instructor(request):
    instructor_id = request.GET.get('instructor_id', '')
    instructor_name = request.GET.get('instructor_name', '')
    instructor_surname = request.GET.get('instructor_surname', '')

    if not instructor_id and not instructor_name and not instructor_surname:
        return JsonResponse({'error': 'No data provided'}, status=400)

    query = "SELECT * FROM instructors WHERE 1=1"
    query_params = []

    if instructor_id:
        query += " AND instructor_id = %s"
        query_params.append(instructor_id)

    if instructor_name:
        query += " AND instructor_name = %s"
        query_params.append(instructor_name)

    if instructor_surname:
        query += " AND instructor_surname = %s"
        query_params.append(instructor_surname)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_params)
            rows = cursor.fetchall()

            instructors = []
            for row in rows:
                instructor = {
                    'instructor_id': row[0],
                    'instructor_name': row[1],
                    'instructor_surname': row[2],
                    'department': row[3]
                }
                instructors.append(instructor)

            if instructors:
                return JsonResponse({'instructors': instructors})
            else:
                return JsonResponse({'error': 'Instructors not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def update_instructor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)  # Debugging line
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Extract data from JSON
        instructor_id = data.get('instructor_id', None)
        instructor_name = data.get('instructor_name', None)
        instructor_surname = data.get('instructor_surname', None)
        department = data.get('department', None)
        
        print("Extracted data:", instructor_id, instructor_name, instructor_surname, department)  # Debugging line
        
        # Check if required data is provided
        if not instructor_id or not instructor_name or not instructor_surname or not department:
            return JsonResponse({'error': 'Required fields missing'}, status=400)
        
        # Insert data into database
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE instructors 
                    SET instructor_name=%s, instructor_surname=%s, department_id=%s 
                    WHERE instructor_id=%s
                """, [instructor_name, instructor_surname, department, instructor_id])
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            print("Database error:", e)  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def delete_instructor(request, instructor_id):
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM instructors WHERE instructor_id=%s", [instructor_id])
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    


def search_student(reqest):
    student_id = reqest.GET.get('student_id', '')
    student_name = reqest.GET.get('student_name', '')
    student_surname = reqest.GET.get('student_surname', '')
    student_major = reqest.GET.get('student_major', '')
    student_phone_number = reqest.GET.get('student_phone_number', '')
    student_dob = reqest.GET.get('student_dob', '')
    student_email = reqest.GET.get('student_email', '')

    if not student_id and not student_name and not student_surname and not student_major and not student_phone_number and not student_dob and not student_email:
        return JsonResponse({'error': 'No data provided'}, status=400)
    
    query = "SELECT * FROM students WHERE 1=1"
    query_params = []

    if student_id:
        query += " AND student_id = %s"
        query_params.append(student_id)
    
    if student_name:
        query += " AND student_name = %s"
        query_params.append(student_name)

    if student_surname:
        query += " AND student_surname = %s"
        query_params.append(student_surname)

    if student_major:
        query += " AND student_major = %s"
        query_params.append(student_major)

    if student_phone_number:
        query += " AND student_phone_number = %s"
        query_params.append(student_phone_number)

    if student_dob:
        query += " AND student_dob = %s"
        query_params.append(student_dob)

    if student_email:
        query += " AND student_email = %s"
        query_params.append(student_email)

    print("Query:", query)
    print("Params:", query_params)

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_params)
            rows = cursor.fetchall()

            students = []
            for row in rows:
                student = {
                    "student_id" : row[0],
                    "student_name" : row[1],
                    "student_surname" : row[2],
                    "student_major" : row[3],
                    "student_email" : row[4],
                    "student_phone_number" : row[5],
                    "student_dob" : row[6],
                    "student_gender" : row[7],
                    "student_enrollment_status" : row[8],
                }
                students.append(student)

            if students:
                print(students)
                return JsonResponse({'students': students})
            else:
                return JsonResponse({'error': 'Students not found'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def update_student(request, student_id):
    # Retrieve data from request
    data = json.loads(request.body.decode('utf-8'))

    student_name = data.get('student_name', '')
    student_surname = data.get('student_surname', '')
    student_major = data.get('student_major', '')
    student_phone_number = data.get('student_phone_number', '')
    student_dob = data.get('student_dob', '')
    student_email = data.get('student_email', '')

    # Update the student in the database
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE students 
                SET student_name=%s, student_surname=%s, student_major=%s, 
                    student_phone_number=%s, student_dob=%s, student_email=%s
                WHERE student_id=%s
            """, [student_name, student_surname, student_major, student_phone_number,
                  student_dob, student_email, student_id])

        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_student(request, student_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM enrollments WHERE student_id = %s;", [student_id])
            cursor.execute("DELETE FROM students WHERE student_id = %s", [student_id])
            

        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

