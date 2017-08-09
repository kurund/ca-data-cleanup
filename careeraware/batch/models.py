from django.db import models

# Create your models here.
class Batch(models.Model):

    STATUS = (
        (1, 'Not Processed'),
        (2, 'Baseline Processed'),
        (3, 'Self Awareness Processed'),
        (4, 'Career Awareness Processed'),
        (5, 'Career Planning Processed'),
        (6, 'Transformation Completed'),
    )

    name = models.CharField(max_length=200)

    batch_date = models.DateField('Date')


    omr_baseline = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='OMR - Baseline',
    )

    omr_self_aware = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='OMR - Self Awareness',
    )

    omr_career_aware = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='OMR - Career Awareness',
    )

    omr_career_planning = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='OMR - Career Planning',
    )

    comment = models.TextField(
        max_length=200,
        blank=True,
    )

    proc_baseline = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Processed - Baseline',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
    )

    proc_self_aware = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Processed - Self Awareness',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
    )

    proc_career_aware = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Processed - Career Awareness',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
    )

    proc_career_planning = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Processed - Career Planning',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
    )

    status = models.IntegerField(
        choices=STATUS,
        default=1,
        help_text='Do not change. This field will be auto updated.',
    )
