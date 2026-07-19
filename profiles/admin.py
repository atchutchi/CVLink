from django.contrib import admin

from .models import Certification, Education, Experience, Profile, ProfileLanguage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("public_name", "user", "professional_title", "status", "is_public")
    list_filter = ("status", "is_public")
    search_fields = ("public_name", "user__email", "professional_title", "location")
    filter_horizontal = ("specializations", "skills")
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Certification)
admin.site.register(ProfileLanguage)
