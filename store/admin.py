from django.contrib import admin

from store.models import Car, Application, Document, DocumentType

# Register your models here.
admin.site.register(Car)
admin.site.register(Application)
admin.site.register(Document)
admin.site.register(DocumentType)
