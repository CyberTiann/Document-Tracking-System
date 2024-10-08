# Generated by Django 5.1.1 on 2024-10-06 06:44

import django.db.models.deletion
import upload.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('choice', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to=upload.models.user_directory_path)),
                ('date_in', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date In')),
                ('workgroup', models.CharField(blank=True, max_length=100, null=True)),
                ('subdirectory', models.CharField(blank=True, help_text='Optional', max_length=100, null=True)),
                ('carbon_copy', models.CharField(blank=True, choices=upload.models.get_folder_choices, max_length=100, null=True, verbose_name='Carbon Copy')),
                ('date_out', models.DateTimeField(blank=True, null=True, verbose_name='Date Out')),
                ('note', models.TextField(blank=True, null=True)),
                ('additional_details', models.TextField(blank=True, null=True)),
                ('existing_subdirectory', models.CharField(blank=True, choices=upload.models.get_folder_choices, help_text='Select an existing subdirectory', max_length=100, null=True)),
                ('approval_l1_message', models.CharField(blank=True, max_length=255, null=True, verbose_name='1st Approval Status')),
                ('approval_l2_message', models.CharField(blank=True, max_length=255, null=True, verbose_name='2nd Approval Status')),
                ('approval_l3_message', models.CharField(blank=True, max_length=255, null=True, verbose_name='3rd Approval Status')),
                ('extracted_text', models.TextField(blank=True, null=True, verbose_name='Extracted Text')),
                ('agency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.agencymodel', verbose_name='Agency')),
                ('approval_l1', models.ForeignKey(blank=True, default=2, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_l1', to='choice.statusmodel', verbose_name='Level 1 Approval')),
                ('approval_l2', models.ForeignKey(blank=True, default=2, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_l2', to='choice.statusmodel', verbose_name='Level 2 Approval')),
                ('approval_l3', models.ForeignKey(blank=True, default=2, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_l3', to='choice.statusmodel', verbose_name='Level 3 Approval')),
                ('document_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.documenttypemodel', verbose_name='Document Type')),
                ('level1_approver', models.ForeignKey(blank=True, help_text='Optional', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='level1_approver', to=settings.AUTH_USER_MODEL, verbose_name='First Level Approver')),
                ('level2_approver', models.ForeignKey(blank=True, help_text='Optional', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='level2_approver', to=settings.AUTH_USER_MODEL, verbose_name='Second Level Approver')),
                ('level3_approver', models.ForeignKey(blank=True, default=None, help_text='Optional', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='level3_approver', to=settings.AUTH_USER_MODEL, verbose_name='Third Level Approver')),
                ('out', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.outmodel', verbose_name='Out')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.sourcemodel', verbose_name='Source')),
                ('status', models.ForeignKey(blank=True, default=2, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.statusmodel')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.subjectmodel', verbose_name='Subject')),
                ('to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.tomodel', verbose_name='To')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.unitmodel', verbose_name='Unit')),
                ('uploader', models.ForeignKey(blank=True, help_text='Account name will auto-fill the uploader', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workgroup_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='choice.workgroupmodel')),
            ],
            options={
                'permissions': [('can_approve_l1', 'Can approve Level 1'), ('can_approve_l2', 'Can approve Level 2'), ('can_approve_l3', 'Can approve Level 3'), ('can_comment', 'Can comment to staff documents')],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Superadmin'), (2, 'Workgroup Admin'), (3, 'Staff')], null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='upload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Title')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date')),
                ('workgroup', models.CharField(blank=True, help_text="Workgroup will be autofilled by the user's group.", max_length=10, null=True, verbose_name='Workgroup')),
                ('file', models.FileField(blank=True, help_text='Leave blank if no file will be uploaded', null=True, upload_to=upload.models.user_directory_path)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('subdirectory', models.CharField(blank=True, max_length=100, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('uploader', models.ForeignKey(blank=True, help_text='Account name will auto-fill the uploader', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Action Officer')),
            ],
        ),
    ]
