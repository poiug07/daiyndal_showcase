from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from myapp import models

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .forms import UserAdminCreationForm, UserAdminChangeForm

User = get_user_model()

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "user_firstname",
                    "user_lastname",
                    "user_phone_number",
                    "user_location",
                    "user_lang",
                    "user_grade",
                )
            },
        ),
        ("Permissions", {"fields": ("is_admin",)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "user_firstname",
                    "user_lastname",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ("id",)
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ()


admin.site.register(User, UserAdmin)


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    search_fields = ("theme_name",)
    list_filter = ("course",)


@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    autocomplete_fields = ["theme"]
    search_fields = ["unit_name"]
    fieldsets = (
        (
            None,
            {
                "fields": ("unit_id", "unit_name", "unit_description"),
            },
        ),
        (
            None,
            {
                "fields": ("theme", "unit_order"),
                "description": "Поиск производится только по названию темы(theme_name), название предмета не учитывается",
            },
        ),
        (
            None,
            {
                "fields": ("author_name",),
            },
        ),
    )
    readonly_fields = ("unit_id",)
    list_filter = ("theme",)
    filter_horizontal = ()


class HTMLInline(admin.StackedInline):
    model = models.HTML
    extra = 0


class TestInline(admin.StackedInline):
    model = models.Test
    extra = 0


@admin.register(models.Step)
class StepAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("step_id", "step_order", "step_type")}),
        (
            None,
            {
                "fields": ("unit",),
                "description": "Лучше найти unit_id и ввести сюда, но можно поиском по имени unit_name",
            },
        ),
    )
    readonly_fields = ("step_id",)
    raw_id_fields = ("unit",)
    inlines = (HTMLInline, TestInline)


@admin.register(models.Test)
class TestAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("test_id", "test_json", "test_difficulty")}),
        (
            None,
            {
                "fields": ("step",),
                "description": "Лучше найти step_id и ввести сюда, но можно поиском",
            },
        ),
    )
    readonly_fields = ("test_id",)
    raw_id_fields = ("step",)


class QuestionInline(admin.StackedInline):
    model = models.Question


@admin.register(models.QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    raw_id_fields = ("test",)
    fieldsets = (
        (
            None,
            {
                "fields": ("id",),
            },
        ),
        (
            None,
            {
                "fields": ("test",),
                "description": "Найди test_id и введи сюда, можно и поиском",
            },
        ),
        (None, {"fields": ("qg_text",)}),
    )
    readonly_fields = ("id",)
    inlines = (QuestionInline,)


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    raw_id_fields = ("question_group",)


@admin.register(models.CourseAttd)
class CourseAttdAdmin(admin.ModelAdmin):
    list_filter = ("active",)


models_to_register = [
    models.Course,
    models.CompletedQuestion,
    models.HTML,
    # Custom admins
]

admin.site.register(models_to_register)

# admin.site.register(User, MyUserAdmin)
