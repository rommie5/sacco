from django.contrib import admin
from .models import MemberProfile

@admin.action(description="✅ Approve selected members")
def approve_members(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="⏳ Mark selected as Pending")
def pending_members(modeladmin, request, queryset):
    queryset.update(is_approved=False)


class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "phone_number",
        "is_completed",
        "is_approved",
        "created_at",
    )
    list_filter = ("is_completed", "is_approved", "created_at")
    search_fields = ("user__username", "user__email", "phone_number", "surname", "given_name")
    ordering = ("-created_at",)
    actions = [approve_members, pending_members]
    readonly_fields = ("created_at", "updated_at")


admin.site.register(MemberProfile, MemberProfileAdmin)
