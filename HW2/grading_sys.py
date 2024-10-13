# Copyright 2024 Devin Kot-Thompson devinkt@bu.edu

import json
import random
import csv
import re
import os
import pandas as pd
import glob
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

#extracting data from json
student_info = open('student_information.json', mode= 'r')
student_info = json.load(student_info)
number_students = student_info['number']
first_names = student_info['first_names']
last_names = student_info['last_names']
student_id = student_info['student_id']
gpa = student_info['GPA']
status = student_info['status']

#generating random student names and writing to csv
r_first_names = []

for name in range(number_students):
    r_first_names.append(random.choice(first_names))

#print(r_first_names)

with open("student_database.csv", 'w') as student_database:
    writer = csv.writer(student_database)
    writer.writerow(r_first_names)

r_last_names = []

for name in range(number_students):
    r_last_names.append(random.choice(last_names))

#print(r_last_names)

with open("student_database.csv", 'a') as student_database:
    writer = csv.writer(student_database)
    writer.writerow(r_last_names)

#generating random ids
r_student_ids = []
max = student_id['max']
min = student_id['min']
prefix = student_id['prefix']

for id in range(number_students):
    num_part = str(random.randrange(min, max))
    r_student_ids.append(prefix + num_part)

#print(r_student_ids)

with open("student_database.csv", 'a') as student_database:
    writer = csv.writer(student_database)
    writer.writerow(r_student_ids)

#assigning a status
student_status = []
index_of_drops = []
enrolled = status[0][0]
dropped = status[1][0]

k = (int)(enrolled * number_students)

percentage_enrolled = random.sample(range(number_students), k)

for student in range(number_students):
    if(student in percentage_enrolled):
        student_status.append("Enrolled")
    else:
        student_status.append("Dropped")
        index_of_drops.append(student)

with open("student_database.csv", 'a') as student_database:
    writer = csv.writer(student_database)
    writer.writerow(student_status)

#print(student_status)

#assigning GPA
student_gpas = []
distribuition = gpa["dist"]
numbers = re.findall(r'\d+\.?\d*',distribuition)
mean = float(numbers[0])
#print(mean)
stdev = float(numbers[1])
#print(stdev)

for student in range(number_students):
    student_gpas.append(int(random.gauss(mean,stdev)*100)/100)
    if (student_gpas[student] > 4): student_gpas[student] = 4
    if (student_gpas[student] < 1): student_gpas[student] = 1

#print(student_gpas)

with open("student_database.csv", 'a') as student_database:
    writer = csv.writer(student_database)
    writer.writerow(student_gpas)

#putting student csv into dataframes
directory = os.getcwd()
csv_name = "student_database.csv"
path = os.path.join(directory,csv_name)

student_df = pd.read_csv(path, header=None).T

student_df.columns = ['First Name','Last Name', 'ID','Status','GPA']

#print(student_df)

#### Assessments 

#extracting from JSON
assessment_info = open('assessment_information.json', mode= 'r')
assessment_info = json.load(assessment_info)
quiz = assessment_info['quiz']
homework = assessment_info['homework']
exam = assessment_info['exam']
test = assessment_info['test']
laboratory = assessment_info['laboratory']
project = assessment_info['project']
participation = assessment_info['participation']

