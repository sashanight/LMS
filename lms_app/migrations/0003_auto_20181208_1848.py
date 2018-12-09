# Generated by Django 2.1.3 on 2018-12-08 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms_app', '0002_auto_20181208_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='admission_year',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='degree',
            field=models.CharField(blank=True, choices=[('BC', 'Bachelor'), ('MR', 'Master'), ('PG', 'Postgraduate')], max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='form_of_study',
            field=models.CharField(blank=True, choices=[('FT', 'Full-time'), ('EM', 'Extramural'), ('EG', 'Evening')], max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='group',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='lms_app.Group'),
        ),
        migrations.AlterField(
            model_name='student',
            name='learning_base',
            field=models.CharField(blank=True, choices=[('CT', 'Contract'), ('BG', 'Budget')], max_length=2),
        ),
    ]
