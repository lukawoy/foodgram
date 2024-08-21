from django.contrib import admin

from .models import User, Follow

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff')
    list_filter = ('is_staff', )
    empty_value_display = 'Не заполнено'
    list_editable = ['is_staff']
    search_fields = ['username', 'email']

admin.site.register(User, UserAdmin)
admin.site.register(Follow)