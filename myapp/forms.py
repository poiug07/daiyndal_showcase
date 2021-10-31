from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, SetPasswordForm

User = get_user_model()


class RegisterForm(forms.ModelForm):

    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@email.com",
                "v-model": "email",
                ":class": '{ "is-invalid": errors.email }',
            }
        )
    )
    user_firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Иван",
                "v-model": "user_firstname",
                ":class": '{ "is-invalid": errors.user_firstname }',
            }
        )
    )
    user_lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Иванов",
                "v-model": "user_lastname",
                ":class": '{ "is-invalid": errors.user_lastname }',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "**********",
                "v-model": "password",
                ":class": '{ "is-invalid": errors.password }',
            }
        )
    )
    password_2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "**********",
                "v-model": "password_2",
                ":class": '{ "is-invalid": errors.password_2 }',
            }
        )
    )

    class Meta:
        model = User
        fields = ["email", "user_firstname", "user_lastname", "password"]

    def clean_email(self):
        """
        Verify email is available.
        """
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean(self):
        """
        Verify both passwords match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "user_firstname", "user_lastname"]

    def clean(self):
        """
        Verify both passwords match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "password", "is_active", "is_admin"]

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


from django.contrib.auth.forms import PasswordResetForm


class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@email.com"}
        )
    )


class MySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(MySetPasswordForm, self).__init__(*args, **kwargs)

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "**********"}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "**********"}
        )
    )


class RegisterContinueForm(forms.ModelForm):

    user_phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "87771112244",
                "v-model": "phone",
                "@input": "phoneValidate",
                ":class": '{ "is-invalid": errors.phone }',
            }
        )
    )
    user_school_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Школа №555",
                "v-model": "school",
                ":class": '{ "is-invalid": errors.school }',
            }
        )
    )
    user_grade = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    user_lang = forms.CharField(
        widget=forms.Select(
            attrs={
                "class": "form-control",
            },
            choices=[("none", "Выберите язык обучения"), ("ru", "Рус"), ("kz", "Қаз")],
        )
    )
    user_location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Актобе",
                "v-model": "location",
                ":class": '{ "is-invalid": errors.location }',
            }
        )
    )

    class Meta:
        model = User
        fields = [
            "user_phone_number",
            "user_school_name",
            "user_grade",
            "user_lang",
            "user_location",
        ]


class EditProfileForm(forms.ModelForm):

    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@email.com"}
        )
    )
    user_firstname = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Иван"})
    )
    user_lastname = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Иванов"})
    )
    user_phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "87771112244"}
        )
    )
    user_school_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Школа №555"}
        )
    )
    user_grade = forms.IntegerField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Школа №555"}
        )
    )
    user_lang = forms.CharField(
        widget=forms.Select(
            attrs={
                "class": "form-control",
            },
            choices=[("none", "Выберите язык обучения"), ("ru", "Рус"), ("kz", "Қаз")],
        )
    )
    user_location = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Актобе"})
    )

    class Meta:
        model = User
        fields = [
            "email",
            "user_firstname",
            "user_lastname",
            "user_phone_number",
            "user_school_name",
            "user_grade",
            "user_lang",
            "user_location",
        ]

    def clean_email(self):
        """
        Verify email is available.
        """
        email = self.cleaned_data.get("email")
        qs = User.objects.exclude(pk=self.instance.pk).filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email
