from django.contrib import admin
from django.conf import settings
import csv, os

# Register your models here.
from .models import Batch

class BatchAdmin(admin.ModelAdmin):
    # controls what's displayed in the batch listing
    list_display = ('name', 'batch_date', 'status')

    # grouping of fields on the batch form
    fieldsets = (
        (None, {
            'fields': ('name', 'batch_date')
        }),
        ('OMR data', {
            'fields': ('omr_baseline', 'omr_self_aware', 'omr_career_aware',
                       'omr_career_planning', 'comment')
        }),
        ('Transformed data', {
            'classes': ('collapse',),
            'fields': ('proc_baseline', 'proc_self_aware', 'proc_career_aware',
                       'proc_career_planning', 'status'),
        }),
    )

    # overrite save model to perform additional data transformation
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # check if batch directory exists, else create one
        batch_name = 'batch-' + str(obj.id)
        batch_dir = settings.DATA_FILES + batch_name
        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)

        #process baseline csv
        self.process_baseline(request, obj, batch_name, batch_dir)

        # process self awareness csv
        self.process_self_awareness(request, obj, batch_name, batch_dir)

        # process career awareness csv
        self.process_career_awareness(request, obj, batch_name, batch_dir)

        # process career planning csv
        self.process_career_planning(request, obj, batch_name, batch_dir)

    # method to handle baseline csv transformation
    def process_baseline(self, request, obj, batch_name, batch_dir):
        # return if baseline is processed
        if obj.status > 1:
            return

        # fetch baseline csv file
        input_file  = obj.omr_baseline.path

        # set output file
        output_file = batch_dir + '/baseline.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow(['BARCODE', 'First Name', 'Last Name', 'Father Occupation', 'Mother Occupation',
                                 'Student Occupation', 'Current Aspiration', 'Age', 'Current Education',
                                 'Contact Number', 'Batch Code', 'Gender', 'Day-1', 'Day-2', 'Day-3', 'Day-4',
                                 'Day-5', 'Computer Literate', 'Currently Working', 'DOB'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                row_values = [row[1]]

                # split name field into first name and last name
                name = row[2].split()
                first_name = last_name = ''
                if len(name) > 0:
                    first_name = name[0]
                if len(name) > 1:
                    last_name = name[1]

                row_values.append(first_name)
                row_values.append(last_name)

                # process other baseline fields
                for i in range(3,19):
                    row_values.append(row[i])

                # calculate date of birth
                dob = ''
                if row[19] and row[20] and row[21]:
                    dob = '/' .join([row[19],row[20],row[21]])

                row_values.append(dob)

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 2 # 2 is 'Baseline Processed'

        # set the processed file path
        obj.proc_baseline = 'data/' + batch_name + '/baseline.csv'

        obj.save()

    # method to handle self awareness csv transformation
    def process_self_awareness(self, request, obj, batch_name, batch_dir):
        # return if self awareness is processed
        if obj.status > 2:
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
                                 'Personality Test 1', 'Personality Test 2', 'Personality Test 3', 'Personality Test 4',
                                 'Personality Test 5', 'Personality Test 6', 'Personality Test 7', 'Personality Test 8',
                                 'Personality Test 9', 'Personality Test 10', 'Personality Test 11',
                                 'Personality Test 12',
                                 'Personality Test 13', 'Personality Test 14', 'Personality Test 15',
                                 'Personality Test 16',
                                 'Reality Test (Self) 1', 'Reality Test (Self) 2', 'Reality Test (Self) 3',
                                 'Reality Test (Self) 4', 'Reality Test (Family) 1', 'Reality Test (Family) 2',
                                 'Reality Test (Family) 3', 'Reality Test (Family) 4', 'Accelerator', 'Decelerator'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                row_values = [row[1]]
                # process interest fields
                # row 2 - 49 format using yesno_helper
                for i in range(2,50):
                    row_values.append(self.yesno_helper(row[i]))

                # process aptitude fields
                # row 50 - 91
                for j in range(50,92):
                    row_values.append(self.singlevalue_helper(row[j]))

                # process personality fields
                # row 92 - 107
                for j in range(92, 108):
                    row_values.append(self.agreedisagree_helper(row[j]))

                # process reality fields
                # row 108 - 117 format using yesno_helper
                for i in range(108,118):
                    row_values.append(self.yesno_helper(row[i]))

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 3  # 3 is 'Self Awareness Processed'

        # set the processed file path
        obj.proc_self_aware = 'data/' + batch_name + '/self_awareness.csv'

        obj.save()

    # method to handle career awareness csv transformation
    def process_career_awareness(self, request, obj, batch_name, batch_dir):
        # return if career awareness is processed
        if obj.status > 3:
            return

        # fetch career awareness csv file
        input_file  = obj.omr_career_aware.path

        # set output file
        output_file = batch_dir + '/career_awareness.csv'

        with open(input_file, newline='\n') as f_input, open(output_file, 'w', newline='\n') as f_output:
            csv_input = csv.reader(f_input)
            csv_output = csv.writer(f_output)

            # set custom header
            csv_output.writerow(['BARCODE', 'Design', 'Performance Arts', 'Media & Communication', 'Beauty & Wellness',
                                 'Education', 'Sports & Fitness', 'Finance', 'Hospitality & Tourism','Medical',
                                 'Public Service', 'Engineering Technologies', 'Trades',
                                 'Enviroment and Biological Science'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                row_values = [row[1]]
                # process career awareness fields
                for i in range(2,15):
                    row_values.append(self.multivalue_formatter(row[i]))

                # write to csv file
                csv_output.writerow(row_values)

        # update status
        obj.status = 4 # 4 is 'Career Awareness Processed'

        # set the processed file path
        obj.proc_career_aware = 'data/' + batch_name + '/career_awareness.csv'

        obj.save()

    # method to handle career planning csv transformation
    def process_career_planning(self, request, obj, batch_name, batch_dir):
        # return if career planning is processed
        if obj.status > 4:
            return

        # update status
        #obj.status = 5 # 5 is 'Career Planning Processed'
        obj.status = 6 # 6 is 'Transformation Completed'
        #obj.save()

    def yesno_helper(self, value):
        if value == 'YesNo':
            value = 'No'
        return value

    def singlevalue_helper(self, value):
        option = list(value)
        if len(option) > 1:
            return option[0]
        else:
            return value

    def agreedisagree_helper(self, value):
        if value == 'AgreeDisagree':
            value = 'Disagree'
        return value

    def multivalue_formatter(self, value):
        options = list(value)
        if len(options) > 1:
            return ';'.join(options)
        else:
            return value

admin.site.register(Batch, BatchAdmin)