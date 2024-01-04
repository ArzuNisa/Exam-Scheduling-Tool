import pandas as pd
import numpy as np

class_list = pd.read_csv('class_list.csv')

classroom_capacity_list = pd.read_csv('classroom_capacities.csv')

# Convert the class_list dataframe to a dictionary with the key being the class ID and the value being the class name
# Set the real capacity of each classroom to be half of the capacity
classroom_capacity_dict = classroom_capacity_list.set_index("RoomID")["Capacity"].to_dict()
classroom_real_capacity_dict = classroom_capacity_list.copy()
classroom_real_capacity_dict["Capacity"] = (classroom_capacity_list["Capacity"] / 2).astype(int)
classroom_real_capacity_dict.sort_values(by=['Capacity'], inplace=True, ascending=False)


print(classroom_real_capacity_dict)
print("--------------------")
print(class_list["CourseID"].unique())
print("--------------------")
print(class_list["Professor Name"].unique())
print("--------------------")
print(class_list["CourseID"].value_counts().to_dict())
print("--------------------")

class_list_copy = class_list.copy()
course = np.random.choice(class_list_copy["CourseID"].unique())
print(course)
print("--------------------")

#get number of students in course
num_students = class_list_copy[class_list_copy["CourseID"] == course]["StudentID"].count()

print(num_students)


empty_schedule = {"Monday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Tuesday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Wednesday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Thursday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Friday":{"09.00":{"course":"", "room":"", "end time":""}},
            "Saturday":{"09.00":{"course":"", "room":"", "end time":""}}
            }


for day in empty_schedule:
    time = "09.00"
    while time != "18.30":
        empty_schedule[day][time] = {"course": "", "room": "", "end time":""}
        time = pd.to_datetime(time, format="%H.%M") + pd.DateOffset(minutes=30)
        time = time.strftime("%H.%M")

print(empty_schedule)

def print_schedule(schedule):
    #print(course, random_day, random_time, end_time.strftime("%H.%M"), "exam duration: ", exam_duration)
    for day in schedule:
        for time in schedule[day]:
            if schedule[day][time]["course"] != "":
                print(schedule[day][time]["course"], day, time, schedule[day][time]["end time"])


print_schedule(schedule)
