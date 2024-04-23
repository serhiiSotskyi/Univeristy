from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_data_from_database/', views.get_data_from_database, name='get_data_from_database'),
    path('get_student_data/', views.get_student_data, name='get_student_data'),
    path('count_enrollments/', views.count_enrollments, name='count_enrollments'),
    path('highest_grade/', views.highest_grade, name='highest_grade'),
    path('number_of_instructors/', views.number_of_instructors, name='number_of_instructors'),
    path('average_grade/', views.average_grade, name='average_grade'),
    path('add_page', views.index2, name='index2'),
    path('add_student/', views.add_student, name='add_student'),
    path('add_instructor/', views.add_instructor, name='add_instructor'),
    path('search_page/', views.search_page, name='search_page'),
    path('search_instructor/', views.search_instructor, name='search_instructor'),
    path('update_instructor/', views.update_instructor, name='update_instructor'),
    path('delete_instructor/<int:instructor_id>/', views.delete_instructor, name='delete_instructor'),
    path('search_student/', views.search_student, name='search_student'),
    path('update_student/<int:student_id>/', views.update_student, name='update_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
]
