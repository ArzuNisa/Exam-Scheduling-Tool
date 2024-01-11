import pandas as pd
import numpy as np
import copy
import random
import math


class ExamSchedulingTool:
    def __init__(self, class_list_file_path='class_list.csv', classroom_capacities_file_path='classroom_capacities.csv'):
        self.class_list = pd.read_csv(class_list_file_path)
        self.classroom_capacity_list = pd.read_csv(classroom_capacities_file_path)

        self.classroom_real_capacities = None
        self.empty_schedule = None

        self.all_student_numbers = self.class_list["StudentID"].unique().tolist()
        self.all_professor_names = self.class_list["Professor Name"].unique().tolist()

        self.init_classroom_capacities()
        self.init_empty_schedule()

    def init_classroom_capacities(self):
        # Get a copy of the classroom data
        self.classroom_real_capacities = self.classroom_capacity_list.copy()

        # Set the real capacities to half of the original capacities
        self.classroom_real_capacities["Capacity"] = (self.classroom_capacity_list["Capacity"] / 2).astype(int)
        self.classroom_real_capacities["Occupied"] = False
        # Set the free after time to 9.00 - by default
        self.classroom_real_capacities["Free After Time"] = "09.00"

        # Sort the classrooms by capacity
        self.classroom_real_capacities.sort_values(by=['Capacity'], inplace=True, ascending=False)

    def init_empty_schedule(self):
        # Set the empty schedule to the default schedule
        self.empty_schedule = {"Monday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Tuesday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Wednesday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Thursday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Friday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Saturday":{"09.00":{"course":"", "room":"", "end time":""}}
            }
        
        # Add the rest of the times - every 30 minutes 
        for day in self.empty_schedule:
            time = "09.00"
            while time != "18.30":
                self.empty_schedule[day][time] = {"course": "", "room": "", "end time":""}
                time = pd.to_datetime(time, format="%H.%M") + pd.DateOffset(minutes=30)
                time = time.strftime("%H.%M")

    def student_has_two_exams_at_same_time(self, student_id, course1, course2):
        student_courses = self.get_all_courses_of_student(student_id)
        if course1 in student_courses and course2 in student_courses:
            return True
        
        return False
    
    def get_all_courses_of_student(self, student_id):
        return self.class_list[self.class_list["StudentID"] == student_id]["CourseID"].tolist()
    
    def professor_has_two_exams_at_same_time(self, professor_name, courseID1, courseID2):
        professor_courses = self.get_all_courses_of_professor(professor_name, self.class_list)
        if courseID1 in professor_courses and courseID2 in professor_courses:
            return True
        
        return False
    
    def get_all_courses_of_professor(self, professor_name):
        return self.class_list[self.class_list["Professor Name"] == professor_name]["CourseID"].unique().tolist()

    def get_num_students_take_course(self, courseID):
        return self.class_list[self.class_list["CourseID"] == courseID]["CourseID"].count()


    def first_random_state(self, schedule):
        temp_schedule = copy.deepcopy(schedule)

        for course in self.class_list["CourseID"].unique().tolist():
            random_day = np.random.choice(list(temp_schedule.keys()))
            random_time = np.random.choice(list(temp_schedule[random_day].keys()))
            
            # If same day and time is not empty then try again
            while temp_schedule[random_day][random_time]["course"] != "":
                random_day = np.random.choice(list(temp_schedule.keys()))
                random_time = np.random.choice(list(temp_schedule[random_day].keys()))
            
            # If empty then assign course
            temp_schedule[random_day][random_time]["course"] = course
            # Get exam duration in minutes
            exam_duration = self.class_list[self.class_list["CourseID"] == course]["ExamDuration(in mins)"].unique()[0]
            # Add exam duration to time to get end time
            end_time = pd.to_datetime(random_time, format="%H.%M") + pd.DateOffset(minutes=exam_duration)
            # Assign end time to schedule
            temp_schedule[random_day][random_time]["end time"] = end_time.strftime("%H.%M")

            #print(course, random_day, random_time, end_time.strftime("%H.%M"), "exam duration: ", exam_duration)

        return temp_schedule

    def print_schedule(self, schedule):
        #print(course, random_day, random_time, end_time.strftime("%H.%M"), "exam duration: ", exam_duration)
        for day in schedule:
            for time in schedule[day]:
                if schedule[day][time]["course"] != "":
                    print(schedule[day][time]["course"], day, time, schedule[day][time]["end time"])
