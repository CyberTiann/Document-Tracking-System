from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from choice.models import attentionModel, agencyModel, workgroupModel, unitModel, subjectModel, toModel, sourceModel, outModel, statusModel, documentTypeModel
import shutil
import pytesseract
from PIL import Image
import os
from django.core.mail import send_mail  # Add this import
from DTS.settings import EMAIL_HOST_USER
from .ocr import perform_ocr  # Import the perform_ocr function

def user_directory_path(instance, filename):
    """
    Upload files to a folder based on the user's workgroup, with an additional subdirectory.
    """
    if hasattr(instance, 'uploader') and instance.uploader:
        user_groups = instance.uploader.groups.all()
        if user_groups.exists():
            group_name = user_groups.first().name
            subdirectory = getattr(instance, 'subdirectory', '')  # Default to empty string if not present
            return f'uploads/{group_name}/{subdirectory}/{filename}' if subdirectory else f'uploads/{group_name}/{filename}'
    
    return f'uploads/DEFAULT/{filename}'

def get_folder_choices():
    directory_path = 'uploads/'  # Change this to your directory path
    entries = os.listdir(directory_path)
    # Get only directories
    folder_names = [(entry, entry) for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
    return folder_names
    
class Document(models.Model):
   

    agency = models.ForeignKey(agencyModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Agency")
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, help_text="Account name will auto-fill the uploader")
    workgroup_source = models.ForeignKey(workgroupModel, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(null=True, blank=True, max_length=100)
    file = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    date_in = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="Date In")
    workgroup = models.CharField(null=True, blank=True, max_length=100)
    subdirectory = models.CharField(null=True, blank=True, max_length=100, help_text="Optional")
    unit = models.ForeignKey(unitModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unit")
    source = models.ForeignKey(sourceModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Source")
    subject = models.ForeignKey(subjectModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Subject")
    to = models.ForeignKey(toModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="To")
    carbon_copy = models.CharField(choices=get_folder_choices, max_length=100, null=True, blank=True, verbose_name="Carbon Copy")
    document_type = models.ForeignKey(documentTypeModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Document Type")
    out = models.ForeignKey(outModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Out")
    date_out = models.DateTimeField(blank=True, null=True, verbose_name="Date Out")
    status = models.ForeignKey(statusModel, on_delete=models.SET_NULL, null=True, blank=True, default=2)
    note = models.TextField(null=True, blank=True)
    additional_details = models.TextField(null=True, blank=True)
    approval_l1 = models.ForeignKey(statusModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_l1', default=2, verbose_name="Level 1 Approval")
    approval_l2 = models.ForeignKey(statusModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_l2', default=2, verbose_name="Level 2 Approval")
    approval_l3 = models.ForeignKey(statusModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_l3', default=2, verbose_name="Level 3 Approval")
    level1_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='level1_approver', verbose_name="First Level Approver", help_text="Optional")
    level2_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='level2_approver', verbose_name="Second Level Approver", help_text="Optional")
    level3_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='level3_approver', default=None, verbose_name="Third Level Approver", help_text="Optional")
    existing_subdirectory = models.CharField(choices=get_folder_choices, max_length=100, blank=True, null=True, help_text="Select an existing subdirectory")
    approval_l1_message = models.CharField(max_length=255, blank=True, null=True, verbose_name="1st Approval Status")
    approval_l2_message = models.CharField(max_length=255, blank=True, null=True, verbose_name="2nd Approval Status")
    approval_l3_message = models.CharField(max_length=255, blank=True, null=True, verbose_name="3rd Approval Status")
    extracted_text = models.TextField(null=True, blank=True, verbose_name="Extracted Text")  # New field
    def __str__(self):
        return f"{self.workgroup}"
    
    def save(self, *args, **kwargs):
        # Ensure initial status is always 'Pending' (assuming 'Pending' has id=2)
        pending_status = statusModel.objects.get(id=2)
        na_status = statusModel.objects.get(id=6)

        # Set approval statuses based on approvers
        if self.level1_approver:
            self.approval_l1 = self.approval_l1 or pending_status
        else:
            self.approval_l1 = na_status

        if self.level2_approver:
            self.approval_l2 = self.approval_l2 or pending_status
        else:
            self.approval_l2 = na_status

        if self.level3_approver:
            self.approval_l3 = self.approval_l3 or pending_status
        else:
            self.approval_l3 = na_status

        # Get the initial status (before save)
        initial_approval_l3 = None
        if self.pk:
            initial_document = Document.objects.get(pk=self.pk)
            initial_approval_l1 = initial_document.approval_l1
            initial_approval_l2 = initial_document.approval_l2
            initial_approval_l3 = initial_document.approval_l3

        # Determine if the highest assigned approver has approved
        if self.level3_approver:
            if self.approval_l3 in [statusModel.objects.get(id=1), statusModel.objects.get(id=3), statusModel.objects.get(id=5)]:
                self.date_out = timezone.now()  # Set date_out if L3 has approved
            else:
                self.date_out = None  # Reset if L3 has not approved
        elif self.level2_approver:
            if self.approval_l2 in [statusModel.objects.get(id=1), statusModel.objects.get(id=3), statusModel.objects.get(id=5)]:
                self.date_out = timezone.now()  # Set date_out if L2 has approved
            else:
                self.date_out = None  # Reset if L2 has not approved
        elif self.level1_approver:
            if self.approval_l1 in [statusModel.objects.get(id=1), statusModel.objects.get(id=3), statusModel.objects.get(id=5)]:
                self.date_out = timezone.now()  # Set date_out if L1 has approved
            else:
                self.date_out = None  # Reset if L1 has not approved
        else:
            self.date_out = None  # Reset if no approvers are assigned

        # Check if approval status changed and append approver's name
        if self.approval_l3 in [statusModel.objects.get(id=1), statusModel.objects.get(id=3), statusModel.objects.get(id=5), statusModel.objects.get(id=4)] and initial_approval_l3 != self.approval_l3:
            if self.approval_l3 ==  statusModel.objects.get(id=1):
                self.approval_l3_message = f"✅ Approved by {self.level3_approver.username}"
            elif self.approval_l3 == statusModel.objects.get(id=5):
                self.approval_l3_message = f"📁 For Filing by {self.level3_approver.username}"  # Store approver's name
            elif self.approval_l3 == statusModel.objects.get(id=3):
                self.approval_l3_message = f"📝 Returned with Remarks by {self.level3_approver.username}" 
                send_mail(
                    'Document Requested for Revision',
                    f'Document ID {self.id} has been rejected and requires revision. Thank you.',
                    f'From {self.level3_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                ) # Store approver's name
            elif statusModel.objects.get(id=4):
                self.approval_l3_message = f"🔁 Revision Requested by {self.level3_approver.username}" 
                send_mail(
                    'Document Requested for Revision',
                    f'Document ID {self.id} has been rejected and requires revision. Thank you.',
                    'from@example.com',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                ) # Store approver's name

        elif self.approval_l2 in [statusModel.objects.get(id=1), statusModel.objects.get(id=5), statusModel.objects.get(id=5), statusModel.objects.get(id=4)] and initial_approval_l2 != self.approval_l2:
            if self.approval_l2 == statusModel.objects.get(id=1):
                self.approval_l2_message = f"✅ Approved by {self.level2_approver.username}"  # Store approver's name
                send_mail(
                    'Document Transfer',
                    f'You have marked Document ID {self.id} as Approved and is now transferred to "{self.level3_approver.username}". Thank you.',
                    f'From {self.level3_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                )   # Store approver's name
            elif self.approval_l2 == statusModel.objects.get(id=5):
                self.approval_l2_message = f"📁 For Filing by {self.level2_approver.username}"  # Store approver's name
            elif self.approval_l2 == statusModel.objects.get(id=4):
                self.approval_l2_message = f"📝 Revision Requested by {self.level2_approver.username}" 
                send_mail(
                    'Document Requested for Revision',
                    f'Document ID {self.id} has been rejected and requires revision. Thank you.',
                    f'From {self.level2_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                ) # Store approver's name
            elif self.approval_l2 == statusModel.objects.get(id=3):
                self.approval_l2_message = f"🔁 Returned with Remarks by {self.level2_approver.username}" 
                send_mail(
                    'Document Requested for Revision',
                    f'Document ID {self.id} has been rejected and requires revision. Thank you.',
                    f'From {self.level2_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                ) # Store approver's name

        elif self.approval_l1 in [statusModel.objects.get(id=1), statusModel.objects.get(id=5), statusModel.objects.get(id=5), statusModel.objects.get(id=4)] and initial_approval_l1 != self.approval_l1:
            if self.approval_l1 == statusModel.objects.get(id=1):           
                self.approval_l1_message = f"✅ Approved by {self.level1_approver.username}" 
                send_mail(
                    'Document Transfer',
                    f'You have marked Document ID {self.id} as Approved and is now transferred to "{self.level2_approver.username}". Thank you.',
                    f'From {self.level1_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                )   # Store approver's name # Store approver's name
            elif self.approval_l1 == statusModel.objects.get(id=5):
                self.approval_l1_message = f"📁 For Filing by {self.level1_approver.username}"  # Store approver's name
            elif self.approval_l1 == statusModel.objects.get(id=4):
                self.approval_l1_message = f"📝 Revision Requested by {self.level1_approver.username}" 
                send_mail(
                    'Document Requested for Revision',
                    f'Document ID {self.id} has been rejected and requires revision. Thank you.',
                    f'From {self.level1_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                ) # Store approver's name
            elif self.approval_l1 == statusModel.objects.get(id=3):
                self.approval_l1_message = f"🔁 Returned with Remarks by {self.level1_approver.username}" 
                send_mail(
                    'Document Requested for Revision',
                    f'Document ID {self.id} has been rejected and requires revision. Thank you.',
                    f'From {self.level1_approver.username}',  # Replace with your sender email
                    [self.uploader.email],  # Assuming uploader has an email field
                    fail_silently=False,
                ) # Store approver's name
        # Save the document first
        super().save(*args, **kwargs)

        # Perform OCR if a file is uploaded
        if self.file:
            # Get the file extension
            file_extension = os.path.splitext(self.file.name)[1].lower()  # Get the file extension in lowercase
            
            # Check if the file is an image
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.pdf']:
                # Call the OCR function
                self.extracted_text = perform_ocr(self.file.path)  # Perform OCR

                # Save the extracted text back to the database without triggering the save method again
                Document.objects.filter(pk=self.pk).update(extracted_text=self.extracted_text)

        # Now that the document is saved, proceed with sending emails
        # Send emails to approvers if necessary
        if self.level1_approver:
            if self.approval_l1 == pending_status:
                self.send_approval_email(self.level1_approver)
            elif self.approval_l1 in[statusModel.objects.get(id=3), statusModel.objects.get(id=4)]:
                pass
        if self.level2_approver:
            if (self.approval_l2 == pending_status) and (self.approval_l1 == statusModel.objects.get(id=1)):
                self.send_approval_email(self.level2_approver)
            elif self.approval_l2 in[statusModel.objects.get(id=3), statusModel.objects.get(id=4)]:
                pass
        if self.level3_approver:
            if (self.approval_l3 == pending_status) and (self.approval_l2 == statusModel.objects.get(id=1)):
                self.send_approval_email(self.level3_approver)
            elif self.approval_l3 in[statusModel.objects.get(id=3), statusModel.objects.get(id=4)]:
                pass

        # Upload the file to the selected carbon copy if it exists
        if self.carbon_copy and self.file:
            self.upload_to_carbon_copy()

        # Upload to the user's workgroup if the document type is "Announcement"
        if self.document_type and self.document_type.document_choice == "Announcement":
            self.upload_to_workgroup()

    def send_approval_email(self, approver):
        # Fetch document details (subject and id) after the document has been saved
        subject = f'Document Approval Request: {self.subject} (ID: {self.id})'
        message = f'Good Day {approver.username},\n\nYou have a new pending document approval. "{self.document_type}".\nDocument ID: {self.id}\n The file approvers are "{self.level1_approver}", "{self.level2_approver}","{self.level3_approver}"\nBest regards,\nNDC DTS'
        recipient_list = [approver.email]

        # Send the email
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)

    def upload_to_carbon_copy(self):
        """
        Copy the document file to the selected carbon copy folder.
        """
        destination_path = os.path.join('uploads', self.carbon_copy, self.file.name)
        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path))
        shutil.copy(self.file.path, destination_path)

    def upload_to_workgroup(self):
        """
        Copy the document file to the user's workgroup folder.
        """
        user_workgroup_path = os.path.join('uploads', self.workgroup, self.file.name)
        if not os.path.exists(os.path.dirname(user_workgroup_path)):
            os.makedirs(os.path.dirname(user_workgroup_path))
        shutil.copy(self.file.path, user_workgroup_path)

    def __str__(self):
        return self.title or self.workgroup or "Unnamed Document"

    class Meta:
        permissions = [
            ('can_approve_l1', 'Can approve Level 1'),
            ('can_approve_l2', 'Can approve Level 2'),
            ('can_approve_l3', 'Can approve Level 3'),
            ('can_comment', 'Can comment to staff documents')  # Custom permission
        ]

class upload(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Title")
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, help_text="Account name will auto-fill the uploader", verbose_name="Action Officer")
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="Date")
    workgroup = models.CharField(max_length=10, blank=True, null=True, help_text="Workgroup will be autofilled by the user's group.", verbose_name="Workgroup")
    file = models.FileField(upload_to=user_directory_path, blank=True, null=True, help_text="Leave blank if no file will be uploaded")
    slug = models.SlugField(blank=True, null=True)
    subdirectory = models.CharField(max_length=100, blank=True, null=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title or self.workgroup

class Profile(models.Model):
    ROLE_CHOICES = (
        (1, 'Superadmin'),
        (2, 'Workgroup Admin'),
        (3, 'Staff')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    @property
    def email(self):
        return self.user.email

    def get_groups(self):
        return ", ".join([group.name for group in self.user.groups.all()])

    def __str__(self):
        return self.user.username
