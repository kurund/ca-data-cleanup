from subprocess import call
from batch.models import Batch
from django.conf import settings
import glob


def copyFiles(batch_dir, newDir, filename):
    from subprocess import call

    if os.path.exists(batch_dir):
        call(["cp", batch_dir + '/' + filename, newDir])
# get the batch list that needs to be processed
# Status: self awareness processed - 6, counselling and feedback - 7
batches_to_process = Batch.objects.filter(status__in=[6,7,8,9])

# if there are batches, then copy the files to process location
if batches_to_process.exists():
    for batch in batches_to_process.iterator():
        print('batch', batch.status)
        # construct batch directory
        batch_name = 'batch-' + str(batch.id)
        batch_dir = settings.DATA_FILES_PATH + '/' + batch_name

        # print(batch_dir)
        print(glob.glob(batch_dir + '/*.csv'))
        newDir = settings.PROCESS_FILES_PATH + '/' + batch_name
        call(["mkdir", newDir])

        if batch.status == 6:
            copyFiles(batch_dir, newDir, 'baseline_1.csv')
            copyFiles(batch_dir, newDir, 'baseline_2.csv')
            copyFiles(batch_dir, newDir, 'career_awareness.csv')
            copyFiles(batch_dir, newDir, 'career_planning.csv')

            copyFiles(batch_dir, newDir, 'self_awareness.csv')
            copyFiles(batch_dir, newDir, 'counselling_and_feedback.csv')
            copyFiles(batch_dir, newDir, 'follow_up_1.csv')
            copyFiles(batch_dir, newDir, 'follow_up_2.csv')

        if batch.status == 7:
            # copyFiles(batch_dir, newDir, 'self_awareness.csv')
            copyFiles(batch_dir, newDir, 'counselling_and_feedback.csv')
            copyFiles(batch_dir, newDir, 'follow_up_1.csv')
            copyFiles(batch_dir, newDir, 'follow_up_2.csv')

        if batch.status == 8:
            # copyFiles(batch_dir, newDir, 'self_awareness.csv')
            # copyFiles(batch_dir, newDir, 'counselling_and_feedback.csv')
            copyFiles(batch_dir, newDir, 'follow_up_1.csv')
            copyFiles(batch_dir, newDir, 'follow_up_2.csv')
            
        if batch.status == 9:
            # copyFiles(batch_dir, newDir, 'self_awareness.csv')
            # copyFiles(batch_dir, newDir, 'counselling_and_feedback.csv')
            # copyFiles(batch_dir, newDir, 'follow_up_1.csv')
            copyFiles(batch_dir, newDir, 'follow_up_2.csv')
 
        
        
        # check if directory exists and then copy to "to-process" folder
        # if os.path.exists(batch_dir):
        #     call(["cp", '-R', batch_dir, settings.PROCESS_FILES_PATH])

        # update the batch status to 10 [10 is 'Transformation Completed']
        batch.status = 10
        batch.save()

