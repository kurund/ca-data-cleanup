from django.contrib import admin
from django.conf import settings
import csv, os
import logging, datetime
from subprocess import call
import time
from django.utils import timezone

# Register your models here.
from .models import Batch

admin.site.site_header = 'Career Aware: administration'
admin.site.site_title = 'Career Aware: administration'

class BatchAdmin(admin.ModelAdmin):
    # controls what's displayed in the batch listing
    list_display = ('name', 'batch_date', 'status', 'created_at', 'modified_at')

    # grouping of fields on the batch form
    fieldsets = (
        (None, {
            'fields': ('name', 'batch_date')
        }),
        ('OMR data', {
            'fields': ('omr_baseline_1', 'omr_baseline_2', 'omr_career_aware', 'omr_career_planning',
                        'omr_self_aware', 'omr_counselling_feedback', 'omr_follow_up_1_data', 'omr_follow_up_2_data', 'comment', 'status')
        }),
        ('Transformed data', {
            'classes': ('collapse',),
            'fields': ('proc_baseline_1', 'proc_baseline_2', 'proc_career_aware', 'proc_career_planning',
                        'proc_self_aware', 'proc_counselling_feedback', 'proc_follow_up_1_data', 'proc_follow_up_2_data'),
        }),
        ('Errors', {
            'classes': ('collapse',),
            'fields': ('error_log',),
        }),
    )

    # overrite save model to perform additional data transformation
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        __original_name = None

        def __init__(self, *args, **kwargs):
            super(Batch, self).__init__(*args, **kwargs)
            self.__original_name = self.name

        # check if batch directory exists, else create one
        batch_name = 'batch-' + str(obj.id)
        batch_dir = settings.DATA_FILES_PATH + '/' + batch_name
        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)

        # set log file
        log_file = batch_dir + '/errors.log'
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        
        initial_status = obj.status

        #process baseline 1 csv
        student_barcodes = self.process_baseline_1(request, obj, batch_name, batch_dir)

        # process baseline 2 csv
        self.process_baseline_2(request, obj, batch_name, batch_dir, student_barcodes)

        # process career awareness csv
        self.process_career_awareness(request, obj, batch_name, batch_dir, student_barcodes)

        # process career planning csv
        self.process_career_planning(request, obj, batch_name, batch_dir, student_barcodes)

        # process self awareness csv
        self.process_self_awareness(request, obj, batch_name, batch_dir, student_barcodes)

        # process counselling and feedback csv
        self.process_counselling_and_feedback(request, obj, batch_name, batch_dir)

        # process follow up 1 csv
        self.process_follow_up_1(request, obj, batch_name, batch_dir)

        # process follow up 2 csv
        self.process_follow_up_2(request, obj, batch_name, batch_dir)

        # save error log file
        # print(obj.status)
        if change == False:
            call(["cp", '-R', batch_dir, settings.PROCESS_FILES_PATH])
        # if (change == True) & (initial_status == 1):
            # call(["cp", '-R', batch_dir, settings.PROCESS_FILES_PATH])

        obj.error_log = settings.DATA_FOLDER + '/' + batch_name + '/errors.log'
        obj.modified_at = timezone.now()
        obj.save()

    # method to handle baseline 1 csv transformation
    def process_baseline_1(self, request, obj, batch_name, batch_dir):
        # return if baseline 1 is processed
        print('process_baseline_1 start')
        if obj.status > 1:
            print('process_baseline_1 return')
            return

        # fetch baseline csv file
        input_file  = obj.omr_baseline_1.path
        print('obj 1:' + str(obj.omr_baseline_1))

        # set output file
        output_file = batch_dir + '/baseline_1.csv'

        student_barcodes = []
        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow([
                'BARCODE', 'First Name', 'Last Name', 'Age', 'Contact Number',
                'Current Education', 'Gender', 'Batch Code', 'Day-1', 'Day-2',
                'Day-3', 'Day-4', 'Day-5', 'DOB', 'Contact Type', 'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline 1
                if row[1] in student_barcodes:
                    logging.debug('Duplicate record skipped in Baseline 1 CSV: Barcode "' + row[1] + '"')
                    continue

                # build student barcode array
                student_barcodes.append(row[1])

                row_values = [row[1]]

                # split name field into first name and last name
                name = row[2].split()
                first_name = last_name = ''
                if len(name) > 0:
                    first_name = name[0]
                if len(name) > 1:
                    last_name = name[1]
                else:
                    last_name = 'Last Name'

                # restrict the characters for first name and last name
                first_name = first_name[:40]
                last_name = last_name[:80]

                row_values.append(first_name)
                row_values.append(last_name)

                # process other baseline fields
                for i in range(3,13):
                    if i >= 8 and i <= 12:
                        # process attendance fields
                        # row 8 - 12 format using absentpresent_
                        row_values.append(self.absentpresent_helper(row[i]))
                    elif i == 5:
                        row_values.append(self.currenteducation_helper(row[i]))
                    elif i == 6:
                        row_values.append(self.gender_helper(row[i]))
                    else:
                        row_values.append(row[i])

                # calculate date of birth
                dob = ''
                day = row[13]
                if len(day) > 2:
                    day = ''

                month = row[14]
                if len(month) > 2:
                    month = ''

                # make sure date has more than 4 digits
                year = row[15]
                if len(year) != 4 or int(year.replace(" ", "")) < 1900:
                    year = ''

                if day and month and year:
                    dob = '/' .join([month,day,year])

                # set blank value to dob for invalid date
                try:
                    datetime.datetime(int(year), int(month), int(day))
                except ValueError:
                    dob = ''

                row_values.append(dob)

                row_values.extend(['Student', 'Baseline 1 Imported'])

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 2 # 2 is 'Baseline 1 Processed'

        # set the processed file path
        obj.proc_baseline_1 = settings.DATA_FOLDER + '/' + batch_name + '/baseline_1.csv'

        obj.save()

        return student_barcodes

    # method to handle baseline 2 csv transformation
    def process_baseline_2(self, request, obj, batch_name, batch_dir, student_barcodes):
        # return if baseline 2 is processed
        print('process_baseline_2 start')

        if obj.status > 3:
            print('process_baseline_2 return')
            return

        if not student_barcodes:
            return

        # fetch baseline 2 csv file
        input_file  = obj.omr_baseline_2.path

        # set output file
        output_file = batch_dir + '/baseline_2.csv'

        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow([
                'BARCODE', 'Father Education', 'Mother Education',
                'Who have you talked to about planning your career',
                'Current Aspiration', 'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline 1
                if row[1] not in student_barcodes:
                    logging.debug('Missing from Baseline 1: Barcode "' + row[1]
                        + '" is skipped from baseline 2 CSV.')
                    continue

                row_values = [row[1]]

                # process baseline 2 fields
                # row 2 and 3 education
                row_values.append(row[2])
                row_values.append(row[3])

                # row 4, career plan
                row_values.append(row[4])

                # current aspiration 5, 6, 7
                ca_count = 0
                ca = ''
                for i in range(5,8):
                    if row[i]:
                        ca = row[i]
                        ca_count = ca_count + 1

                if ca_count > 1:
                    ca = ''

                row_values.append(ca)

                row_values.extend(['Baseline 2 Imported'])

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 3 # 3 is 'Baseline 2 Processed'

        # set the processed file path
        obj.proc_baseline_2 = settings.DATA_FOLDER + '/' + batch_name + '/baseline_2.csv'

        obj.save()

    # method to handle career awareness csv transformation
    def process_career_awareness(self, request, obj, batch_name, batch_dir, student_barcodes):
        # return if career awareness is processed
        print('process_career_awareness start')

        if obj.status > 4:
            print('process_career_awareness return')
            return

        if not student_barcodes:
            return

        # fetch career awareness csv file
        input_file  = obj.omr_career_aware.path

        # set output file
        output_file = batch_dir + '/career_awareness.csv'

        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow([
                'BARCODE', 'Industry Agnostic', 'Arts and Design',
                'Media and Entertainment', 'Finance', 'Healthcare', 'Tourism and Hospitality', 
                'Wellness and Fitness', 'Education', 'Public Services', 'Environment and Bioscience',
                'Information Technology', 'Trades', 'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline
                if row[1] not in student_barcodes:
                    logging.debug( 'Missing from Baseline 1: Barcode "' + row[1]
                        + '" is skipped from career awareness CSV.')
                    continue

                row_values = [row[1]]

                # process career awareness fields
                for i in range(2,14):
                    row_values.append(self.multivalue_formatter(row[i]))

                # add the import status
                row_values.append('Career Awareness Imported')

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 4 # 4 is 'Career Awareness Processed'

        # set the processed file path
        obj.proc_career_aware = settings.DATA_FOLDER + '/' + batch_name + '/career_awareness.csv'

        obj.save()

    # method to handle career planning csv transformation
    def process_career_planning(self, request, obj, batch_name, batch_dir, student_barcodes):
        # return if career planning is processed
        print('process_career_planning start')

        if obj.status > 5:
            print('process_career_planning return')
            return
        
        if not student_barcodes:
            return

        # fetch career awareness csv file
        input_file  = obj.omr_career_planning.path

        # set output file
        output_file = batch_dir + '/career_planning.csv'

        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow([
                'BARCODE', 'Interest 1', 'Interest 2', 'Interest 3', 'Aptitude 1', 'Aptitude 2', 'Aptitude 3',
                'Step 1', 'Step 2', 'Study till 18', 'Possible Careers 1', 'Possible Careers 2', 'Possible Careers 3',
                'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline
                if row[1] not in student_barcodes:
                    logging.debug('Missing from Baseline: Barcode "' + row[1] + '" is skipped from career planning CSV.')
                    continue

                row_values = [row[1]]

                # process career planning fields
                # interest and aptitude fields
                for i in range(2,8):
                    row_values.append(row[i])

                # Step 1 and Step 2 fields
                row_values.append(self.singlevalue_helper(row[8]))
                row_values.append(self.singlevalue_helper(row[9]))

                # study till 18
                row_values.append(self.yesno_helper(row[10]))

                # get first, second and third preference
                first_preference = second_preference = third_preference = ''
                for i in range(11,55):
                    if row[i] == '1' or row[i] == '123' or row[i] == '12' or row[i] == '13':
                        if first_preference == '':
                            first_preference = i
                        elif second_preference == '':
                            second_preference = i
                        elif third_preference == '':
                            third_preference  = i
                    elif row[i] == '2' or row[i] == '23':
                        if second_preference == '':
                            second_preference = i
                        elif first_preference == '':
                            first_preference = i
                        elif third_preference == '':
                            third_preference = i
                    elif row[i] == '3':
                        if third_preference == '':
                            third_preference = i
                        elif first_preference == '':
                            first_preference = i
                        elif second_preference == '':
                            second_preference = i

                row_values.extend([first_preference, second_preference, third_preference])

                # add the import status
                row_values.append('Career Planning Imported')

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 5 # 5 is 'Career Planning Processed'

        # set the processed file path
        obj.proc_career_planning = settings.DATA_FOLDER + '/' + batch_name + '/career_planning.csv'

        obj.save()

    # method to handle self awareness csv transformation
    def process_self_awareness(self, request, obj, batch_name, batch_dir, student_barcodes):
        # return if self awareness is processed
        print('process_self_awareness start')

        if obj.status > 6:
            print('process_self_awareness return')
            return
        if not student_barcodes:
            return

        # fetch self awareness csv file
        input_file  = obj.omr_self_aware.path

        # set output file
        output_file = batch_dir + '/self_awareness.csv'

        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # # set custom header
            csv_output.writerow([
                'BARCODE', 'Interest Test 1', 'Interest Test 2', 'Interest Test 3', 'Interest Test 4',
                'Interest Test 5', 'Interest Test 6', 'Interest Test 7', 'Interest Test 8',
                'Interest Test 9', 'Interest Test 10', 'Interest Test 11', 'Interest Test 12',
                'Interest Test 13', 'Interest Test 14', 'Interest Test 15', 'Interest Test 16',
                'Interest Test 17', 'Interest Test 18', 'Interest Test 19', 'Interest Test 20',
                'Interest Test 21', 'Interest Test 22', 'Interest Test 23', 'Interest Test 24',
                'Interest Test 25', 'Interest Test 26', 'Interest Test 27', 'Interest Test 28',
                'Interest Test 29', 'Interest Test 30', 'Interest Test 31', 'Interest Test 32',
                'Interest Test 33', 'Interest Test 34', 'Interest Test 35', 'Interest Test 36',
                'Interest Test 37', 'Interest Test 38', 'Interest Test 39', 'Interest Test 40',
                'Interest Test 41', 'Interest Test 42', 'Interest Test 43', 'Interest Test 44',
                'Interest Test 45', 'Interest Test 46', 'Interest Test 47', 'Interest Test 48',
                'Aptitude Test (Spatial) 1', 'Aptitude Test (Spatial) 2', 'Aptitude Test (Spatial) 3',
                'Aptitude Test (Spatial) 4', 'Aptitude Test (Spatial) 5', 'Aptitude Test (Spatial) 6',
                'Aptitude Test (Spatial) 7', 'Aptitude Test (Spatial) 8',
                'Aptitude Test (Numerical Ability) 1', 'Aptitude Test (Numerical Ability) 2',
                'Aptitude Test (Numerical Ability) 3', 'Aptitude Test (Numerical Ability) 4',
                'Aptitude Test (Numerical Ability) 5', 'Aptitude Test (Numerical Ability) 6',
                'Aptitude Test (Numerical Ability) 7', 'Aptitude Test (Numerical Ability) 8',
                'Aptitude Test (Mechanical Ability) 1', 'Aptitude Test (Mechanical Ability) 2',
                'Aptitude Test (Mechanical Ability) 3', 'Aptitude Test (Mechanical Ability) 4',
                'Aptitude Test (Mechanical Ability) 5', 'Aptitude Test (Mechanical Ability) 6',
                'Aptitude Test (Mechanical Ability) 7', 'Aptitude Test (Mechanical Ability) 8',
                'Aptitude Test (Abstract Reasoning) 1', 'Aptitude Test (Abstract Reasoning) 2',
                'Aptitude Test (Abstract Reasoning) 3', 'Aptitude Test (Abstract Reasoning) 4',
                'Aptitude Test (Abstract Reasoning) 5', 'Aptitude Test (Abstract Reasoning) 6',
                'Aptitude Test (Abstract Reasoning) 7', 'Aptitude Test (Abstract Reasoning) 8',
                'Aptitude Test (Verbal Attitude Test) 1', 'Aptitude Test (Verbal Attitude Test) 2',
                'Aptitude Test (Verbal Attitude Test) 3', 'Aptitude Test (Verbal Attitude Test) 4',
                'Aptitude Test (Verbal Attitude Test) 5', 'Aptitude Test (Verbal Attitude Test) 6',
                'Aptitude Test (Verbal Attitude Test) 7', 'Aptitude Test (Verbal Attitude Test) 8',
                'Aptitude Test (Creative Ability) 1', 'Aptitude Test (Creative Ability) 2',
                'Aptitude Test (Creative Ability) 3', 'Aptitude Test (Creative Ability) 4',
                'Aptitude Test (Creative Ability) 5', 'Aptitude Test (Creative Ability) 6',
                'Aptitude Test (Creative Ability) 7', 'Aptitude Test (Creative Ability) 8',
                'Personality Test 1', 'Personality Test 2', 'Personality Test 3', 'Personality Test 4',
                'Reality Test (Self) 1', 'Reality Test (Self) 2', 'Reality Test (Self) 3',
                'Reality Test (Self) 4', 'Reality Test (Family) 1', 'Reality Test (Family) 2',
                'Reality Test (Family) 3', 'Reality Test (Family) 4', 'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline
                if row[1] not in student_barcodes:
                    logging.debug('Missing from Baseline: Barcode "' + row[1] + '" is skipped from self awareness CSV.')
                    continue

                row_values = [row[1]]
                # process interest fields
                # row 2 - 49 format using yesno_helper
                for i in range(2,50):
                    row_values.append(self.yesno_helper(row[i]))

                # process aptitude and other fields
                # row 50 - 97
                for j in range(50,98):
                    row_values.append(self.singlevalue_helper(row[j]))

                # process personality fields
                # row 98 - 101
                for j in range(98, 102):
                    if j == 98:
                        row_values.append(self.personality_helper(row[j], 'introvert', 'extrovert'))
                    elif j == 99:
                        row_values.append(self.personality_helper(row[j], 'sensing', 'intuition'))
                    elif j == 100:
                        row_values.append(self.personality_helper(row[j], 'thinking', 'feeling'))
                    elif j == 101:
                        row_values.append(self.personality_helper(row[j], 'judging', 'perceiving'))

                # process reality fields
                # row 102 - 110 format using yesno_helper
                for i in range(102,110):
                    if i == 105 or i == 109:
                        row_values.append(row[i])
                    else:
                        row_values.append(self.yesno_helper(row[i]))

                # add the import status
                row_values.append('Self Awareness Imported')

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 6  # 6 is 'Self Awareness Processed'

        # set the processed file path
        obj.proc_self_aware = settings.DATA_FOLDER + '/' + batch_name + '/self_awareness.csv'

        obj.save()

    # method to handle counselling and feedback csv transformation
    def process_counselling_and_feedback(self, request, obj, batch_name, batch_dir):
        # always process counselling and feedback as this activity will be done later on
        print('process_counselling_and_feedback start')

        if obj.status != 7:
            print('process_counselling_and_feedback return')

            return

        # if file is not uploaded skip it
        if not obj.omr_counselling_feedback:
            return

        # fetch counselling and feedback csv file
        input_file  = obj.omr_counselling_feedback.path

        # set output file
        output_file = batch_dir + '/counselling_and_feedback.csv'

        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # # set custom header
            csv_output.writerow([
                'BARCODE', 'Guardian Attendance', 'I agree with the reccomendation',
                'I am Clear About what I need to do after Class 10',
                'Was the Program useful and helpful for you',
                'Did you learn something new about yourself',
                'Did you learn about some new Careers',
                'Was the teachers way of teaching easy to understand and follow',
                'Did the teacher clear all your doubts?',
                'Were you able to understand the workbook easily?',
                'Would you recommend the Career aware program to other students?',
                'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                row_values = [row[1]]

                # row 2 format using absentpresent_helper
                row_values.append(self.absentpresent_helper(row[2]))

                # row 3 - 12
                for j in range(3, 12):
                    row_values.append(row[j])

                # add the import status
                row_values.append('Import Completed')

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 7  # 7 is 'Counselling and Feedback Processed'
        # obj.status = 8 # 8 is 'Transformation Completed'

        # set the processed file path
        obj.proc_counselling_feedback = settings.DATA_FOLDER + '/' + batch_name + '/counselling_and_feedback.csv'

        obj.save()

    def absentpresent_helper(self, value):
        if value.lower() == 'absentpresent':
            value = 'PRESENT'
        elif value.lower() == 'presentabsent':
            value = 'PRESENT'
        return value

    def yesno_helper(self, value):
        if value.lower() == 'yesno':
            value = 'NO'
        return value

    def singlevalue_helper(self, value):
        option = list(value)
        if len(option) > 1:
            return option[0]
        else:
            return value

    def multivalue_formatter(self, value):
        options = list(value)
        if len(options) > 1:
            return ';'.join(options)
        else:
            return value

    def singlevalueonly_helper(self, value):
        option = list(value)
        if len(option) > 1:
            return ''
        else:
            return value

    def gender_helper(self, value):
        if value.lower() == 'male' or value.lower() == 'female' or value.lower() == 'other':
            return value
        return ''

    def currenteducation_helper(self, value):
        if value.lower() == '8th' or value.lower() == '9th' or value.lower() == '10th' \
            or value.lower() == '11th' or value.lower() == '12th' or value.lower() == 'other':
            return value
        return ''

    def validenline_helper(self, value):
        if not value:
            return value
        elif int(value) > 0 and int(value) < 10:
            return value
        else:
            return ''

    def personality_helper(self, value, expected_value_1, expected_value_2):
        if value.lower() == expected_value_1 or value.lower() == expected_value_2:
            return value
        else:
            return ''

    # method to handle followup 1 csv transformation
    def process_follow_up_1(self, request, obj, batch_name, batch_dir):
        print("process_follow_up_1 start")

        # return if followup 1 is processed
        if obj.status != 8:
            print("process_follow_up_1 return")
            return

        # if file is not uploaded skip it
        if not obj.omr_follow_up_1_data:
            return

        # fetch baseline csv file
        input_file  = obj.omr_follow_up_1_data.path

        # set output file
        output_file = batch_dir + '/follow_up_1.csv'
        print("followup 1 file" + output_file)

        with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow([
                'Bar_Code__c','Followup_1_Baseline_1__c', 'Followup_1_Baseline_2__c',
                'Followup_1_Baseline_3__c', 'Followup_1_Baseline_4__c', 'Followup_1_Baseline_5__c', 
                'Followup_1_Baseline_6__c', 'Followup_1_Baseline_7__c', 'Followup_1_Endline_1__c', 
                'Followup_1_Endline_2__c', 'Followup_1_Endline_3__c', 'Followup_1_Endline_4__c', 'Followup_1_Endline_5__c', 
                'Followup_1_Endline_6__c', 'Followup_1_Endline_7__c', 'Followup_1_Endline_8__c', 'Followup_1_Aspiration__c',
                'Import Status'
                ])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                row_values = [row[1].replace(" ", ""), row[2].upper(), row[3].upper(), row[4].upper(), row[5].upper(), row[6].upper(), row[7].upper(), row[8].upper(), row[9].upper(), row[10].upper(), row[11].upper(), row[12].upper(), 
                    row[13].upper(), row[14].upper(), row[15].upper(), row[16].upper()]

                aspiration = ""
                #populating filds
                for i in range(17, 21):
                    if row[i] != '':
                        aspiration = aspiration + str(row[i]) + ', '
                
                #remove last space and comma
                aspiration = aspiration[:-2]
                #append populated filds
                row_values.append(aspiration)
                #append Import Status
                print("followup 1 imported")
                row_values.append('Followup 1 Imported')
                csv_output.writerow(row_values)

        # update status
        obj.status = 8 # 8 is 'Follow up 1 Data Processed'
        print("followup 1 change status")

        # # set the processed file path
        obj.proc_follow_up_1_data = settings.DATA_FOLDER + '/' + batch_name + '/follow_up_1.csv'

        obj.save()
        print("followup 1 save")

    # method to handle followup 2 csv transformation
    def process_follow_up_2(self, request, obj, batch_name, batch_dir):
            # return if followup 1 is processed    
            print("process_follow_up_2 start")
                    
            if obj.status != 9:
                print("process_follow_up_2 return")
                return
            
            # if file is not uploaded skip it
            if not obj.omr_follow_up_2_data:
                return

            # fetch baseline csv file
            input_file  = obj.omr_follow_up_2_data.path

            # set output file
            output_file = batch_dir + '/follow_up_2.csv'

            with open(input_file, encoding='latin1', newline='\n') as f_input, open(output_file, 'w', encoding='latin1', newline='\n') as f_output:
                csv_input = csv.reader(f_input)
                csv_output = csv.writer(f_output)

                # set custom header
                csv_output.writerow([
                    'Bar_Code__c','Followup_2_Baseline_1__c', 'Followup_2_Baseline_2__c',
                    'Followup_2_Baseline_3__c', 'Followup_2_Baseline_4__c', 'Followup_2_Baseline_5__c', 
                    'Followup_2_Baseline_6__c', 'Followup_2_Baseline_7__c', 'Followup_2_Endline_1__c', 
                    'Followup_2_Endline_2__c', 'Followup_2_Endline_3__c', 'Followup_2_Endline_4__c',
                    'Followup_2_Endline_5__c', 'Followup_2_Endline_6__c', 'Followup_2_Endline_7__c',
                    'Followup_2_Endline_8__c', 'Followup_2_Aspiration__c', 'Import Status'
                    ])

                # skip header as we set custom header
                next(csv_input)

                for row in csv_input:
                    row_values = [row[1].replace(" ", ""), row[2].upper(), row[3].upper(), row[4].upper(), row[5].upper(), row[6].upper(), row[7].upper(), row[8].upper(), row[9].upper(), row[10].upper(), row[11].upper(), row[12].upper(), 
                    row[13].upper(), row[14].upper(), row[15].upper(), row[16].upper()]

                    aspiration = ""
                    #populating fields
                    for i in range(17, 21):
                        if row[i] != '':
                            aspiration = aspiration + str(row[i]) + ', '
                    #remove last space and comma
                    aspiration = aspiration[:-2]
                    row_values.append(aspiration)
                    #Add Import Status
                    row_values.append('Followup 2 Imported')
                    csv_output.writerow(row_values)

            # # update status
            obj.status = 9 # 9 is 'Follow up 2 Data Processed'

            # # set the processed file path
            obj.proc_follow_up_2_data = settings.DATA_FOLDER + '/' + batch_name + '/follow_up_2.csv'

            obj.save()
            # obj.status = 10 # 9 is 'Follow up 2 Data Processed'

admin.site.register(Batch, BatchAdmin)
