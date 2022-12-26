# Generated by Django 4.1.4 on 2022-12-26 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0023_linkvisit_remove_tokensummary_token_count_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linkvisit',
            name='user_id',
        ),
        migrations.AlterField(
            model_name='linkvisit',
            name='count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='linkvisit',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='linkvisit',
            name='link_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='linkvisit',
            name='month',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='linkvisit',
            name='year',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]