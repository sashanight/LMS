# Generated by Django 2.1.3 on 2018-12-08 16:00

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms_app', '0004_auto_20181208_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='admission_year',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='student',
            name='degree',
            field=models.CharField(choices=[('BC', 'Bachelor'), ('MR', 'Master'), ('PG', 'Postgraduate')], max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='form_of_study',
            field=models.CharField(choices=[('FT', 'Full-time'), ('EM', 'Extramural'), ('EG', 'Evening')], max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='group',
            field=models.ForeignKey(default=111, on_delete=django.db.models.deletion.CASCADE, to='lms_app.Group'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='learning_base',
            field=models.CharField(choices=[('CT', 'Contract'), ('BG', 'Budget')], max_length=2),
        ),
    ]
