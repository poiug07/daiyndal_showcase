from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, user_firstname, user_lastname, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not user_firstname or not user_lastname:
            raise ValueError("Users must have firstname and lastname")

        user = self.model(
            email=self.normalize_email(email),
            user_firstname=user_firstname,
            user_lastname=user_lastname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_firstname, user_lastname, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            user_firstname=user_firstname,
            user_lastname=user_lastname,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = None
    email = models.EmailField("email address", unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    user_firstname = models.CharField(max_length=50)
    user_lastname = models.CharField(max_length=50)
    user_phone_number = models.CharField(max_length=13, null=True)
    user_lang = models.CharField(
        max_length=2,
        choices=[
            ("ru", "Рус"),
            ("kz", "Қаз"),
        ],
        default="ru",
    )
    user_school_name = models.CharField(max_length=100, null=True)
    user_grade = models.IntegerField(null=True)
    user_location = models.CharField(max_length=50, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_firstname", "user_lastname"]
    objects = UserManager()

    def __str__(self):
        return self.user_firstname + " " + self.user_lastname

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Supervisor(models.Model):
    # TODO: proper supervisor model
    pass


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=30)
    course_description = models.CharField(max_length=300)
    course_avatar = models.CharField(
        max_length=300, default="/static/img/course_avatar/math-avatar.png"
    )
    course_thumbnail = models.CharField(
        max_length=300, default="/static/img/course_thumbnail/math-card.jpg"
    )
    course_supervisor = models.CharField(max_length=100)
    course_supervisor_avatar = models.CharField(
        max_length=300,
        default="https://cdn0.iconfinder.com/data/icons/user-pictures/100/male-512.png",
    )
    active = models.BooleanField(default=False)
    # course_supervisor=models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    def __str__(self):
        return self.course_name


class Theme(models.Model):
    theme_id = models.AutoField(primary_key=True)
    theme_name = models.CharField(max_length=30)
    theme_order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False):
        # Only modify number if creating for the first time (is default 0)
        if self.theme_order == 0:
            # Grab the highest current index (if it exists)
            try:
                last = Theme.objects.filter(course__exact=self.course).order_by(
                    "theme_order"
                )[0]
                self.theme_order = last.theme_order + 1
            except IndexError:
                self.theme_order = 1
        # Call the "real" save() method
        super(Theme, self).save(force_insert, force_update)

    def __str__(self):
        return str(self.course) + ">" + self.theme_name


class Unit(models.Model):
    unit_id = models.AutoField(primary_key=True)
    unit_name = models.CharField(max_length=100)
    unit_description = models.CharField(max_length=100)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    unit_order = models.IntegerField(default=0)
    author_name = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ("theme", "unit_order")

    def save(self, force_insert=False, force_update=False):
        # Only modify number if creating for the first time (is default 0)
        if self.unit_order == 0:
            # Grab the highest current index (if it exists)
            try:
                last = Unit.objects.filter(theme__exact=self.theme).order_by(
                    "unit_order"
                )[0]
                self.unit_order = last.unit_order + 1
            except IndexError:
                self.unit_order = 1
        # Call the "real" save() method
        super(Unit, self).save(force_insert, force_update)

    def __str__(self):
        return str(self.theme) + ">" + self.unit_name


class Step(models.Model):
    step_id = models.AutoField(primary_key=True)
    step_name = models.CharField(max_length=100, blank=True)
    step_order = models.PositiveSmallIntegerField(default=0)
    # step_type: 0 - HTML, 1 - Test
    step_type = models.PositiveSmallIntegerField(
        choices=(
            (0, "HTML"),
            (1, "Test"),
        ),
        default=0,
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("unit", "step_order")

    def save(self, force_insert=False, force_update=False):
        # Only modify number if creating for the first time (is default 0)
        if self.step_order == 0:
            # Grab the highest current index (if it exists)
            try:
                last = Step.objects.filter(unit=self.unit).order_by("-step_order")[0]
                print(last.step_order)
                self.step_order = last.step_order + 1
            except IndexError:
                print("Index Error Happened")
                self.step_order = 1
        # Call the "real" save() method
        super(Step, self).save(force_insert, force_update)

    def __str__(self):
        return (
            str(self.unit)
            + ">"
            + str(self.step_order)
            + (" HTML", " Test")[self.step_type]
        )


class Test(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_json = models.TextField(blank=True, default="")
    # test_difficulty: 1-3 difficulty
    test_difficulty = models.PositiveSmallIntegerField(
        choices=(
            (1, "Easy"),
            (2, "Medium"),
            (3, "Hard"),
        ),
        default=1,
    )
    step = models.ForeignKey(Step, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.step)


class QuestionGroup(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    qg_text = models.TextField(null=True, blank=True)


class Question(models.Model):
    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    # a1 is correct answer by default
    a1 = models.CharField(max_length=100, help_text="This must be correct answer")
    a2 = models.CharField(max_length=100)
    a3 = models.CharField(max_length=100)
    a4 = models.CharField(max_length=100)


class CompletedQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    cq_correct = models.BooleanField()


class HTML(models.Model):
    content = models.TextField()
    step = models.OneToOneField(Step, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.step)


class CourseAttd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    finished_steps = models.TextField(blank=True)
    stop_on = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
