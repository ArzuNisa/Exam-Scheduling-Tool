import pandas as pd
import numpy as np
import copy
import random
import math


class ExamSchedulingTool:
    def __init__(self, class_list_file_path='class_list.csv', classroom_capacities_file_path='classroom_capacities.csv'):
        self.class_list, self.classroom_capacity_list = self.read_input_files(class_list_file_path, classroom_capacities_file_path)
    
        self.classroom_real_capacities = None
        self.empty_schedule = None

        self.all_student_numbers = self.class_list["StudentID"].unique().tolist()
        self.all_professor_names = self.class_list["Professor Name"].unique().tolist()

        self.init_classroom_capacities()
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

    def cost(schedule, class_list):
        cost = 0
    
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
                                    for student in all_student_numbers:
                                        if student_has_two_exams_at_same_time(student, schedule[day][time]["course"], schedule[day][other_time]["course"], class_list):
                                            cost += 1
                                    # Check if a professor has more than one exam at the same time on the same day
                                    for professor in all_professors:
                                        if professor_has_two_exams_at_same_time(professor, schedule[day][time]["course"], schedule[day][other_time]["course"], class_list):
                                            cost += 1
        
        # If cost is 0 (exams placed properly), try to fit course exams that has collision with other exams to empty classrooms
        # After trying to place them, if there is not enough empty classrooms, add 1 to cost
        # Exams can be placed more than one empty classroom according to their student numbers
        if cost == 0:
            for day in schedule:
                for time in schedule[day]:
                    if schedule[day][time]["course"] != "":
                        end_time_course1 = schedule[day][time]["end time"]
                        
                        # If classroom free time has passed, make it free
                        for i in range(len(classroom_real_capacity_dict)):
                            if pd.to_datetime(time, format="%H.%M") >= pd.to_datetime(classroom_real_capacity_dict.iloc[i, 3], format="%H.%M"):
                                classroom_real_capacity_dict.iloc[i, 2] = False
                        
                        num_students_course1 = get_num_students_take_course(schedule[day][time]["course"], class_list)
                        # Place course to classrooms
                        for i in range(len(classroom_real_capacity_dict)):
                            while num_students_course1 > 0:
                                if classroom_real_capacity_dict.iloc[i, 2] == False:
                                    classroom_real_capacity_dict.iloc[i, 2] = True
                                    classroom_real_capacity_dict.iloc[i, 3] = end_time_course1
    
                                    if schedule[day][time]["room"] == "":
                                        schedule[day][time]["room"] = classroom_real_capacity_dict.iloc[i, 0]
                                    else:
                                        schedule[day][time]["room"] += "-" + classroom_real_capacity_dict.iloc[i, 0]
    
                                    num_students_course1 -= classroom_real_capacity_dict.iloc[i, 1]
                                
                                else: 
                                    break
    
                        if num_students_course1 > 0:
                            cost += 1
                            continue
                            
                        for other_time in schedule[day]:
                            if other_time != time:
                                if schedule[day][other_time]["course"] != "":
                                    end_time_course2 = schedule[day][other_time]["end time"]
    
                                    if pd.to_datetime(time, format="%H.%M") < pd.to_datetime(other_time, format="%H.%M") < pd.to_datetime(end_time_course1, format="%H.%M"):
                                        num_students_course2 = get_num_students_take_course(schedule[day][other_time]["course"], class_list)
                                        
                                        for i in range(len(classroom_real_capacity_dict)):
                                            while num_students_course2 > 0:
                                                if classroom_real_capacity_dict.iloc[i, 2] == False:
                                                    classroom_real_capacity_dict.iloc[i, 2] = True
                                                    classroom_real_capacity_dict.iloc[i, 3] = end_time_course2
    
                                                    if schedule[day][other_time]["room"] == "":
                                                        schedule[day][other_time]["room"] = classroom_real_capacity_dict.iloc[i, 0]
                                                    else:
                                                        schedule[day][other_time]["room"] += "-" + classroom_real_capacity_dict.iloc[i, 0]
                                                    num_students_course2 -= classroom_real_capacity_dict.iloc[i, 1]
                                                
                                                else: 
                                                    break
                                            
                                        if num_students_course2 > 0:
                                            cost += 1
                                            break

                                        for i in range(len(classroom_real_capacity_dict)):
                                            if num_students <= classroom_real_capacity_dict.iloc[i, 1]:
                                                if classroom_real_capacity_dict.iloc[i, 2] == False:
                                                    classroom_real_capacity_dict.iloc[i, 2] = True
                                                    schedule[day][other_time]["room"] = classroom_real_capacity_dict.iloc[i, 0]
                                                    break

                                            if i == len(classroom_real_capacity_dict) - 1:
                                                if classroom_real_capacity_dict.iloc[i, 2] == False:
                                                    classroom_real_capacity_dict.iloc[i, 2] = True
                                                    num_students -= classroom_real_capacity_dict.iloc[i, 1]


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

        return original_schedule

    def simulated_annealing_scheduler(self, temp_max, temp_min, cooling_rate, max_iter, K):
        print("\n\nStarting simulated annealing scheduler...\n")

        schedule = self.first_random_state(self.empty_schedule)
        old_cost = self.cost(schedule)
        iter_num = 0
        
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
