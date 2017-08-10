from django.contrib import admin
from django.conf import settings
import csv, os

# Register your models here.
from .models import Batch

class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch_date',)

    fieldsets = (
        (None, {
            'fields': ('name', 'batch_date', 'status')
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
            csv_output.writerow(['BARCODE','First Name','Last Name','Father Occupation','Mother Occupation',
                                 'Student Occupation','Current Aspiration','Age','Current Education',
                                 'Contact Number','Batch Code','Gender','Day-1','Day-2','Day-3','Day-4',
                                 'Day-5','Computer Literate','Currently Working','DOB'])

            # skip header as we set custom header
            next(csv_input)

            for row in csv_input:
                # split name field into first name and last name
                name = row[2].split()
                first_name = last_name = ''
                if len(name) > 0:
                    first_name = name[0]
                if len(name) > 1:
                    last_name = name[1]

                # set date of birth
                if row[19] and row[20] and row[21]:
                    dob = row[19] + '/' + row[20] + '/' + row[21]

                # write to csv file
                csv_output.writerow([row[1],first_name,last_name,row[3],row[4],row[5],row[6],row[7],
                                     row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],
                                     row[16],row[17],row[18],dob])

        # update status
        obj.status = 2 # 2 is 'Baseline Processed'

        # set the processed file path
        obj.proc_baseline = 'data/' + batch_name + '/baseline.csv'

        obj.save()

    # method to handle career planning csv transformation
    def process_career_planning(self, request, obj, batch_name, batch_dir):
        # update status
        obj.status = 5
        obj.save()

    # method to handle career awareness csv transformation
    def process_career_awareness(self, request, obj, batch_name, batch_dir):
        # update status
        obj.status = 4
        obj.save()

    # method to handle self awareness csv transformation
    def process_self_awareness(self, request, obj, batch_name, batch_dir):
        # update status
        obj.status = 3
        obj.save()

admin.site.register(Batch, BatchAdmin)