from subprocess import call
from batch.models import Batch
from django.conf import settings

# get the batch list that needs to be processed
batches_to_process = Batch.objects.filter(status=5)

# if there are batches, then copy the files to process location
if batches_to_process.exists():
    for batch in batches_to_process.iterator():
        # construct batch directory
        batch_name = 'batch-' + str(batch.id)
        batch_dir = settings.DATA_FILES_PATH + '/' + batch_name

        # check if directory exists and then copy to "to-process" folder
        if os.path.exists(batch_dir):
            call(["cp", '-R', batch_dir, settings.PROCESS_FILES_PATH])

        # update the batch status to 6 [6 is 'Transformation Completed']
        #batch.status = 6
        batch.save()

