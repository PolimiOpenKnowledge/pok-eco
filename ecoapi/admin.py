# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Teacher, TeacherDescription, CourseStructureCache


class TeacherDescriptionInline(admin.TabularInline):
    model = TeacherDescription
    extra = 1


class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id_teacher', 'first_name', 'last_name', 'image']
    list_display_links = ['first_name', 'last_name']
    inlines = [TeacherDescriptionInline]

admin.site.register(Teacher, TeacherAdmin)
admin.site.register(CourseStructureCache)
