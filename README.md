# Exam Scheduling Tool

This exam scheduler was made for our department. It works for all kinds of scenarios, as long as the CSV files indicating the list of exams that students will take and the capacities of the classes are provided in a proper format. You can change the parameters of the algorithm within the main function.

## Team Members
- <a href="https://github.com/ArzuNisa" target="_blank">Arzu Nisa Yalcınkaya</a>
- <a href="https://github.com/haticeakkus" target="_blank">Hatice Akkuş</a>
- <a href="https://github.com/nazifebutun" target="_blank">Nazife Bütün</a>
- <a href="https://github.com/sertaci" target="_blank">Sertac İnce</a>

## Installation
```
pip install "numpy>=1.26.3" "pandas>=2.1.4"
```
OR
```
pip install -r requirements.txt
```
---
## Usage
```
python ExamSchedulingTool.py
```
---

## EXAMPLE OUTPUT:

![startingScheduler](https://github.com/ArzuNisa/Exam-Scheduling-Tool/assets/111875259/91c09e8c-047c-492b-a77b-d194e66c61cd)

![exampleBaseOutput](https://github.com/ArzuNisa/Exam-Scheduling-Tool/assets/111875259/1607334b-13c2-48ce-8ab3-31d8e04c27f9)

---
## EXAMPLE CSV FILES

For student_exam_list.csv (order is not important):

| StudentID | Professor Name | CourseID | ExamDuration(in mins) |
| ------------- | ------------- | ------------- | ------------- |
| ... | ... | ... | ... |
| 1001 | Muhammed Fatih Demirci | CENG101 | 60 |
| ... | ... | ... | ... |
| 4015 | Fadi Yılmaz | CENG405 | 90 |
| ... | ... | ... | ... |

<br />
For classroom_and_capacities.csv:

| RoomID | Capacity |
| ------------- | ------------- |
| ... | ... |
| C111 | 120 |
| ... | ... |
| C507 | 80 |
| ... | ... |

---
## Behaviors in some abnormal situations:

### Case 1 - Could not find a proper place after 1000 iterations (This parameter can be changed at main function ):
![extraDayAddedInfo](https://github.com/ArzuNisa/Exam-Scheduling-Tool/assets/111875259/87042e7c-145d-46ab-9e8f-08eed08a055f)

Here it added sunday and rescheduled:
![extraDayAddedSchedule](https://github.com/ArzuNisa/Exam-Scheduling-Tool/assets/111875259/330330f2-e26e-4d56-b0fc-6dd1a14b3531)

---
### Case 2 - Not enough classroom capacity:
![notEnoughClassroom](https://github.com/ArzuNisa/Exam-Scheduling-Tool/assets/111875259/029ad191-2c2f-4735-b564-3f4ad1a5edb6)



