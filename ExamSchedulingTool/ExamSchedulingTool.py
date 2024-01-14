import pandas as pd
import numpy as np
import copy
import random
import math
import os


class ExamSchedulingTool:
    def __init__(self, class_list_file_path='class_list.csv', classroom_capacities_file_path='classroom_capacities.csv'):
        self.class_list, self.classroom_capacity_list = self.read_input_files(class_list_file_path, classroom_capacities_file_path)
    
        self.classroom_real_capacities = None
        self.empty_schedule = None

        self.all_student_numbers = self.class_list["StudentID"].unique().tolist()
        self.all_professor_names = self.class_list["Professor Name"].unique().tolist()

        self.init_classroom_capacities()
        # Constants for classroom capacities
        # Get min of the real capacities
        self.SMALL_CLASSROOM_THRESHOLD = self.classroom_real_capacities["Capacity"].min()
        # Get max of the real capacities
        self.BIG_CLASSROOM_THRESHOLD = self.classroom_real_capacities["Capacity"].max()
        self.init_empty_schedule()
        self.init_blocked_hours()

    def read_input_files(self, class_list_file_path, classroom_capacities_file_path):
        try:
            class_list = pd.read_csv(class_list_file_path)
            classroom_capacity_list = pd.read_csv(classroom_capacities_file_path)
        except:
            print("Required CSV files for Exam scheduler could not be found. Exiting the program...")
            exit(1)
        
        return class_list, classroom_capacity_list

    def init_blocked_hours(self):
        blocked_hours_str = input("Enter blocked hours in the format of\n'course_id Day start_time duration(minutes), course_id Day start_time duration(minutes)...' \n\nExample Usage: TIT101 Monday 09.00 60, TDL101 Wednesday 12.00 90\n\nType 's' to skip this step: ")
        
        if blocked_hours_str == "s":
            print("Skipped")
            return

        blocked_hours = blocked_hours_str.split(",")

        for day_hour in blocked_hours:
            try:
                course_id, day, start_time, duration = day_hour.strip().split(" ")
            except:
                print("Invalid input. Exiting the program...")
                exit(1)

            self.handle_blocked_hours(day, start_time, duration)

            self.empty_schedule[day][start_time]["course"] = f"BLOCKED BY {course_id}"

            end_time = pd.to_datetime(start_time, format="%H.%M") + pd.DateOffset(minutes=int(duration))
            self.empty_schedule[day][start_time]["end time"] =  end_time.strftime("%H.%M")
        
    def handle_blocked_hours(self, day, start_time, duration):
        # Check if the day is valid
            if day not in self.empty_schedule:
                print("Invalid day: ", day, "\nExiting the program...")
                exit(1)

            # Check if the hours is valid
            if start_time not in self.empty_schedule[day]:
                print("Invalid start time: ", start_time, "\nExiting the program...")
                exit(1)

            # Check if the duration is valid
            if not duration.isnumeric():
                print("Invalid duration: ", duration, "\nExiting the program...")
                exit(1)
    
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
        professor_courses = self.get_all_courses_of_professor(professor_name)
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

    def cost(self, schedule, class_list):
        cost = 0


        # Check if a course time is overlapping with another course
        for day in schedule:
            for time in schedule[day]:
                if schedule[day][time]["course"] != "":
                    end_time = schedule[day][time]["end time"]
                    for other_time in schedule[day]:
                        if other_time != time:
                            if schedule[day][other_time]["course"] != "":
                                if pd.to_datetime(time, format="%H.%M") < pd.to_datetime(other_time, format="%H.%M") < pd.to_datetime(end_time, format="%H.%M"):
                                    cost += 1
                                    
        # Check all the students and if a student has more than one exam at the same time on the same day add 1 to cost
        # Also check all the professors and if a professor has more than one exam at the same time on the same day add 1 to cost
        for day in schedule:
            for time in schedule[day]:
                if schedule[day][time]["course"] != "":
                    end_time = schedule[day][time]["end time"]
                    for other_time in schedule[day]:
                        if other_time != time:
                            if schedule[day][other_time]["course"] != "":
                                if pd.to_datetime(time, format="%H.%M") < pd.to_datetime(other_time, format="%H.%M") < pd.to_datetime(end_time, format="%H.%M"):
                                    # Check if a student has more than one exam at the same time on the same day
                                    for student in self.all_student_numbers:
                                        if self.student_has_two_exams_at_same_time(student, schedule[day][time]["course"], schedule[day][other_time]["course"]):
                                            cost += 1
                                    # Check if a professor has more than one exam at the same time on the same day
                                    for professor in self.all_professors_names:
                                        if self.professor_has_two_exams_at_same_time(professor, schedule[day][time]["course"], schedule[day][other_time]["course"]):
                                            cost += 1
        
       


        return cost
                        
    def successor_move(self, old_schedule):
        original_schedule = copy.deepcopy(old_schedule)

        # Get random course to move
        random_course = np.random.choice(self.class_list["CourseID"].unique().tolist())

        # Get random day and time to move course to
        random_day = np.random.choice(list(old_schedule.keys()))
        random_time = np.random.choice(list(old_schedule[random_day].keys()))

        # If same day and time is not empty then try again
        while old_schedule[random_day][random_time]["course"] != "":
            random_day = np.random.choice(list(old_schedule.keys()))
            random_time = np.random.choice(list(old_schedule[random_day].keys()))

        # Find the day and time of the course to move
        for day in old_schedule:
            for time in old_schedule[day]:
                if old_schedule[day][time]["course"] == random_course:
                    course_day = day
                    course_time = time

        # Get exam duration in minutes
        exam_duration = self.class_list[self.class_list["CourseID"] == random_course]["ExamDuration(in mins)"].unique()[0]
        # Add exam duration to time to get end time
        end_time = pd.to_datetime(random_time, format="%H.%M") + pd.DateOffset(minutes=exam_duration)
        # Assign end time to schedule
        old_schedule[random_day][random_time]["end time"] = end_time.strftime("%H.%M")

        # Move course to new day and time
        old_schedule[random_day][random_time]["course"] = random_course
        old_schedule[random_day][random_time]["room"] = ""
        # Remove course from old day and time
        old_schedule[course_day][course_time]["course"] = ""
        old_schedule[course_day][course_time]["room"] = ""
        old_schedule[course_day][course_time]["end time"] = ""
        # Extra: check if there is a collision with other exams
        # If there is a collision, move the other exam to a random empty time
        for day in old_schedule:
            for time in old_schedule[day]:
                if old_schedule[day][time]["course"] != "":
                    end_time = old_schedule[day][time]["end time"]
                    for other_time in old_schedule[day]:
                        if other_time != time:
                            if old_schedule[day][other_time]["course"] != "":
                                if pd.to_datetime(time, format="%H.%M") < pd.to_datetime(other_time, format="%H.%M") < pd.to_datetime(end_time, format="%H.%M"):
                                    # Get random day and time to move other course to
                                    random_day = np.random.choice(list(old_schedule.keys()))
                                    random_time = np.random.choice(list(old_schedule[random_day].keys()))
    
                                    # If same day and time is not empty then try again
                                    while old_schedule[random_day][random_time]["course"] != "":
                                        random_day = np.random.choice(list(old_schedule.keys()))
                                        random_time = np.random.choice(list(old_schedule[random_day].keys()))
    
                                    # Get exam duration in minutes
                                    exam_duration = self.class_list[self.class_list["CourseID"] == old_schedule[day][other_time]["course"]]["ExamDuration(in mins)"].unique()[0]
                                    # Add exam duration to time to get end time
                                    end_time = pd.to_datetime(random_time, format="%H.%M") + pd.DateOffset(minutes=exam_duration)
                                    # Assign end time to schedule
                                    old_schedule[random_day][random_time]["end time"] = end_time.strftime("%H.%M")
    
                                    # Move course to new day and time
                                    old_schedule[random_day][random_time]["course"] = old_schedule[day][other_time]["course"]
                                    old_schedule[random_day][random_time]["room"] = ""
                                    # Remove course from old day and time
                                    old_schedule[day][other_time]["course"] = ""
                                    old_schedule[day][other_time]["room"] = ""
                                    old_schedule[day][other_time]["end time"] = ""
        return original_schedule

    def simulated_annealing_scheduler(self, temp_max, temp_min, cooling_rate, max_iter, K):
        print("\n\nStarting simulated annealing scheduler...\n")

        schedule = self.first_random_state(self.empty_schedule)
        old_cost = self.cost(schedule)
        iter_num = 0
        add_extra_day_iter_threshold = 1000
        flag_day_added = False
        
        temperature = temp_max
        while temperature >= temp_min:
            for i in range(max_iter):
                schedule_before_update = self.successor_move(schedule)
                new_cost = self.cost(schedule)

                if new_cost == 0:
                    total = iter_num + i
                    print(f"Found in {total}. iteration")
                    return schedule
                
                delta = new_cost - old_cost
                if delta >= 0:
                    if random.random() > math.exp(-1.0 * delta / (K * temperature)):
                        schedule = schedule_before_update
                    else:
                        old_cost = new_cost
                else:
                    old_cost = new_cost

            iter_num += max_iter
            temperature *= cooling_rate

            if iter_num % 50 == 0:
                print("Iteration: ", iter_num, "Fault Score: ", old_cost)

            # If could not find a solution with 6 days, add an extra day
            if iter_num > add_extra_day_iter_threshold and not flag_day_added:
                print(f"Could not find a solution with 6 days after {add_extra_day_iter_threshold} iterations. Adding an extra day...")
                flag_day_added = True
                self.add_extra_day(schedule)

    def add_extra_day(self, schedule):
        # Add an extra day named "Sunday"
        schedule["Sunday"] = {"09.00":{"course":"", "room":"", "end time":""}}
        # Add the rest of the times - every 30 minutes
        time = "09.00"
        while time != "18.30":
            schedule["Sunday"][time] = {"course": "", "room": "", "end time":""}
            time = pd.to_datetime(time, format="%H.%M") + pd.DateOffset(minutes=30)
            time = time.strftime("%H.%M")  

    def set_exam_classrooms(self, schedule):
        # Assign classrooms to courses
        for day in schedule:
            for time in schedule[day]:
                if schedule[day][time]["course"] != "":
                    course_id = schedule[day][time]["course"]
                    # Get num of students take the course
                    course_capacity = self.get_num_students_take_course(course_id)
                    
                    # If course capacity is higher than the whole capacity of the classrooms, raise an error
                    if course_capacity > self.classroom_real_capacities["Capacity"].sum():
                        print("Course capacity is higher than the whole capacity of the classrooms. Exiting the program...")
                        exit(1) 
                    
                    # Assign a random small classroom
                    elif 0 < course_capacity <= self.SMALL_CLASSROOM_THRESHOLD:
                        random_small_classroom = np.random.choice(self.classroom_real_capacities[self.classroom_real_capacities["Capacity"] <= self.SMALL_CLASSROOM_THRESHOLD]["RoomID"].tolist())
                        schedule[day][time]["room"] = random_small_classroom

                    # Assign a random big classroom
                    elif self.SMALL_CLASSROOM_THRESHOLD < course_capacity <= self.BIG_CLASSROOM_THRESHOLD:
                        random_big_classroom = np.random.choice(self.classroom_real_capacities[self.classroom_real_capacities["Capacity"] > self.SMALL_CLASSROOM_THRESHOLD]["RoomID"].tolist())
                        schedule[day][time]["room"] = random_big_classroom
       
    def get_first_occured_digit(self, course_name):
            for c in course_name:
                if c.isdigit():
                    return c
                
                if c == " ":
                    return "0"
                
    def show_schedule(self, schedule):
        """
        Prints the schedule to the console in a readable format
        """

        # Get the courses of each year
        first_year_course_schedule = ""
        second_year_course_schedule = ""
        third_year_course_schedule = ""
        fourth_year_course_schedule = ""
        # Get the blocked hours
        blocked_hourse_courses = ""

    
        for day in schedule:
            for time in schedule[day]:
                if schedule[day][time]["course"] != "":
                    # Check the course code and add to the corresponding year
                    # e.g. 1. year courses start with 1
                    # Find the first occured digit in the course code
                    if self.get_first_occured_digit(schedule[day][time]["course"]) == "1":
                        first_year_course_schedule += f" \t {schedule[day][time]['course']} \t | \t {day} \t | \t {time}-{schedule[day][time]['end time']}  \t  | \t {schedule[day][time]['room']}\n"

                    elif self.get_first_occured_digit(schedule[day][time]["course"]) == "2":
                        second_year_course_schedule += f" \t {schedule[day][time]['course']} \t | \t {day} \t | \t {time}-{schedule[day][time]['end time']}  \t  | \t {schedule[day][time]['room']}\n"
                    
                    elif self.get_first_occured_digit(schedule[day][time]["course"]) == "3":
                        third_year_course_schedule += f" \t {schedule[day][time]['course']} \t | \t {day} \t | \t {time}-{schedule[day][time]['end time']}  \t  | \t {schedule[day][time]['room']}\n"
                    
                    elif self.get_first_occured_digit(schedule[day][time]["course"]) == "4":
                        fourth_year_course_schedule += f" \t {schedule[day][time]['course']} \t | \t {day} \t | \t {time}-{schedule[day][time]['end time']}  \t  | \t {schedule[day][time]['room']}\n"

                    # Blocked Hours
                    else:
                        blocked_hourse_courses += f"     {schedule[day][time]['course']} \t | \t {day} \t | \t {time}-{schedule[day][time]['end time']}  \t  | \t\n"

        # Print the schedule to the console in a readable format
        input("\nPress Enter to show the schedule...")
        print("\n\n--------------------------------------------- THE SCHEDULE -------------------------------------------")
        print("\n       Course Code \t | \t   Day \t\t | \t    Time  \t  | \t     Classes")
        print("------------------------------------------------------------------------------------------------------")
        print(first_year_course_schedule, end="")
        print("------------------------------------------------------------------------------------------------------")
        print(second_year_course_schedule, end="")
        print("------------------------------------------------------------------------------------------------------")
        print(third_year_course_schedule, end="")
        print("------------------------------------------------------------------------------------------------------")
        print(fourth_year_course_schedule, end="")
        print("------------------------------------------------------------------------------------------------------")
        print("\n------------------------------------------- BLOCKED HOURS --------------------------------------------")
        print(blocked_hourse_courses, end="")
        print("------------------------------------------------------------------------------------------------------"),




def print_welcome_message():
    os.system('cls||clear')
    print("---------------------------------- WELCOME TO THE EXAM SCHEDULER TOOL --------------------------------\n")


if __name__ == "__main__":
    # Print welcome message
    print_welcome_message()

    # Create the scheduler tool object
    scheduler_tool = ExamSchedulingTool()
    
    # Set the parameters for simulated annealing
    temp_max = 1.0 / 3
    temp_min = 0.0
    cooling_rate = 0.95
    max_iter = 10
    K = 1

    # Start the simulated annealing scheduler
    schedule = scheduler_tool.simulated_annealing_scheduler(temp_max, temp_min, cooling_rate, max_iter, K)
    # Print the schedule to the console in a readable format
    scheduler_tool.show_schedule(schedule)
