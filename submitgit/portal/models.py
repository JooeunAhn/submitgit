from django.conf import settings
from django.db import models


class Course(models.Model):
    SEMESTER = (
        (0, "1학기"),
        (1, "여름 계절학기"),
        (2, "2학기"),
        (3, "겨울 계절학기")
    )
    professor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name="courses",
                                  limit_choices_to={'profile__is_prof': True},
                                  on_delete=models.CASCADE)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                      through="Repository",
                                      through_fields=("course", "student"))
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=5000)
    year = models.IntegerField()
    semester = models.IntegerField(choices=SEMESTER)
    attachments = models.FileField(blank=True,
                                   upload_to="uploads/course/%Y/%m/%d/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s %s교수님" % (
            self.year,
            self.SEMESTER[self.semester][1],
            self.title,
            self.professor.profile.name)

    @property
    def full_semester(self):
        return "%s %s" % (self.year, self.SEMESTER[self.semester][1])


class Repository(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                limit_choices_to={'profile__is_prof': False},
                                on_delete=models.CASCADE)
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s's repository" % (
            self.course.full_semester,
            self.course.title,
            self.student.profile.name)


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=5000)
    attachments = models.FileField(blank=True,
                                   upload_to="uploads/assignment/%Y/%m/%d/")
    deadline = models.DateTimeField()
    is_test = models.BooleanField(default=False)
    test_time = models.FloatField(default=2)
    test_file_name = models.CharField(max_length=100)
    test_input = models.TextField(max_length=5000, blank=True)
    test_output = models.TextField(max_length=5000, blank=True)
    test_langids = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s" % (
            self.course.full_semester,
            self.course.title,
            self.title)


def update_filename(instance, filename):
    import os
    path = "uploads/test_history/%Y/%m/%d/" + str(instance.assignment.id) + "/"
    filename = instance.student.profile.sid + "-" + filename
    return os.path.join(path, filename)


class Submission(models.Model):
    LANG_CHOICES = (
        (0, "Python"),
        (1, "Ruby"),
        (2, "Clojure"),
        (3, "PHP"),
        (4, "Javascript"),
        (5, "Scala"),
        (6, "Go"),
        (7, "C,C++"),
        (8, "Java"),
        (9, "VB.NET"),
        (10, "C#"),
        (11, "Bash"),
        (12, "Objective-C"),
        (13, "MySQL"),
        (14, "Perl"),
    )
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                limit_choices_to={'profile__is_prof': False},
                                on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment,
                                   on_delete=models.CASCADE)
    is_passed = models.BooleanField(default=False)
    is_working = models.BooleanField(default=True)
    is_last_submission = models.BooleanField(default=True)
    has_error = models.BooleanField(default=False)
    raw_code = models.FileField(upload_to=update_filename, blank=True)
    code = models.TextField(max_length=5000, blank=True)
    langid = models.IntegerField(choices=LANG_CHOICES, null=True, blank=True)
    errors = models.TextField(max_length=5000, blank=True)
    output = models.TextField(max_length=5000, blank=True)
    time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s" % (self.id, self.assignment, self.student.profile)

    def save(self, *args, **kwargs):
        Submission.objects.filter(student=self.student) \
            .update(is_last_submission=False)
        super(Submission, self).save(*args, **kwargs)
