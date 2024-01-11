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



