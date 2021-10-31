from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Max, Min
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView

import json

from .models import UserManager, User
from .models import Course, Theme, Unit, Step, CourseAttd
from .models import Test, QuestionGroup, Question, CompletedQuestion

from .forms import (
    RegisterForm,
    UserPasswordResetForm,
    RegisterContinueForm,
    EditProfileForm,
)

UserModel = get_user_model()


def index(request):
    return render(request, "myapp/index.html", {})


def about(request):
    return render(request, "myapp/about.html", {})


def login_user(request):
    context = {}
    email = password = ""
    if request.POST:
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next_page = request.POST["next"]
                if not next_page:
                    return HttpResponseRedirect("/courses")
                return HttpResponseRedirect(next_page)
        else:
            context["wrong_credentials"] = True
    return render(request, "myapp/login.html", context)


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return HttpResponseRedirect("/registration-continued")
        return render(request, "myapp/registration.html", {"form": form})
    form = RegisterForm()
    return render(request, "myapp/registration.html", {"form": form})


@login_required(login_url="/login")
def registration_continued(request):
    if request.method == "POST":
        form = RegisterContinueForm(request.POST)
        if form.is_valid():
            request.user.user_phone_number = request.POST.get("user_phone_number")
            request.user.user_school_name = request.POST.get("user_school_name")
            request.user.user_grade = request.POST.get("user_grade")
            request.user.user_lang = request.POST.get("user_lang")
            request.user.user_location = request.POST.get("user_location")
            request.user.save()
            return HttpResponseRedirect("/courses")
        return HttpResponseRedirect("/error")
    form = RegisterContinueForm()
    return render(request, "myapp/registration-continued.html", {"form": form})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/login")


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = UserPasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Запрос на сброс пароля"
                    email_template_name = "myapp/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        "user_name": user.user_firstname,
                        "domain": "daiyndal.kz",
                        "site_name": "daiyndal",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "https",
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            "daiyndalgroup@gmail.com ",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("/password_reset/done/")
    password_reset_form = UserPasswordResetForm()
    return render(
        request=request,
        template_name="myapp/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )


@login_required(login_url="/login")
def profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        print(form.errors)
        if form.is_valid():
            request.user.email = request.POST.get("email")
            request.user.user_firstname = request.POST.get("user_firstname")
            request.user.user_lastname = request.POST.get("user_lastname")
            request.user.user_phone_number = request.POST.get("user_phone_number")
            request.user.user_school_name = request.POST.get("user_school_name")
            request.user.user_grade = request.POST.get("user_grade")
            request.user.user_lang = request.POST.get("user_lang")
            request.user.user_location = request.POST.get("user_location")
            request.user.save()
            return HttpResponseRedirect("/profile/")
        print("form is not valid")
    form = EditProfileForm(initial=model_to_dict(request.user))
    return render(request, "myapp/profile.html", {"form": form})


class CourseList(ListView):
    model = Course
    paginate_by = 9

    def get_queryset(self):
        name = self.request.GET.get("search", "")
        object_list = self.model.objects.all()
        if name:
            object_list = object_list.filter(course_name__icontains=name)
        return object_list


class MyCourseList(ListView):
    model = Course
    template_name = "myapp/mycourse_list.html"

    def get_queryset(self):
        object_list = self.model.objects.filter(
            course_id__in=CourseAttd.objects.filter(
                user=self.request.user, active=True
            ).values_list("course_id", flat=True)
        )
        return object_list


class CourseDetailView(DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # context['book_list'] = Book.objects.all()
        self.object = self.get_object()
        context["themes"] = Theme.objects.filter(
            course_id=self.object.course_id
        ).order_by("theme_order")
        context["units"] = (
            Unit.objects.filter(theme__in=context["themes"])
            .order_by("unit_order")
            .order_by("theme__theme_order")
        )
        context["tests"] = Step.objects.filter(unit__in=context["units"], step_type=1)
        if self.request.user.is_authenticated:
            context["attd"] = CourseAttd.objects.filter(
                user=self.request.user,
                course=self.get_object(),
                active=True,
            ).first()
            if context["attd"] and context["attd"].finished_steps:
                step_stop_on = Step.objects.get(pk=context["attd"].stop_on)
                context[
                    "continue_url"
                ] = f"/unit/{step_stop_on.unit_id}/step/{step_stop_on.step_id}/"
            else:
                first_step = (
                    Step.objects.filter(unit=context["units"][0])
                    .order_by("step_order")
                    .first()
                )
                context[
                    "continue_url"
                ] = f"/unit/{first_step.unit_id}/step/{first_step.step_id}/"
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if CourseAttd.objects.filter(
                user=request.user,
                course=self.get_object(),
                active=True,
            ).first():
                # Course attendance record exists in database
                return HttpResponseBadRequest()
            new_attd = CourseAttd(
                user=request.user, course=self.get_object(), finished_steps=""
            )
            new_attd.save()
            return HttpResponseRedirect(request.path)
        return HttpResponseRedirect(f"/login/?next={request.path}")


def lesson(request, unit_id, step_id):
    step = Step.objects.select_related("unit").get(pk=step_id)
    # Calculate next step
    steps_in_current_unit = Step.objects.filter(unit_id=unit_id).order_by("step_order")
    unit = step.unit
    if steps_in_current_unit.last() == step:
        # This step is last in its unit
        # Get parent unit to find next unit object
        if (
            Unit.objects.filter(theme=unit.theme_id).aggregate(Max("unit_order"))[
                "unit_order__max"
            ]
            == unit.unit_order
        ):
            # This unit is last in its theme
            # Get parent theme to find next theme object
            theme = Theme.objects.get(pk=unit_id)
            if (
                Theme.objects.filter(course=theme.course_id).aggregate(
                    Max("theme_order")
                )["theme_order__max"]
                == theme.theme_order
            ):
                # This theme is last in its course
                next_step = None
            else:
                next_theme = (
                    Theme.objects.filter(
                        course=theme.course_id, theme_order__gt=theme.theme_order
                    )
                    .order_by("theme_order")
                    .first()
                )
                next_unit = (
                    Unit.objects.filter(theme=next_theme).order_by("unit_order").first()
                )
                next_step = (
                    Step.objects.filter(unit=next_unit).order_by("step_order").first()
                )
        else:
            next_unit = (
                Unit.objects.filter(theme=unit.theme_id, unit_order__gt=unit.unit_order)
                .order_by("unit_order")
                .first()
            )
            next_step = (
                Step.objects.filter(unit=next_unit).order_by("step_order").first()
            )
    else:
        # Get next available step in this unit
        next_step = (
            Step.objects.filter(unit_id=unit_id, step_order__gt=step.step_order)
            .order_by("step_order")
            .first()
        )

    # Calculate previous step
    if steps_in_current_unit.first() == step:
        # This step is first in its unit
        # Get parent unit to find previous unit object
        if (
            Unit.objects.filter(theme=unit.theme_id).aggregate(Min("unit_order"))[
                "unit_order__min"
            ]
            == unit.unit_order
        ):
            # This unit is first in its theme
            # Get parent theme to find previous theme object
            theme = Theme.objects.get(pk=unit_id)
            if (
                Theme.objects.filter(course=theme.course_id).aggregate(
                    Min("theme_order")
                )["theme_order__min"]
                == theme.theme_order
            ):
                # This theme is first in its course
                prev_step = None
            else:
                prev_theme = (
                    Theme.objects.filter(
                        course=theme.course_id, theme_order__lt=theme.theme_order
                    )
                    .order_by("-theme_order")
                    .first()
                )
                last_unit__prev_theme = (
                    Unit.objects.filter(theme=prev_theme)
                    .order_by("-unit_order")
                    .first()
                )
                last_step__prev_unit = (
                    Step.objects.filter(unit=last_unit__prev_theme)
                    .order_by("-step_order")
                    .first()
                )
        else:
            prev_unit = (
                Unit.objects.filter(theme=unit.theme_id, unit_order__lt=unit.unit_order)
                .order_by("-unit_order")
                .first()
            )
            prev_step = (
                Step.objects.filter(unit=next_unit).order_by("-step_order").first()
            )
    else:
        # Get prev available step in this unit
        prev_step = (
            Step.objects.filter(unit_id=unit_id, step_order__lt=step.step_order)
            .order_by("-step_order")
            .first()
        )

    # Sidebar stuff
    themes = Theme.objects.filter(course=unit.theme.course_id).order_by("theme_order")
    themes_obj = []
    for theme in themes:
        themes_obj.append(
            (theme, Unit.objects.filter(theme=theme).order_by("unit_order"))
        )

    # Progress bar stuff
    attd = CourseAttd.objects.filter(
        course=unit.theme.course_id,
        user=request.user,
        active=True,
    ).first()
    step_attd = set(map(int, filter(None, attd.finished_steps.split(";"))))
    steps_complete = []
    for step_ in steps_in_current_unit:
        steps_complete.append("passed" if step_.step_id in step_attd else "")
        if step_ == step:
            steps_complete[-1] = "active"

    # generate url here to reduce query number
    prev_step_url = (
        f"/unit/{prev_step.unit_id}/step/{prev_step.step_id}"
        if prev_step
        else f"/courses/{unit.theme.course_id}"
    )
    next_step_url = (
        f"/unit/{next_step.unit_id}/step/{next_step.step_id}"
        if next_step
        else f"/course-ended/{unit.theme.course_id}"
    )

    attd.stop_on = step.step_id
    if step.step_type == 0:
        # HTML
        if step.step_id not in step_attd:
            attd.finished_steps += str(step.step_id) + ";"
        attd.save()
        return render(
            request,
            "myapp/step.html",
            {
                "step": step,
                "prev_step_url": prev_step_url,
                "next_step_url": next_step_url,
                "themes_obj": themes_obj,
                "steps_complete": steps_complete,
            },
        )
    else:
        attd.save()
        # Test
        test = Test.objects.get(step=step)
        return render(
            request,
            "myapp/step-test.html",
            {
                "step": step,
                "test_id": test.test_id,
                "prev_step_url": prev_step_url,
                "next_step_url": next_step_url,
                "themes_obj": themes_obj,
                "steps_complete": steps_complete,
            },
        )
    return Http404()


def course_ended(request, course_id):
    themes = Theme.objects.filter(course_id=course_id).order_by("theme_order")
    themes_obj = []
    for theme in themes:
        themes_obj.append(
            (theme, Unit.objects.filter(theme=theme).order_by("unit_order"))
        )
    return render(
        request,
        "myapp/course_ended.html",
        {"themes_obj": themes_obj, "course_id": course_id},
    )


def get_test(request, test_id):
    response_obj = []
    test_obj = Test.objects.get(pk=test_id)
    question_groups = QuestionGroup.objects.filter(test=test_id)
    for question_group in question_groups:
        questions = Question.objects.filter(question_group=question_group)
        response_obj.append(
            {
                "questions": [
                    {
                        "id": question.id,
                        "a": [question.a1, question.a2, question.a3, question.a4],
                        "question_text": question.question_text,
                    }
                    for question in questions
                ],
                "qg_text": question_group.qg_text,
            }
        )
    return JsonResponse(response_obj, safe=False)


def save_test(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        for question in data["q"]:
            new_cq = CompletedQuestion.objects.update_or_create(
                defaults={"cq_correct": question["correct"]},
                user_id=data["user_id"],
                question_id=question["id"],
            )
        attd = CourseAttd.objects.get(
            course=data["course_id"], user=data["user_id"], active=True
        )
        step_attd = set(map(int, filter(None, attd.finished_steps.split(";"))))
        if data["step_id"] not in step_attd:
            attd.finished_steps += ";" + str(data["step_id"])
        attd.stop_on = data["step_id"]
        attd.save()
        return JsonResponse(data, status=201)
    return JsonResponse(data, status=400)


def delete_attendance(request, course_id):
    if request.user.is_authenticated:
        attd = CourseAttd.objects.get(user=request.user.id, course_id=course_id)
        attd.active = False
        attd.save()
    return HttpResponseRedirect("/my-courses")


@csrf_exempt
def get_passed_percentage(request):
    response = {"passed_percentage": 0}
    if request.method == "GET":
        user_id = request.GET.get("user_id", "")
        course_id = request.GET.get("course_id", "")
        attd = CourseAttd.objects.get(course=course_id, user=user_id, active=True)
        attended = tuple(filter(None, attd.finished_steps.split(";")))
        total_steps = Step.objects.filter(unit__theme__course=course_id).count()
        response["passed_percentage"] = round(len(attended) / total_steps * 100)
        return JsonResponse(response, status=200)
