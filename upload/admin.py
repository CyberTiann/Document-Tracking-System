from django.contrib import admin
from .models import Document, upload, Profile
import pandas as pd
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db.models import F

import os


# START OF DTS
def export_to_excel(modeladmin, request, queryset):
    # Annotate the queryset to include related object's display value
    queryset = queryset.annotate(
        action_officer=F('uploader__username'),
        agency_name=F('agency__agency_choice'),
        document_type_name=F('document_type__document_choice'),
        approval_l1_name=F('approval_l1__status_choice'),
        approval_l2_name=F('approval_l2__status_choice'),
        approval_l3_name=F('approval_l3__status_choice'),
        subject_name=F('subject__subject_choice')
    )

    # Select only the desired fields
    data = list(queryset.values(
        'action_officer',
        'workgroup',
        'subject_name',
        'agency_name',
        'id',
        'document_type_name',
        'approval_l1_name',
        'approval_l2_name',
        'approval_l3_name',
        'date_in',
        'date_out'
    ))

    # Create a pandas DataFrame from the data
    df = pd.DataFrame(data)

    # Rename columns to match desired output
    df.rename(columns={
        'action_officer': 'Action Officer',
        'workgroup': 'Workgroup',
        'subject_name': 'Subject',
        'agency_name': 'Agency',
        'id': 'ID',
        'document_type_name': 'Document Type',
        'approval_l1_name': 'Approver L1',
        'approval_l2_name': 'Approver L2',
        'approval_l3_name': 'Approver L3',
        'date_in': 'Date In',
        'date_out': 'Date Out'
    }, inplace=True)

    # Convert timezone-aware datetimes to timezone-naive
    for col in ['Date In', 'Date Out']:
        df[col] = pd.to_datetime(df[col]).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export.xlsx'

    # Use pandas to write the DataFrame to the response
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    return response
export_to_excel.short_description = 'Export to Excel'

       
       
class DocumentAdmin(admin.ModelAdmin):


    search_fields = [
        'id',
        'uploader__username',
        'agency__agency_choice',
        'workgroup_source__workgroup_choice',
        'unit__unit_choice',
        'subject__subject_choice',
        'to__to_choice',
        'extracted_text',
        'source__source_choice',
        'document_type__document_choice',
        'out__out_choice',
        'status__status_choice',
        'file',
        'date_in',
        'date_out',
    ]
    
    fieldsets = (
        ('Source of Document', {
            "fields": (
                "agency", "workgroup_source", "unit",
            ),
        }),
        ('Details', {
            "fields": (
                "document_type", "file", "subject", "to",   "carbon_copy", "additional_details", "out",
            ),
        }),
        ('Approvers', {
            "fields": (
                "level1_approver", "level2_approver", "level3_approver",
            ),
        }),
        ('Status', {
            "fields": (
                "approval_l1", "approval_l2", "approval_l3", "note",
            ),
        }),
        ('Subdirectory', {
            "fields": (
                "subdirectory", #"existing_subdirectory",    
            ),
        })
    )

    list_display = ("get_action_officer", "workgroup_source", "subject", "id","document_type", "approval_l1_message", "approval_l2_message", "approval_l3_message", "date_in", "date_out", "agency", "extracted_text")  # Add extracted_text
    list_filter = [
        'agency',
        'workgroup_source',
        'unit',
        'document_type',
        'date_in',
        'date_out',
    ]

    def get_action_officer(self, obj):
        # Return the username of the action officer or 'N/A' if not set
        return obj.uploader.username if obj.uploader else 'N/A'
    get_action_officer.short_description = 'Action Officer'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploader = request.user
            user_groups = request.user.groups.all()
            if user_groups.exists():
                obj.workgroup = user_groups.first().name
            else:
                obj.workgroup = 'DEFAULT'
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj:
            # Make approver fields read-only for everyone except the uploader
            if request.user != obj.uploader:
                readonly.extend(['level1_approver', 'level2_approver', 'level3_approver'])
            # Make status fields read-only for the uploader
            if request.user == obj.uploader:
                readonly.extend(['approval_l1', 'approval_l2', 'approval_l3'])
            # Make status fields editable only for the respective approvers
            if request.user != obj.level1_approver:
                readonly.append('approval_l1')
            if request.user != obj.level2_approver:
                readonly.append('approval_l2')
            if request.user != obj.level3_approver:
                readonly.append('approval_l3')


            ####UNALLOW OVERRIDE OF PERMISSIONS    
            # Sequential approval logic
            #if obj.approval_l1.id == 2:  # Assuming 'Pending' has id=2
            #    readonly.extend(['approval_l2', 'approval_l3'])
            #elif obj.approval_l2.id == 2:
            #    readonly.append('approval_l3')
        else:
            # When creating a new document, make approval fields read-only for the uploader
            readonly.extend(['approval_l1', 'approval_l2', 'approval_l3'])

        return readonly
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='GM').exists():
            return qs
        user_groups = request.user.groups.all()
        if user_groups.exists():
            return qs.filter(workgroup=user_groups.first().name) | qs.filter(document_type__document_choice="Announcement")
        return qs.filter(document_type__document_choice="Announcement")

    actions = [export_to_excel]

admin.site.register(Document, DocumentAdmin)
# END OF DTS

# START OF DMS
class UploadAdminArea(admin.AdminSite):
    site_header = "DMS SuperAdmin"

upload_site = UploadAdminArea(name='UploadAdmin')
upload_site.register(upload)

class Filter_Upload(admin.ModelAdmin):
    list_display = ("title",'subdirectory', "id", "uploader", "workgroup", "date")
    readonly_fields = ('uploader', "workgroup")
    list_filter = ("workgroup", 'date',)
    search_fields = ("title", "workgroup")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_groups = request.user.groups.all()
        if user_groups.exists():
            return qs.filter(workgroup=user_groups.first().name)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploader = request.user
            user_groups = request.user.groups.all()
            if user_groups.exists():
                obj.workgroup = user_groups.first().name
            else:
                obj.workgroup = 'DEFAULT'
        super().save_model(request, obj, form, change)

admin.site.register(upload, Filter_Upload)

class Filter(admin.ModelAdmin):
    list_display = ("id", "email", "created_at", "role", "is_active", "get_groups")
    list_filter = ("is_active", "role", "created_at")

admin.site.register(Profile, Filter)
# END OF DMS

# START OF FILE MOVEMENT HANDLING

# END OF FILE MOVEMENT HANDLING

