from django.contrib import admin

from .models import agencyModel, workgroupModel, unitModel, subjectModel, toModel, sourceModel, outModel, statusModel, documentTypeModel
# Register your models here.
admin.site.register(agencyModel)
admin.site.register(workgroupModel)
admin.site.register(unitModel)
admin.site.register(subjectModel)
admin.site.register(toModel)
admin.site.register(sourceModel)
admin.site.register(outModel)
admin.site.register(statusModel)
admin.site.register(documentTypeModel)


