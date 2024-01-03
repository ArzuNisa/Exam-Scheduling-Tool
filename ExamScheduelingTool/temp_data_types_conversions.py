import pandas as pd
import numpy as np

class_list = pd.read_csv('class_list.csv')

classroom_capacity_list = pd.read_csv('classroom_capacities.csv')

# Convert the class_list dataframe to a dictionary with the key being the class ID and the value being the class name
# Set the real capacity of each classroom to be half of the capacity
classroom_capacity_dict = classroom_capacity_list.set_index("RoomID")["Capacity"].to_dict()
classroom_real_capacity_dict = classroom_capacity_list.copy()
classroom_real_capacity_dict["Capacity"] = (classroom_capacity_list["Capacity"] / 2).astype(int)


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



# Schedule dictionary with the following structure:
# {day: {time: {course: "", professor: "", room: ""}}}
schedule = {"Monday":{"09.00":{"course":"", "professor":"", "room":""}},
            "Tuesday":{"09.00":{"course":"", "professor":"", "room":""}},
            "Wednesday":{"09.00":{"course":"", "professor":"", "room":""}},
            "Thursday":{"09.00":{"course":"", "professor":"", "room":""}},
            "Friday":{"09.00":{"course":"", "professor":"", "room":""}},
            "Saturday":{"09.00":{"course":"", "professor":"", "room":""}}
            }

# Fill the schedule dictionary with half-hour time slots from 9.00 to 18.00
for day in schedule:
    time = "09.00"
    while time != "18.30":
        schedule[day][time] = {"course": "", "professor": "", "room": ""}
        time = pd.to_datetime(time, format="%H.%M") + pd.DateOffset(minutes=30)
        time = time.strftime("%H.%M")

print("------SCHEDULE-----")
print(schedule)