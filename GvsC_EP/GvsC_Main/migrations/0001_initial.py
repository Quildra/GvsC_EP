# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-03 09:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import djangoplugins.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('djangoplugins', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.PositiveSmallIntegerField()),
                ('table_number', models.PositiveSmallIntegerField()),
                ('match_completed', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Seating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.PositiveSmallIntegerField()),
                ('place', models.PositiveSmallIntegerField()),
                ('score', models.PositiveSmallIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('players', models.ManyToManyField(to='GvsC_Main.Player')),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('registration_start', models.TimeField()),
                ('regestration_close', models.TimeField()),
                ('first_round_begins', models.TimeField()),
                ('player_limit', models.PositiveSmallIntegerField()),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SinglePlayerSeating',
            fields=[
                ('seating_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GvsC_Main.Seating')),
                ('player', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='GvsC_Main.Player')),
            ],
            options={
                'abstract': False,
            },
            bases=('GvsC_Main.seating',),
        ),
        migrations.CreateModel(
            name='SinglePlayerTournament',
            fields=[
                ('tournament_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GvsC_Main.Tournament')),
                ('players', models.ManyToManyField(blank=True, to='GvsC_Main.Player')),
            ],
            options={
                'abstract': False,
            },
            bases=('GvsC_Main.tournament',),
        ),
        migrations.CreateModel(
            name='TeamSeating',
            fields=[
                ('seating_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GvsC_Main.Seating')),
                ('team', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='GvsC_Main.Team')),
            ],
            options={
                'abstract': False,
            },
            bases=('GvsC_Main.seating',),
        ),
        migrations.CreateModel(
            name='TeamTournament',
            fields=[
                ('tournament_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GvsC_Main.Tournament')),
                ('team_size', models.SmallIntegerField()),
                ('teams', models.ManyToManyField(to='GvsC_Main.Team')),
            ],
            options={
                'abstract': False,
            },
            bases=('GvsC_Main.tournament',),
        ),
        migrations.AddField(
            model_name='tournament',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GvsC_Main.Event'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='game_plugin',
            field=djangoplugins.fields.PluginField(on_delete=django.db.models.deletion.CASCADE, to='djangoplugins.Plugin'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_gvsc_main.tournament_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='seating',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GvsC_Main.Match'),
        ),
        migrations.AddField(
            model_name='seating',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_gvsc_main.seating_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='match',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GvsC_Main.Tournament'),
        ),
    ]
