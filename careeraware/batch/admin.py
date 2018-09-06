from django.contrib import admin
from django.conf import settings
import csv, os
import logging, datetime

# Register your models here.
from .models import Batch

admin.site.site_header = 'Career Aware: administration'
admin.site.site_title = 'Career Aware: administration'

class BatchAdmin(admin.ModelAdmin):
    # controls what's displayed in the batch listing
    list_display = ('name', 'batch_date', 'status')

    # grouping of fields on the batch form
    fieldsets = (
        (None, {
            'fields': ('name', 'batch_date')
        }),
        ('OMR data', {
            'fields': ('omr_baseline_1', 'omr_baseline_2', 'omr_career_aware', 'omr_career_planning',
                        'omr_self_aware', 'omr_counselling_feedback', 'comment', 'status')
        }),
        ('Transformed data', {
            'classes': ('collapse',),
            'fields': ('proc_baseline_1', 'proc_baseline_2', 'proc_career_aware', 'proc_career_planning',
                        'proc_self_aware', 'proc_counselling_feedback'),
        }),
        ('Errors', {
            'classes': ('collapse',),
            'fields': ('error_log',),
        }),
    )

    # overrite save model to perform additional data transformation
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # check if batch directory exists, else create one
        batch_name = 'batch-' + str(obj.id)
        batch_dir = settings.DATA_FILES_PATH + '/' + batch_name
        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)

        # set log file
        log_file = batch_dir + '/errors.log'
        logging.basicConfig(filename=log_file, level=logging.DEBUG)

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

        # save error log file
        obj.error_log = settings.DATA_FOLDER + '/' + batch_name + '/errors.log'
        obj.save()

    # method to handle baseline 1 csv transformation
    def process_baseline_1(self, request, obj, batch_name, batch_dir):
        # return if baseline 1 is processed
        if obj.status > 1:
            return

        # fetch baseline csv file
        input_file  = obj.omr_baseline_1.path

        # set output file
        output_file = batch_dir + '/baseline_1.csv'

        student_barcodes = []
        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow(['BARCODE', 'First Name', 'Last Name', 'Age', 'Contact Number',
                                 'Gender', 'Currently Working', 'Computer Literate', 'Father Occupation',
                                 'Mother Occupation', 'DOB', 'Contact Type', 'Import Status'])

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
                for i in range(3,10):
                    if i == 6 or i == 7:
                        row_values.append(self.yesno_helper(row[i]))
                    elif i == 5:
                        row_values.append(self.gender_helper(row[i]))
                    else:
                        row_values.append(row[i])

                # calculate date of birth
                dob = ''
                day = row[10]
                if len(day) > 2:
                    day = ''

                month = row[11]
                if len(month) > 2:
                    month = ''

                # make sure date has more than 4 digits
                year = row[12]
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
        if obj.status > 3:
            return

        # fetch baseline 2 csv file
        input_file  = obj.omr_baseline_2.path

        # set output file
        output_file = batch_dir + '/baseline_2.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow(['BARCODE', 'Current Aspiration','Batch Code', 'Current Education',
                                 'Day-1', 'Day-2', 'Day-3', 'Day-4', 'Day-5', 'Import Status'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline 1
                if row[1] not in student_barcodes:
                    logging.debug( 'Missing from Baseline 1: Barcode "' + row[1]
                                   + '" is skipped from baseline 2 CSV.')
                    continue

                row_values = [row[1]]

                # current aspiration 2, 3, 4, 5
                ca_count = 0
                ca = ''
                for i in range(2,6):
                    if row[i]:
                        ca = row[i]
                        ca_count = ca_count + 1

                if ca_count > 1:
                    ca = ''

                row_values.append(ca)

                # process other baseline fields
                for i in range(6,13):
                    if i >= 8 and i <= 12:
                        # process attendance fields
                        # row 8 - 12 format using absentpresent_
                        row_values.append(self.absentpresent_helper(row[i]))
                    elif i == 7:
                        row_values.append(self.currenteducation_helper(row[i]))
                    else:
                        row_values.append(row[i])

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
        if obj.status > 4:
            return

        # fetch career awareness csv file
        input_file  = obj.omr_career_aware.path

        # set output file
        output_file = batch_dir + '/career_awareness.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow(['BARCODE', 'Industry Agnostic', 'Arts and Design', 'Media and Entertainment',
                                 'Finance', 'Healthcare', 'Tourism and Hospitality', 'Retail',
                                 'Wellness and Fitness', 'Education', 'Public Services',
                                 'Environment and Bioscience', 'Trades', 'Import Status'])

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
        if obj.status > 5:
            return

        # fetch career awareness csv file
        input_file  = obj.omr_career_planning.path

        # set output file
        output_file = batch_dir + '/career_planning.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow(['BARCODE', 'Possible Careers 1', 'Possible Careers 2', 'Possible Careers 3', 'CCP 1',
                                 'CCP 2', 'CCP 3', 'Endline', 'Study till 18', 'Import Status'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # skip the record if student is missing in baseline
                if row[1] not in student_barcodes:
                    logging.debug('Missing from Baseline: Barcode "' + row[1] + '" is skipped from career planning CSV.')
                    continue

                row_values = [row[1]]

                # process career planning fields
                # get first, second and third preference
                first_preference = second_preference = third_preference = ''
                for i in range(2,61):
                    if row[i] == '1' or row[i] == '123' or row[i] == '12' or row[i] == '13':
                        if first_preference == '':
                            first_preference = i - 1
                        elif second_preference == '':
                            second_preference = i - 1
                        elif third_preference == '':
                            third_preference  = i - 1
                    elif row[i] == '2' or row[i] == '23':
                        if second_preference == '':
                            second_preference = i - 1
                        elif first_preference == '':
                            first_preference = i - 1
                        elif third_preference == '':
                            third_preference = i - 1
                    elif row[i] == '3':
                        if third_preference == '':
                            third_preference = i - 1
                        elif first_preference == '':
                            first_preference = i - 1
                        elif second_preference == '':
                            second_preference = i - 1

                row_values.extend([first_preference, second_preference, third_preference,
                                   self.singlevalueonly_helper(row[61]), self.singlevalueonly_helper(row[62]),
                                   self.singlevalueonly_helper(row[63])])

                if row[65]:
                    row_values.append(self.validenline_helper(row[65]))
                else:
                    row_values.append(self.validenline_helper(row[64]))

                row_values.append(self.yesno_helper(row[66]))

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
        if obj.status > 6:
            return

        # fetch self awareness csv file
        input_file  = obj.omr_self_aware.path

        # set output file
        output_file = batch_dir + '/self_awareness.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # # set custom header
            csv_output.writerow(['BARCODE', 'Interest Test 1', 'Interest Test 2', 'Interest Test 3', 'Interest Test 4',
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
                                 'Reality Test (Family) 3', 'Reality Test (Family) 4', 'Accelerator', 'Decelerator',
                                 'Import Status'])

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

                # process aptitude fields
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
                # row 102 - 111 format using yesno_helper
                for i in range(102,112):
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
        if obj.status != 7:
            return

        # if file is not uploaded skip it
        if not obj.omr_counselling_feedback:
            return

        # fetch counselling and feedback csv file
        input_file  = obj.omr_counselling_feedback.path

        # set output file
        output_file = batch_dir + '/counselling_and_feedback.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # # set custom header
            csv_output.writerow(['BARCODE', 'Attendance', 'Guardian Attendance', 'I agree with the reccomendation',
                                 'I am clear about what I need to do after class 10',
                                 'Was the Program useful and helpful for you',
                                 'Did you learn something new about yourself',
                                 'Did you learn about some new Careers',
                                 "Was the teacher's way of teaching easy to understand and follow?",
                                 'Did the teacher clear all your doubts?',
                                 'Were you able to understand the workbook easily?',
                                 'Would you recommend the CareerAware program to other students?',
                                 'Import Status'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                row_values = [row[1]]

                # row 2 - 3 format using absentpresent_helper
                for j in range(2, 4):
                    row_values.append(self.absentpresent_helper(row[j]))

                # row 4 - 5 format using yesno_helper
                for i in range(4, 6):
                    row_values.append(self.yesno_helper(row[i]))

                # row 6 - 13
                for j in range(6, 13):
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

admin.site.register(Batch, BatchAdmin)