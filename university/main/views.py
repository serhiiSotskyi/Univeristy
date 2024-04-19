from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'main/index.html')

def index2(request):
    return render(request, 'main/index2.html')

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

        if not instructor_name or not instructor_surname or not department:
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
    return render(request, "main/search.html")

# def search_instructor(request):
    
#     instructor_id = request.GET.get('instructor_id', '')
#     instructor_name = request.GET.get('instructor_name', '')
#     instructor_surname = request.GET.get('instructor_surname', '')
        
#     if not instructor_id and not instructor_name and not instructor_surname:
#         return JsonResponse({'error': 'No data provided'}, status=400)
#     elif not instructor_id and not instructor_name:
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                 SELECT * FROM instructors WHERE instructor_surname = %s;
#                 """, [instructor_surname])

#                 row = cursor.fetchall()

#                 if row:
#                     instructor_id = row[0]
#                     instructor_name = row[1]
#                     instructor_surname = row[2]
#                     department = row[3]

#                     return JsonResponse({'instructor_id': instructor_id, 'instructor_name' : instructor_name, 'instructor_surname' : instructor_surname, 'department' : department})
            
#                 else:
#                     return JsonResponse({'error': 'Instructor not found'})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     elif not instructor_id and not instructor_surname:
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                 SELECT * FROM instructors WHERE instructor_name = %s;
#                 """, [instructor_name])

#                 row = cursor.fetchall()

#                 if row:
#                     instructor_id = row[0]
#                     instructor_name = row[1]
#                     instructor_surname = row[2]
#                     department = row[3]

#                     return JsonResponse({'instructor_id': instructor_id, 'instructor_name' : instructor_name, 'instructor_surname' : instructor_surname, 'department' : department})
            
#                 else:
#                     return JsonResponse({'error': 'Instructor not found'})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
        
#     elif not instructor_name and not instructor_surname:
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                 SELECT * FROM instructors WHERE instructor_id = %s;
#                 """, [instructor_id])

#                 row = cursor.fetchall()

#                 if row:
#                     instructor_id = row[0]
#                     instructor_name = row[1]
#                     instructor_surname = row[2]
#                     department = row[3]

#                     return JsonResponse({'instructor_id': instructor_id, 'instructor_name' : instructor_name, 'instructor_surname' : instructor_surname, 'department' : department})
            
#                 else:
#                     return JsonResponse({'error': 'Instructor not found'})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
        
#     elif not instructor_id:
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                 SELECT * FROM instructors WHERE instructor_name = %s, instructor_surname = %s;
#                 """, [instructor_name, instructor_surname])

#                 row = cursor.fetchall()

#                 if row:
#                     instructor_id = row[0]
#                     instructor_name = row[1]
#                     instructor_surname = row[2]
#                     department = row[3]

#                     return JsonResponse({'instructor_id': instructor_id, 'instructor_name' : instructor_name, 'instructor_surname' : instructor_surname, 'department' : department})
            
#                 else:
#                     return JsonResponse({'error': 'Instructor not found'})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
    
#     elif not instructor_name:
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                 SELECT * FROM instructors WHERE instructor_id = %s, instructor_surname = %s;
#                 """, [instructor_id, instructor_surname])

#                 row = cursor.fetchall()

#                 if row:
#                     instructor_id = row[0]
#                     instructor_name = row[1]
#                     instructor_surname = row[2]
#                     department = row[3]

#                     return JsonResponse({'instructor_id': instructor_id, 'instructor_name' : instructor_name, 'instructor_surname' : instructor_surname, 'department' : department})
            
#                 else:
#                     return JsonResponse({'error': 'Instructor not found'})
                
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
        
#     elif not instructor_surname:
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                 SELECT * FROM instructors WHERE instructor_id = %s, instructor_name = %s;
#                 """, [instructor_id, instructor_name])

#                 row = cursor.fetchall()

#                 if row:
#                     instructor_id = row[0]
#                     instructor_name = row[1]
#                     instructor_surname = row[2]
#                     department = row[3]

#                     return JsonResponse({'instructor_id': instructor_id, 'instructor_name' : instructor_name, 'instructor_surname' : instructor_surname, 'department' : department})
            
#                 else:
#                     return JsonResponse({'error': 'Instructor not found'})

#         except Exception as e:
#             logger.error("Error executing SQL query: %s", e)
#             return JsonResponse({'error': 'Internal server error'}, status=500)

       
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
    print(query)
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
