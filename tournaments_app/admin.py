from django.contrib import admin

# Register your models here.


from django_summernote.admin import SummernoteModelAdmin
from tournaments_app.models import Tournaments
# Apply summernote to all TextField in model.
class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
    summernote_fields = ('details',)

admin.site.register(Tournaments, SomeModelAdmin)