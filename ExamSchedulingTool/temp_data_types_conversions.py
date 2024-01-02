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