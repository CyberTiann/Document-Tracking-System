from django.db import models

class agencyModel(models.Model):
    agency_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.agency_choice

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"
        ordering = ['agency_choice']  # Order alphabetically

class workgroupModel(models.Model):
    workgroup_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.workgroup_choice

    class Meta:
        verbose_name = "Workgroup"
        verbose_name_plural = "Workgroups"
        ordering = ['workgroup_choice']  # Order alphabetically

class attentionModel(models.Model):
    attention_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.attention_choice

    class Meta:
        verbose_name = "Attention"
        verbose_name_plural = "Attentions"
        ordering = ['attention_choice']  # Order alphabetically

class unitModel(models.Model):
    unit_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unit_choice

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        ordering = ['unit_choice']  # Order alphabetically

class subjectModel(models.Model):
    subject_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.subject_choice

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['subject_choice']  # Order alphabetically

class toModel(models.Model):
    to_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.to_choice

    class Meta:
        verbose_name = "Recipient"
        verbose_name_plural = "Recipients"
        ordering = ['to_choice']  # Order alphabetically

class sourceModel(models.Model):
    source_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.source_choice

    class Meta:
        verbose_name = "Source"
        verbose_name_plural = "Sources"
        ordering = ['source_choice']  # Order alphabetically

class documentTypeModel(models.Model):
    document_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.document_choice

    class Meta:
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"
        ordering = ['document_choice']  # Order alphabetically

class outModel(models.Model):
    out_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.out_choice

    class Meta:
        verbose_name = "Output"
        verbose_name_plural = "Outputs"
        ordering = ['out_choice']  # Order alphabetically

class statusModel(models.Model):
    status_choice = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.status_choice

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        ordering = ['status_choice']  # Order alphabetically
