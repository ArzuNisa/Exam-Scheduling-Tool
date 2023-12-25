import csv

class Program:
    def __init__(self):
       pass

    def read_csv(self, file_path):
        # Function to read CSV files
        data = []
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row
            for row in reader:
                data.append(row)
        return data
  
def main():
    student_list_data = Program().read_csv('student_list.csv')
    for i in student_list_data:
        print(i)
    classroom_capacities_data = Program().read_csv('classroom_capacities.csv')
    for i in classroom_capacities_data:
        print(i)


if __name__ == "__main__":
    main()
