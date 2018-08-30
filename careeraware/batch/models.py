from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
class Batch(models.Model):

    STATUSES = (
        (1, 'Not Processed'),
        (2, 'Baseline 1 Processed'),
        (3, 'Baseline 2 Processed'),
        (4, 'Career Awareness Processed'),
        (5, 'Career Planning Processed'),
        (6, 'Self Awareness Processed'),
        (7, 'Counselling and Student Feedback Processed'),
        (8, 'Transformation Completed'),
    )

    name = models.CharField(max_length=200)

    batch_date = models.DateField('Date')

    omr_baseline_1 = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Baseline 1',
        default='',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    omr_baseline_2 = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Baseline 2',
        default='',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    omr_self_aware = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Self Awareness',
        default='',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    omr_career_aware = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Career Awareness',
        default='',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    omr_career_planning = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Career Planning',
        default='',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    omr_counselling_feedback = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Counselling and Student Feedback',
        blank=True,
        default='',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    error_log = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Error Log',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['log'], 'Please upload valid log file')],
    )

    comment = models.TextField(
        max_length=200,
        blank=True,
    )

    proc_baseline_1 = models.FileField(
        upload_to='data/',
        verbose_name='Baseline 1',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    proc_baseline_2 = models.FileField(
        upload_to='data/',
        verbose_name='Baseline 2',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    proc_self_aware = models.FileField(
        upload_to='data/',
        verbose_name='Self Awareness',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    proc_career_aware = models.FileField(
        upload_to='data/',
        verbose_name='Career Awareness',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    proc_career_planning = models.FileField(
        upload_to='data/',
        verbose_name='Career Planning',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    proc_counselling_feedback = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Counselling and Student Feedback',
        blank=True,
        help_text='Do not upload. This field will be auto updated.',
        validators=[FileExtensionValidator(['csv'], 'Please upload valid CSV file')],
    )

    status = models.IntegerField(
        choices=STATUSES,
        default=1,
        help_text='Do not change. This field will be auto updated.',
    )

    def __str__(self):
        return self.name
