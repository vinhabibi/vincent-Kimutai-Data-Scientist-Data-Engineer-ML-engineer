"""
SCT213-C002-0053/2023 - KIMUTAI VINCENT
JKUAT Karen Campus - University Database
DynamoDB Implementation (using moto for local simulation)
"""

import json
import boto3
from moto import mock_aws

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_results(label, items):
    print(f"\n── {label} ──")
    for item in items:
        print(json.dumps(item, indent=2, default=str))

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
@mock_aws
def run():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # ─── TABLE DEFINITIONS ───────────────────
    print_section("1. CREATING TABLES")

    # Campus table
    campus_table = dynamodb.create_table(
        TableName='Campus',
        KeySchema=[{'AttributeName': 'name', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'name', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Campus table created")

    # Department table
    dept_table = dynamodb.create_table(
        TableName='Department',
        KeySchema=[{'AttributeName': 'code', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'code', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Department table created")

    # Course table
    course_table = dynamodb.create_table(
        TableName='Course',
        KeySchema=[{'AttributeName': 'code', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'code', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Course table created")

    # Lecturer table
    lecturer_table = dynamodb.create_table(
        TableName='Lecturer',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Lecturer table created")

    # Student table
    student_table = dynamodb.create_table(
        TableName='Student',
        KeySchema=[{'AttributeName': 'regNo', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'regNo', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Student table created")

    # Enrollment join table (Student-Course relationship)
    enrollment_table = dynamodb.create_table(
        TableName='Enrollment',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},   # studentRegNo#courseCode
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}    # ENROLLMENT
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'},
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Enrollment table created")

    # LecturerCourse join table
    lc_table = dynamodb.create_table(
        TableName='LecturerCourse',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},   # lecturerID#courseCode
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}    # TEACHES
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'},
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ LecturerCourse table created")

    # ─── SEED DATA ───────────────────────────
    print_section("2. INSERTING DATA")

    # Campus
    campus_table.put_item(Item={
        'name': 'JKUAT Karen Campus',
        'location': 'Karen, Nairobi',
        'type': 'Constituent College',
        'departments': ['IT', 'DSA', 'LLB']   # denormalized reference list
    })
    print("✓ Campus inserted")

    # Departments
    departments = [
        {'code': 'IT',  'name': 'Information Technology',  'campusName': 'JKUAT Karen Campus',
         'courses': ['CS301','CS401','CS402','SWE302','IT201','CS202']},
        {'code': 'DSA', 'name': 'Data Science & Analytics', 'campusName': 'JKUAT Karen Campus',
         'courses': ['DSA401','CS201']},
        {'code': 'LLB', 'name': 'Law',                      'campusName': 'JKUAT Karen Campus',
         'courses': []},
    ]
    with dept_table.batch_writer() as batch:
        for d in departments:
            batch.put_item(Item=d)
    print(f"✓ {len(departments)} departments inserted")

    # Courses
    courses = [
        {'code': 'CS301',  'name': 'Database Systems',      'credits': 3, 'year': 3, 'deptCode': 'IT'},
        {'code': 'CS401',  'name': 'NoSQL Databases',        'credits': 3, 'year': 4, 'deptCode': 'IT'},
        {'code': 'CS402',  'name': 'Artificial Intelligence','credits': 3, 'year': 4, 'deptCode': 'IT'},
        {'code': 'SWE302', 'name': 'Software Engineering',   'credits': 3, 'year': 3, 'deptCode': 'IT'},
        {'code': 'DSA401', 'name': 'Machine Learning',       'credits': 3, 'year': 4, 'deptCode': 'DSA'},
        {'code': 'IT201',  'name': 'Computer Networks',      'credits': 3, 'year': 2, 'deptCode': 'IT'},
        {'code': 'CS202',  'name': 'Operating Systems',      'credits': 3, 'year': 2, 'deptCode': 'IT'},
        {'code': 'CS201',  'name': 'Data Structures',        'credits': 3, 'year': 2, 'deptCode': 'DSA'},
    ]
    with course_table.batch_writer() as batch:
        for c in courses:
            batch.put_item(Item=c)
    print(f"✓ {len(courses)} courses inserted")

    # Lecturers
    lecturers = [
        {'id': 'L001', 'name': 'Dr. Mwangi Njoroge', 'rank': 'Associate Professor', 'courses': ['CS301']},
        {'id': 'L002', 'name': 'Dr. Amina Hassan',   'rank': 'Senior Lecturer',     'courses': ['CS401','CS402']},
        {'id': 'L003', 'name': 'Mr. Kevin Ochieng',  'rank': 'Lecturer',            'courses': ['SWE302']},
        {'id': 'L004', 'name': 'Dr. Faith Wambui',   'rank': 'Associate Professor', 'courses': ['DSA401']},
    ]
    with lecturer_table.batch_writer() as batch:
        for l in lecturers:
            batch.put_item(Item=l)
    print(f"✓ {len(lecturers)} lecturers inserted")

    # LecturerCourse relationships
    lc_items = [
        {'PK': 'L001#CS301',  'SK': 'TEACHES', 'lecturerID': 'L001', 'courseCode': 'CS301'},
        {'PK': 'L002#CS401',  'SK': 'TEACHES', 'lecturerID': 'L002', 'courseCode': 'CS401'},
        {'PK': 'L002#CS402',  'SK': 'TEACHES', 'lecturerID': 'L002', 'courseCode': 'CS402'},
        {'PK': 'L003#SWE302', 'SK': 'TEACHES', 'lecturerID': 'L003', 'courseCode': 'SWE302'},
        {'PK': 'L004#DSA401', 'SK': 'TEACHES', 'lecturerID': 'L004', 'courseCode': 'DSA401'},
    ]
    with lc_table.batch_writer() as batch:
        for item in lc_items:
            batch.put_item(Item=item)
    print(f"✓ {len(lc_items)} lecturer-course links inserted")

    # Students
    students = [
        {'regNo': 'SCT221-C001-0001/2023', 'name': 'Brian Kamau',   'year': 3},
        {'regNo': 'SCT221-C002-0010/2023', 'name': 'Aisha Muthoni', 'year': 3},
        {'regNo': 'SCT221-C002-0023/2022', 'name': 'David Otieno',  'year': 4},
        {'regNo': 'SCT213-C002-0001/2022', 'name': 'Grace Wanjiku', 'year': 4},
    ]
    with student_table.batch_writer() as batch:
        for s in students:
            batch.put_item(Item=s)
    print(f"✓ {len(students)} students inserted")

    # Enrollments
    enrollments = [
        {'PK': 'SCT221-C001-0001/2023#CS301',  'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT221-C001-0001/2023', 'courseCode': 'CS301',  'semester': 'Fall 2024'},
        {'PK': 'SCT221-C001-0001/2023#SWE302', 'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT221-C001-0001/2023', 'courseCode': 'SWE302', 'semester': 'Fall 2024'},
        {'PK': 'SCT221-C002-0010/2023#CS301',  'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT221-C002-0010/2023', 'courseCode': 'CS301',  'semester': 'Fall 2024'},
        {'PK': 'SCT221-C002-0010/2023#SWE302', 'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT221-C002-0010/2023', 'courseCode': 'SWE302', 'semester': 'Fall 2024'},
        {'PK': 'SCT221-C002-0023/2022#CS401',  'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT221-C002-0023/2022', 'courseCode': 'CS401',  'semester': 'Fall 2024'},
        {'PK': 'SCT221-C002-0023/2022#CS402',  'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT221-C002-0023/2022', 'courseCode': 'CS402',  'semester': 'Fall 2024'},
        {'PK': 'SCT213-C002-0001/2022#DSA401', 'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT213-C002-0001/2022', 'courseCode': 'DSA401', 'semester': 'Fall 2024'},
        {'PK': 'SCT213-C002-0001/2022#CS402',  'SK': 'ENROLLED_IN', 'studentRegNo': 'SCT213-C002-0001/2022', 'courseCode': 'CS402',  'semester': 'Fall 2024'},
    ]
    with enrollment_table.batch_writer() as batch:
        for e in enrollments:
            batch.put_item(Item=e)
    print(f"✓ {len(enrollments)} enrollments inserted")

    # ─── QUERIES ─────────────────────────────
    print_section("3. QUERY RESULTS")

    # Query 1: Courses offered by IT Department
    print("\n▶ Query 1: Courses offered by IT Department")
    it_dept = dept_table.get_item(Key={'code': 'IT'})['Item']
    it_courses = []
    for code in it_dept['courses']:
        c = course_table.get_item(Key={'code': code})['Item']
        it_courses.append(c)
    it_courses.sort(key=lambda x: (x['year'], x['code']))
    print(f"  Department: {it_dept['name']}")
    for c in it_courses:
        print(f"    [{c['code']}] {c['name']} — Year {c['year']}")

    # Query 2: Students enrolled in CS301
    print("\n▶ Query 2: Students enrolled in CS301 (Database Systems)")
    all_enrollments = enrollment_table.scan()['Items']
    cs301_students = [e for e in all_enrollments if e['courseCode'] == 'CS301']
    course_info = course_table.get_item(Key={'code': 'CS301'})['Item']
    print(f"  Course: {course_info['name']}")
    for e in cs301_students:
        s = student_table.get_item(Key={'regNo': e['studentRegNo']})['Item']
        print(f"    {s['name']} ({s['regNo']})")

    # Query 3: Lecturers and their courses
    print("\n▶ Query 3: Lecturers and their courses")
    all_lecturers = lecturer_table.scan()['Items']
    all_lecturers.sort(key=lambda x: x['name'])
    for l in all_lecturers:
        course_names = []
        for code in l['courses']:
            c = course_table.get_item(Key={'code': code})['Item']
            course_names.append(f"{c['code']} – {c['name']}")
        print(f"  {l['name']} ({l['rank']})")
        for cn in course_names:
            print(f"    → {cn}")

    # Query 4: Campus → Department → Course hierarchy
    print("\n▶ Query 4: Campus structure")
    campus = campus_table.get_item(Key={'name': 'JKUAT Karen Campus'})['Item']
    print(f"  Campus: {campus['name']}")
    for dept_code in campus['departments']:
        dept = dept_table.get_item(Key={'code': dept_code})['Item']
        print(f"    Department: {dept['name']} ({dept['code']})")
        for ccode in dept['courses']:
            c = course_table.get_item(Key={'code': ccode})['Item']
            print(f"      Course: [{c['code']}] {c['name']} (Year {c['year']})")

    # Query 5: Students → their lecturers through courses
    print("\n▶ Query 5: Students and their lecturers (multi-table join)")
    all_students = student_table.scan()['Items']
    all_students.sort(key=lambda x: x['name'])
    all_enrollments = enrollment_table.scan()['Items']
    all_lc = lc_table.scan()['Items']
    all_lec = {l['id']: l for l in lecturer_table.scan()['Items']}

    for student in all_students:
        enrolled = [e for e in all_enrollments if e['studentRegNo'] == student['regNo']]
        print(f"  Student: {student['name']}")
        for e in enrolled:
            course = course_table.get_item(Key={'code': e['courseCode']})['Item']
            teacher_links = [lc for lc in all_lc if lc['courseCode'] == e['courseCode']]
            for tl in teacher_links:
                lec = all_lec[tl['lecturerID']]
                print(f"    [{course['code']}] {course['name']} → {lec['name']} ({lec['rank']})")

    print_section("DONE — All queries completed successfully")

if __name__ == '__main__':
    run()
