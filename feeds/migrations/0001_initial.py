# Generated by Django 3.0.10 on 2020-10-04 13:51

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import feeds.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_celery_beat', '0012_periodictask_expire_seconds'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('title', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Title')),
                ('link', models.URLField(db_index=True, max_length=255, null=True, verbose_name='Link')),
                ('summary', models.TextField(null=True, verbose_name='Summary')),
                ('tag_line', models.TextField(null=True, verbose_name='Tag line')),
                ('url', models.CharField(max_length=512, null=True, verbose_name='Url')),
                ('published', models.DateTimeField(null=True, verbose_name='Publication date')),
                ('modified', models.DateTimeField(null=True, verbose_name='Modification date')),
                ('entries', django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Entries')),
            ],
            options={
                'verbose_name': 'Feed',
                'verbose_name_plural': 'Feeds',
                'ordering': ['-updated_at'],
            },
            bases=(models.Model, feeds.models.RSSMixin),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='Name')),
                ('url', models.URLField(db_index=True, max_length=255, verbose_name='url to the xml feed')),
                ('fetch_status', models.SmallIntegerField(choices=[(0, 'Failed'), (1, 'Done'), (2, 'Pending')], default=1, verbose_name='Fetch status')),
                ('fetch_interval', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_celery_beat.IntervalSchedule')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
            },
            bases=(models.Model, feeds.models.RSSMixin),
        ),
        migrations.CreateModel(
            name='FeedEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.BooleanField(default=False, verbose_name='Has been read')),
                ('title', models.CharField(max_length=255, null=True, verbose_name='Title')),
                ('link', models.CharField(max_length=255, null=True, verbose_name='Link')),
                ('summary', models.TextField(null=True, verbose_name='Summary')),
                ('url', models.CharField(max_length=512, null=True, verbose_name='Url')),
                ('published', models.DateTimeField(null=True, verbose_name='Publication date')),
                ('modified', models.DateTimeField(null=True, verbose_name='Modification date')),
                ('author', models.TextField(max_length=255, null=True, verbose_name='Author')),
                ('copyright', models.TextField(max_length=255, null=True, verbose_name='Copyright')),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feeds.Feed')),
            ],
            options={
                'verbose_name': 'Feed entry',
                'verbose_name_plural': 'Feed entries',
            },
        ),
        migrations.AddField(
            model_name='feed',
            name='source',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='feeds.Source'),
        ),
    ]
