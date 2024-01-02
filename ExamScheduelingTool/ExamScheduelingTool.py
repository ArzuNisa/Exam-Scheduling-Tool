import csv
from datetime import datetime, timedelta

class Program:
    def __init__(self):
        self.schedule = {}  # Dictionary to store the exam schedule
        self.blocked_hours = {}  # Dictionary to store blocked hours

    def read_csv(self, file_path):
        # Function to read CSV files
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row
            for row in reader:
                data.append(row)
        return data
  
    def user_input_blocked_hours(self):
        # Function to take user input for blocked hours
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        while True:
            day = input("Enter blocked day (Mon, Tue, Wed, Thu, Fri, Sat) or 'q' to quit: ")
            if day.lower() == 'q':
                break
            if day not in days:
                print("Invalid day. Please try again.")
                continue
            time_range = input(f"Enter blocked time range for {day} (e.g., 2:00 PM - 4:00 PM): ")
            if day not in self.blocked_hours:
                self.blocked_hours[day] = []
            self.blocked_hours[day].append(time_range)

    def schedule_exams(self, class_list, classroom_capacities):
        # Greedy Algorithm to schedule exams
        time = datetime.strptime("9:00 AM", "%I:%M %p")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for clss in class_list:
            class_id, professor, course_id, exam_duration = clss
            for day in days:
                if day not in self.blocked_hours or f"{day}" not in self.schedule:
                    self.schedule[f"{day}"] = []

                # Sort classrooms by capacity in descending order
                sorted_classrooms = sorted(classroom_capacities, key=lambda x: x[1], reverse=True)

                for classroom in sorted_classrooms:
                    room_id, capacity = classroom
                    if int(capacity) >= int(exam_duration) / 2 and (room_id not in self.schedule[f"{day}"]):
                        self.schedule[f"{day}"].append({
                            'time': time.strftime("%I:%M %p"),
                            'course': f"{course_id} - {professor}",
                            'classroom': f"Room {room_id}"
                        })
                        time += timedelta(minutes=int(exam_duration))
                        break
    
    def print_schedule(self):
        # Function to print the final exam schedule and blocked hours
        print("Exam Schedule:")
        for day, exams in self.schedule.items():
            print(day)
            for exam in exams:
                print(f"{exam['time']} - {exam['course']} - {exam['classroom']}")
        print("\nBlocked Hours:")
        for day, time_ranges in self.blocked_hours.items():
            print(day)
            for time_range in time_ranges:
                print(time_range)                

def main():
    class_list_data = Program().read_csv('class_list.csv')
    for i in class_list_data:
        print(i)
    classroom_capacities_data = Program().read_csv('classroom_capacities.csv')
    for i in classroom_capacities_data:
        print(i)


    exam_program = Program()
    exam_program.user_input_blocked_hours()
    exam_program.schedule_exams(class_list_data, classroom_capacities_data)
    exam_program.print_schedule()

if __name__ == "__main__":
    main()
