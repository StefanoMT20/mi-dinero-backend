from django.contrib import admin
from .models import Objective, KeyResult, Milestone


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0
    readonly_fields = ['id']


class KeyResultInline(admin.TabularInline):
    model = KeyResult
    extra = 0
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'start_date', 'end_date', 'created_at']
    list_filter = ['category', 'status', 'user', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    inlines = [KeyResultInline]


@admin.register(KeyResult)
class KeyResultAdmin(admin.ModelAdmin):
    list_display = ['title', 'objective', 'measurement_type', 'current_value', 'target_value', 'unit', 'created_at']
    list_filter = ['measurement_type', 'objective__category', 'created_at']
    search_fields = ['title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    inlines = [MilestoneInline]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'key_result', 'completed', 'order']
    list_filter = ['completed', 'key_result__objective__category']
    search_fields = ['title']
    readonly_fields = ['id']
    ordering = ['key_result', 'order']