#homework constants
count = homework['count']
total = homework['total']
per_assignment = total/count
hw_range = homework['range']
min_grade = (hw_range[0]/100) * per_assignment
completes = homework['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = homework['grades']
weight_dist1 = grades[0][0]
weight_dist2 = grades[1][0]
mean_dist1 = grades[0][1]
mean_dist2 = grades[1][1]
std_dist1 = grades[0][2]
std_dist2 = grades[1][2]
pop_dist1 = int(weight_dist1 * number_students)
pop_dist2 = int(weight_dist2 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist2_GPA_df = sorted_GPA_df[0:number_students -pop_dist1]
dist1_GPA_df = sorted_GPA_df[number_students-pop_dist1:number_students]

#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

dist2_dropped_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Dropped']
dist2_enrolled_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Enrolled']

def homework_grader(number):
#homework function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)

    dist2_enrolled_complete_df = dist2_enrolled_df.sample(int(enrolled_comp*(dist2_enrolled_df.shape[0])), random_state=1)
    dist2_dropped_complete_df = dist2_dropped_df.sample(int(dropped_comp*(dist2_dropped_df.shape[0])), random_state=1)

    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])
    dist2_completes = pd.concat([dist2_enrolled_complete_df, dist2_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]
    dist2_not_completes1 = dist2_enrolled_df[~dist2_enrolled_df.isin(dist2_enrolled_complete_df).all(axis=1)]
    dist2_not_completes2 = dist2_dropped_df[~dist2_dropped_df.isin(dist2_dropped_complete_df).all(axis=1)]

    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2, dist2_not_completes1, dist2_not_completes2])

    dist1_hw = []
    dist1_hw_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_hw = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_hw[item] > per_assignment:
                    dist1_hw[item] = per_assignment
                if dist1_hw[item] < min_grade:
                    dist1_hw[item] = min_grade
            dist1_hw_dict[f'{student}'] = dist1_hw
            break


    homework_dict_df1 = pd.DataFrame(dist1_hw_dict).T


    dist2_hw = []
    dist2_hw_dict = {}
    for student in dist2_completes['ID']:
        while True:
            dist2_hw = [int((random.gauss((mean_dist2/100)*per_assignment), (std_dist2/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist2_hw[item] > per_assignment:
                    dist2_hw[item] = per_assignment
                if dist2_hw[item] < min_grade:
                    dist2_hw[item] = min_grade
            dist2_hw_dict[f'{student}'] = dist2_hw
            break



    homework_dict_df2 = pd.DataFrame(dist2_hw_dict).T


    not_completes_hw_dict = {}
    for student in not_completes['ID']:
        not_completes_hw_dict[f'{student}'] = [-1]

    not_complete_hw_df = pd.DataFrame(not_completes_hw_dict).T


    homework_df = pd.concat([homework_dict_df1,homework_dict_df2,not_complete_hw_df])
    homework_df.columns = [f'Homework {number}']

    homework_df.to_csv(f'homework{number}grades.csv', index=True)

homework_grader(1)
homework_grader(2)
homework_grader(3)
homework_grader(4)
homework_grader(5)

#test constants
count = test['count']
total = test['total']
per_assignment = total/count
test_range = test['range']
min_grade = (test_range[0]/100) * per_assignment
completes = test['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = test['grades']
weight_dist1 = grades[0][0]
weight_dist2 = grades[1][0]
mean_dist1 = grades[0][1]
mean_dist2 = grades[1][1]
std_dist1 = grades[0][2]
std_dist2 = grades[1][2]
pop_dist1 = int(weight_dist1 * number_students)
pop_dist2 = int(weight_dist2 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist1_GPA_df = sorted_GPA_df[0:number_students -pop_dist2]
dist2_GPA_df = sorted_GPA_df[number_students-pop_dist2:number_students]

#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

dist2_dropped_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Dropped']
dist2_enrolled_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Enrolled']

def test_grader(number):
#test function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)

    dist2_enrolled_complete_df = dist2_enrolled_df.sample(int(enrolled_comp*(dist2_enrolled_df.shape[0])), random_state=1)
    dist2_dropped_complete_df = dist2_dropped_df.sample(int(dropped_comp*(dist2_dropped_df.shape[0])), random_state=1)

    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])
    dist2_completes = pd.concat([dist2_enrolled_complete_df, dist2_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]
    dist2_not_completes1 = dist2_enrolled_df[~dist2_enrolled_df.isin(dist2_enrolled_complete_df).all(axis=1)]
    dist2_not_completes2 = dist2_dropped_df[~dist2_dropped_df.isin(dist2_dropped_complete_df).all(axis=1)]

    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2, dist2_not_completes1, dist2_not_completes2])

    dist1_test = []
    dist1_test_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_test = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_test[item] > per_assignment:
                    dist1_test[item] = per_assignment
                if dist1_test[item] < min_grade:
                    dist1_test[item] = min_grade
            dist1_test_dict[f'{student}'] = dist1_test
            break


    test_dict_df1 = pd.DataFrame(dist1_test_dict).T


    dist2_test = []
    dist2_test_dict = {}
    for student in dist2_completes['ID']:
        while True:
            dist2_test = [int((random.gauss((mean_dist2/100)*per_assignment), (std_dist2/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist2_test[item] > per_assignment:
                    dist2_test[item] = per_assignment
                if dist2_test[item] < min_grade:
                    dist2_test[item] = min_grade
            dist2_test_dict[f'{student}'] = dist2_test
            break



    test_dict_df2 = pd.DataFrame(dist2_test_dict).T


    not_completes_test_dict = {}
    for student in not_completes['ID']:
        not_completes_test_dict[f'{student}'] = [-1]

    not_complete_test_df = pd.DataFrame(not_completes_test_dict).T


    test_df = pd.concat([test_dict_df1,test_dict_df2,not_complete_test_df])
    test_df.columns = [f'Test {number}']

    test_df.to_csv(f'Test{number}grades.csv', index=True)

test_grader(1)
test_grader(2)

#quiz constants
count = quiz['count']
total = quiz['total']
per_assignment = total/count
quiz_range = quiz['range']
min_grade = (quiz_range[0]/100) * per_assignment
completes = quiz['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = quiz['grades']
weight_dist1 = grades[0][0]
mean_dist1 = grades[0][1]
std_dist1 = grades[0][2]
pop_dist1 = int(weight_dist1 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist1_GPA_df = sorted_GPA_df[0:number_students]

#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

def quiz_grader(number):
#homework function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)


    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]

    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2])

    dist1_quiz = []
    dist1_quiz_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_quiz = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_quiz[item] > per_assignment:
                    dist1_quiz[item] = per_assignment
                if dist1_quiz[item] < min_grade:
                    dist1_quiz[item] = min_grade
            dist1_quiz_dict[f'{student}'] = dist1_quiz
            break


    quiz_dict_df1 = pd.DataFrame(dist1_quiz_dict).T



    not_completes_quiz_dict = {}
    for student in not_completes['ID']:
        not_completes_quiz_dict[f'{student}'] = [-1]

    not_complete_quiz_df = pd.DataFrame(not_completes_quiz_dict).T


    quiz_df = pd.concat([quiz_dict_df1,not_complete_quiz_df])
    quiz_df.columns = [f'Quiz {number}']

    quiz_df.to_csv(f'quiz{number}grades.csv', index=True)

for num in range(count):
    quiz_grader(num+1)

#exam constants
count = exam['count']
total = exam['total']
assignment1 = total[0]
assignment2 = total[1]
assignment3 = total[2]
exam_range = exam['range']
min_grade1 = (exam_range[0]/100) * assignment1
min_grade2 = (exam_range[0]/100) * assignment2
min_grade3 = (exam_range[0]/100) * assignment3
completes = exam['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = exam['grades']
weight_dist1 = grades[0][0]
weight_dist2 = grades[1][0]
weight_dist3 = grades[2][0]
mean_dist1 = grades[0][1]
mean_dist2 = grades[1][1]
mean_dist3 = grades[2][1]
std_dist1 = grades[0][2]
std_dist2 = grades[1][2]
std_dist3 = grades[2][2]
pop_dist1 = int(weight_dist1 * number_students)
pop_dist2 = int(weight_dist2 * number_students)
pop_dist3 = int(weight_dist3 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist3_GPA_df = sorted_GPA_df[0:number_students -pop_dist2-pop_dist3]
dist1_GPA_df = sorted_GPA_df[number_students-pop_dist2-pop_dist3:number_students-pop_dist2]
dist2_GPA_df = sorted_GPA_df[number_students-pop_dist2:number_students]
#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

dist2_dropped_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Dropped']
dist2_enrolled_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Enrolled']

dist3_dropped_df = dist3_GPA_df[dist3_GPA_df['Status'] == 'Dropped']
dist3_enrolled_df = dist3_GPA_df[dist3_GPA_df['Status'] == 'Enrolled']

def exam_grader(number, per_assignment, min_grade):
#exam function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)

    dist2_enrolled_complete_df = dist2_enrolled_df.sample(int(enrolled_comp*(dist2_enrolled_df.shape[0])), random_state=1)
    dist2_dropped_complete_df = dist2_dropped_df.sample(int(dropped_comp*(dist2_dropped_df.shape[0])), random_state=1)

    dist3_enrolled_complete_df = dist3_enrolled_df.sample(int(enrolled_comp*(dist3_enrolled_df.shape[0])), random_state=1)
    dist3_dropped_complete_df = dist3_dropped_df.sample(int(dropped_comp*(dist3_dropped_df.shape[0])), random_state=1)

    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])
    dist2_completes = pd.concat([dist2_enrolled_complete_df, dist2_dropped_complete_df])
    dist3_completes = pd.concat([dist3_enrolled_complete_df, dist3_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]
    dist2_not_completes1 = dist2_enrolled_df[~dist2_enrolled_df.isin(dist2_enrolled_complete_df).all(axis=1)]
    dist2_not_completes2 = dist2_dropped_df[~dist2_dropped_df.isin(dist2_dropped_complete_df).all(axis=1)]
    dist3_not_completes1 = dist3_enrolled_df[~dist3_enrolled_df.isin(dist3_enrolled_complete_df).all(axis=1)]
    dist3_not_completes2 = dist3_dropped_df[~dist3_dropped_df.isin(dist3_dropped_complete_df).all(axis=1)]


    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2, dist2_not_completes1, dist2_not_completes2, dist3_not_completes1, dist3_not_completes2])

    dist1_exam = []
    dist1_exam_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_exam = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_exam[item] > per_assignment:
                    dist1_exam[item] = per_assignment
                if dist1_exam[item] < min_grade:
                    dist1_exam[item] = min_grade
            dist1_exam_dict[f'{student}'] = dist1_exam
            break


    exam_dict_df1 = pd.DataFrame(dist1_exam_dict).T


    dist2_exam = []
    dist2_exam_dict = {}
    for student in dist2_completes['ID']:
        while True:
            dist2_exam = [int((random.gauss((mean_dist2/100)*per_assignment), (std_dist2/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist2_exam[item] > per_assignment:
                    dist2_exam[item] = per_assignment
                if dist2_exam[item] < min_grade:
                    dist2_exam[item] = min_grade
            dist2_exam_dict[f'{student}'] = dist2_exam
            break



    exam_dict_df2 = pd.DataFrame(dist2_exam_dict).T

    dist3_exam = []
    dist3_exam_dict = {}
    for student in dist3_completes['ID']:
        while True:
            dist3_exam = [int((random.gauss((mean_dist3/100)*per_assignment), (std_dist3/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist3_exam[item] > per_assignment:
                    dist3_exam[item] = per_assignment
                if dist3_exam[item] < min_grade:
                    dist3_exam[item] = min_grade
            dist3_exam_dict[f'{student}'] = dist3_exam
            break



    exam_dict_df3 = pd.DataFrame(dist3_exam_dict).T


    not_completes_exam_dict = {}
    for student in not_completes['ID']:
        not_completes_exam_dict[f'{student}'] = [-1]

    not_complete_exam_df = pd.DataFrame(not_completes_exam_dict).T


    exam_df = pd.concat([exam_dict_df1,exam_dict_df2, exam_dict_df3, not_complete_exam_df])
    exam_df.columns = [f'Exam {number}']

    exam_df.to_csv(f'Exam{number}grades.csv', index=True)

exam_grader(1, assignment1, min_grade1)
exam_grader(2, assignment2, min_grade2)
exam_grader(3, assignment3, min_grade3)

#laboratory constants
count = laboratory['count']
total = laboratory['total']
per_assignment = total/count
lab_range = laboratory['range']
min_grade = (lab_range[0]/100) * per_assignment
completes = laboratory['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = laboratory['grades']
weight_dist1 = grades[0][0]
weight_dist2 = grades[1][0]
mean_dist1 = grades[0][1]
mean_dist2 = grades[1][1]
std_dist1 = grades[0][2]
std_dist2 = grades[1][2]
pop_dist1 = int(weight_dist1 * number_students)
pop_dist2 = int(weight_dist2 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist2_GPA_df = sorted_GPA_df[0:number_students -pop_dist1]
dist1_GPA_df = sorted_GPA_df[number_students-pop_dist1:number_students]

#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

dist2_dropped_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Dropped']
dist2_enrolled_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Enrolled']

def laboratory_grader(number):
#laboratory function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)

    dist2_enrolled_complete_df = dist2_enrolled_df.sample(int(enrolled_comp*(dist2_enrolled_df.shape[0])), random_state=1)
    dist2_dropped_complete_df = dist2_dropped_df.sample(int(dropped_comp*(dist2_dropped_df.shape[0])), random_state=1)

    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])
    dist2_completes = pd.concat([dist2_enrolled_complete_df, dist2_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]
    dist2_not_completes1 = dist2_enrolled_df[~dist2_enrolled_df.isin(dist2_enrolled_complete_df).all(axis=1)]
    dist2_not_completes2 = dist2_dropped_df[~dist2_dropped_df.isin(dist2_dropped_complete_df).all(axis=1)]

    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2, dist2_not_completes1, dist2_not_completes2])

    dist1_lab = []
    dist1_lab_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_lab = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_lab[item] > per_assignment:
                    dist1_lab[item] = per_assignment
                if dist1_lab[item] < min_grade:
                    dist1_lab[item] = min_grade
            dist1_lab_dict[f'{student}'] = dist1_lab
            break


    laboratory_dict_df1 = pd.DataFrame(dist1_lab_dict).T


    dist2_lab = []
    dist2_lab_dict = {}
    for student in dist2_completes['ID']:
        while True:
            dist2_lab = [int((random.gauss((mean_dist2/100)*per_assignment), (std_dist2/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist2_lab[item] > per_assignment:
                    dist2_lab[item] = per_assignment
                if dist2_lab[item] < min_grade:
                    dist2_lab[item] = min_grade
            dist2_lab_dict[f'{student}'] = dist2_lab
            break



    laboratory_dict_df2 = pd.DataFrame(dist2_lab_dict).T


    not_completes_lab_dict = {}
    for student in not_completes['ID']:
        not_completes_lab_dict[f'{student}'] = [-1]

    not_complete_lab_df = pd.DataFrame(not_completes_lab_dict).T


    laboratory_df = pd.concat([laboratory_dict_df1,laboratory_dict_df2,not_complete_lab_df])
    laboratory_df.columns = [f'Laboratory {number}']

    laboratory_df.to_csv(f'Laboratory{number}grades.csv', index=True)

for num in range(count):
    laboratory_grader(num+1)

#project constants
count = project['count']
total = project['total']
per_assignment = total/count
proj_range = project['range']
min_grade = (proj_range[0]/100) * per_assignment
completes = project['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = project['grades']
weight_dist1 = grades[0][0]
weight_dist2 = grades[1][0]
mean_dist1 = grades[0][1]
mean_dist2 = grades[1][1]
std_dist1 = grades[0][2]
std_dist2 = grades[1][2]
pop_dist1 = int(weight_dist1 * number_students)
pop_dist2 = int(weight_dist2 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist1_GPA_df = sorted_GPA_df[0:number_students -pop_dist2]
dist2_GPA_df = sorted_GPA_df[number_students-pop_dist2:number_students]

#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

dist2_dropped_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Dropped']
dist2_enrolled_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Enrolled']

def project_grader(number):
#project function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)

    dist2_enrolled_complete_df = dist2_enrolled_df.sample(int(enrolled_comp*(dist2_enrolled_df.shape[0])), random_state=1)
    dist2_dropped_complete_df = dist2_dropped_df.sample(int(dropped_comp*(dist2_dropped_df.shape[0])), random_state=1)

    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])
    dist2_completes = pd.concat([dist2_enrolled_complete_df, dist2_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]
    dist2_not_completes1 = dist2_enrolled_df[~dist2_enrolled_df.isin(dist2_enrolled_complete_df).all(axis=1)]
    dist2_not_completes2 = dist2_dropped_df[~dist2_dropped_df.isin(dist2_dropped_complete_df).all(axis=1)]

    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2, dist2_not_completes1, dist2_not_completes2])

    dist1_proj = []
    dist1_proj_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_proj = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_proj[item] > per_assignment:
                    dist1_proj[item] = per_assignment
                if dist1_proj[item] < min_grade:
                    dist1_proj[item] = min_grade
            dist1_proj_dict[f'{student}'] = dist1_proj
            break


    project_dict_df1 = pd.DataFrame(dist1_proj_dict).T


    dist2_proj = []
    dist2_proj_dict = {}
    for student in dist2_completes['ID']:
        while True:
            dist2_proj = [int((random.gauss((mean_dist2/100)*per_assignment), (std_dist2/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist2_proj[item] > per_assignment:
                    dist2_proj[item] = per_assignment
                if dist2_proj[item] < min_grade:
                    dist2_proj[item] = min_grade
            dist2_proj_dict[f'{student}'] = dist2_proj
            break



    project_dict_df2 = pd.DataFrame(dist2_proj_dict).T


    not_completes_proj_dict = {}
    for student in not_completes['ID']:
        not_completes_proj_dict[f'{student}'] = [-1]

    not_complete_proj_df = pd.DataFrame(not_completes_proj_dict).T


    project_df = pd.concat([project_dict_df1,project_dict_df2,not_complete_proj_df])
    project_df.columns = [f'Project {number}']

    project_df.to_csv(f'Project{number}grades.csv', index=True)


project_grader(1)


#participation constants
count = participation['count']
total = participation['total']
per_assignment = total/count
part_range = participation['range']
min_grade = (part_range[0]/100) * per_assignment
completes = participation['completes']
enrolled_comp = completes[0]
dropped_comp = completes[1]
grades = participation['grades']
weight_dist1 = grades[0][0]
weight_dist2 = grades[1][0]
mean_dist1 = grades[0][1]
mean_dist2 = grades[1][1]
std_dist1 = grades[0][2]
std_dist2 = grades[1][2]
pop_dist1 = int(weight_dist1 * number_students)
pop_dist2 = int(weight_dist2 * number_students)
sorted_GPA_df = student_df.sort_values(by='GPA')

#selecting the appropriate mixed dist based on GPA
dist1_GPA_df = sorted_GPA_df[0:number_students -pop_dist2]
dist2_GPA_df = sorted_GPA_df[number_students-pop_dist2:number_students]

#getting populations based on completetion weights
dist1_dropped_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Dropped']
dist1_enrolled_df = dist1_GPA_df[dist1_GPA_df['Status'] == 'Enrolled']

dist2_dropped_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Dropped']
dist2_enrolled_df = dist2_GPA_df[dist2_GPA_df['Status'] == 'Enrolled']

def participation_grader(number):
#participation function
    dist1_enrolled_complete_df = dist1_enrolled_df.sample(int(enrolled_comp*(dist1_enrolled_df.shape[0])), random_state=1)
    dist1_dropped_complete_df = dist1_dropped_df.sample(int(dropped_comp*(dist1_dropped_df.shape[0])), random_state=1)

    dist2_enrolled_complete_df = dist2_enrolled_df.sample(int(enrolled_comp*(dist2_enrolled_df.shape[0])), random_state=1)
    dist2_dropped_complete_df = dist2_dropped_df.sample(int(dropped_comp*(dist2_dropped_df.shape[0])), random_state=1)

    dist1_completes = pd.concat([dist1_enrolled_complete_df, dist1_dropped_complete_df])
    dist2_completes = pd.concat([dist2_enrolled_complete_df, dist2_dropped_complete_df])

    #if not completed need to handle excused or not excused
    dist1_not_completes1 = dist1_enrolled_df[~dist1_enrolled_df.isin(dist1_enrolled_complete_df).all(axis=1)]
    dist1_not_completes2 = dist1_dropped_df[~dist1_dropped_df.isin(dist1_dropped_complete_df).all(axis=1)]
    dist2_not_completes1 = dist2_enrolled_df[~dist2_enrolled_df.isin(dist2_enrolled_complete_df).all(axis=1)]
    dist2_not_completes2 = dist2_dropped_df[~dist2_dropped_df.isin(dist2_dropped_complete_df).all(axis=1)]

    not_completes = pd.concat([dist1_not_completes1, dist1_not_completes2, dist2_not_completes1, dist2_not_completes2])

    dist1_part = []
    dist1_part_dict = {}
    for student in dist1_completes['ID']:
        while True:
            dist1_part = [int((random.gauss((mean_dist1/100)*per_assignment), (std_dist1/100)*per_assignment)[0]*100)/100]
            for item in range(1):
                if dist1_part[item] > per_assignment:
                    dist1_part[item] = per_assignment
                if dist1_part[item] < min_grade:
                    dist1_part[item] = min_grade
            dist1_part_dict[f'{student}'] = dist1_part
            break


    participation_dict_df1 = pd.DataFrame(dist1_part_dict).T


    dist2_part = []
    dist2_part_dict = {}
    for student in dist2_completes['ID']:
        while True:
            dist2_part = [int((random.gauss((mean_dist2/100)*per_assignment), (std_dist2/100)*per_assignment)[0]*100)/100]

            for item in range(1):
                if dist2_part[item] > per_assignment:
                    dist2_part[item] = per_assignment
                if dist2_part[item] < min_grade:
                    dist2_part[item] = min_grade
            dist2_part_dict[f'{student}'] = dist2_part
            break



    participation_dict_df2 = pd.DataFrame(dist2_part_dict).T


    not_completes_part_dict = {}
    for student in not_completes['ID']:
        not_completes_part_dict[f'{student}'] = [-1]

    not_complete_part_df = pd.DataFrame(not_completes_part_dict).T


    participation_df = pd.concat([participation_dict_df1,participation_dict_df2,not_complete_part_df])
    participation_df.columns = [f'Participation {number}']

    participation_df.to_csv(f'Participation{number}grades.csv', index=True)

for num in range(count):
    participation_grader(num+1)


#total points possible
total = (quiz['total'] + homework['total'] + exam['total'][0]+ exam['total'][1] + 
         exam['total'][2] + test['total'] + laboratory['total'] + 
         project['total'] + participation['total'])

#master grade dataframe
path = os.getcwd()
print(path)
csv_files = glob.glob(f'{path}/*.csv')
grades_df = [pd.read_csv(file) for file in csv_files if 'student_database.csv' not in file]

grades_df = pd.concat(grades_df, ignore_index=False, axis =1 )
grades_df = grades_df.loc[:, ~grades_df.columns.duplicated()]
grades_df = grades_df.rename(columns = {'Unnamed: 0': 'ID'})
#print(grades_df)


#handling drops and missed assignments

Dropped_IDs = student_df.loc[student_df['Status'] == 'Dropped', 'ID'].tolist()

#dropped students receive withdraws we can just average their missing grades the same it is unimportant
dropped_grades = grades_df['ID'].isin(Dropped_IDs)
grades_df.loc[dropped_grades, ['Grade', 'Letter Grade']] = ['W', 'W']

Gradebook_df = pd.DataFrame(grades_df)


#handle missed assignments
def missed_assignment_handler(row):
    row = grades_df.iloc[row]
    missing_assignment = []
    for key, value in row.items():
        if value == -1:
            missing_assignment.append(key)
    quiz_str = 'Quiz'
    lab_str = 'Laboratory'
    homework_str = 'Homework'
    exam_str = 'Exam'
    test_str = 'Test'
    project_str = 'Project'
    participation_str = 'Participation'

    missing_quizzes = [s for s in missing_assignment if quiz_str in s]
    missing_lab = [s for s in missing_assignment if lab_str in s]
    missing_homework = [s for s in missing_assignment if homework_str in s]
    missing_exam = [s for s in missing_assignment if exam_str in s]
    missing_test = [s for s in missing_assignment if test_str in s]
    missing_project = [s for s in missing_assignment if project_str in s]
    missing_participation = [s for s in missing_assignment if participation_str in s]


    row_quizzes = []
    row_lab = []
    row_homework = []
    row_exam = []
    row_test = []
    row_project = []
    row_participation = []

    def assignment_rows(assignment_str, assignment_list):
        for key, value in row.items():
            if key.startswith(assignment_str):
                assignment_list.append(key)

    assignment_rows('Quiz', row_quizzes)
    assignment_rows('Lab', row_lab)
    assignment_rows('Homework', row_homework)
    assignment_rows('Exam', row_exam)
    assignment_rows('Test', row_test)
    assignment_rows('Project', row_project)
    assignment_rows('Participation', row_participation)

    def avg_grade_missing(assignment_list, missing_assignments, assignment_str):
        completed_assignments = [item for item in assignment_list if item not in missing_assignments]
        total = 0
        if(len(completed_assignments) == 0):
            avg_grade = 0
        else:    
            for key, value in row.items():
                if key in completed_assignments:
                    total += value
            avg_grade = total/len(completed_assignments)

        assignment_columns = Gradebook_df.filter(like=assignment_str).columns  
        Gradebook_df[assignment_columns] = Gradebook_df[assignment_columns].replace(-1.00, avg_grade)

    avg_grade_missing(row_exam, missing_exam, 'Exam')   
    avg_grade_missing(row_quizzes, missing_quizzes, 'Quiz')   
    avg_grade_missing(row_lab, missing_lab, 'Laboratory')   
    avg_grade_missing(row_homework, missing_homework, 'Homework')   
    avg_grade_missing(row_test, missing_test, 'Test')   
    avg_grade_missing(row_project, missing_project, 'Project')   
    avg_grade_missing(row_participation, missing_participation, 'Participation')   

for student in range(number_students):
    missed_assignment_handler(student)


student_grade_100 = (Gradebook_df.select_dtypes(include='number').sum(axis=1)/total)*100

def get_letter_grade(grade):
    if grade > 94:
        return 'A'
    elif grade > 90:
        return 'A-'
    elif grade > 87:
        return 'B+'
    elif grade > 84:
        return 'B'
    elif grade > 80:
        return 'B-'
    elif grade > 77:
        return 'C+'
    elif grade > 74:
        return 'C'
    elif grade > 70:
        return 'C-'
    elif grade > 60:
        return 'D'
    else:
        return 'F'

Gradebook_df['Letter Grade'] = student_grade_100.apply(get_letter_grade)

Gradebook_df['Grade'] = student_grade_100

Gradebook_df.loc[dropped_grades, ['Grade', 'Letter Grade']] = ['W', 'W']

grade_order = {
    'A+': 11, 'A': 10, 'A-': 9,
    'B+': 8, 'B': 7, 'B-': 6,
    'C+': 5, 'C': 4, 'C-': 3,
    'D': 2, 'F': 1
}


reverse_grade_order = {v: k for k, v in grade_order.items()}


filtered_grades = Gradebook_df[Gradebook_df['Letter Grade'] != 'W']['Letter Grade'].map(grade_order)


sorted_grades = filtered_grades.sort_values()


plt.hist(sorted_grades, bins=len(grade_order), edgecolor='black')
plt.xticks(ticks=range(1, len(grade_order) + 1), labels=[reverse_grade_order[i] for i in range(1, len(grade_order) + 1)])
plt.xlabel('Letter Grades')
plt.ylabel('Frequency')
plt.grid()
plt.show()


filtered_grades = Gradebook_df[Gradebook_df['Grade'] != 'W']['Grade']
filtered_IDs = Gradebook_df[Gradebook_df['Grade'] != 'W']['ID']
filtered_GPAs = filtered_IDs.map(student_df.set_index('ID')['GPA'])

sorted_indices = np.argsort(filtered_GPAs.values)
print(sorted_indices)
sorted_GPAs = filtered_GPAs.iloc[sorted_indices]
print(sorted_GPAs)
sorted_grades = filtered_grades.iloc[sorted_indices]
print(sorted_grades)

plt.scatter(sorted_GPAs, sorted_grades)
plt.grid()
plt.xlabel('GPA')
plt.ylabel('Grade')
plt.xticks(rotation=90, fontsize=8) 
plt.show()  