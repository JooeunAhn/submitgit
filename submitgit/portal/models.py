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
    key = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s's repository" % (
            self.course.full_semester,
            self.course.title,
            self.student.profile.name)

    def save(self, *args, **kwargs):
        from Crypto.Hash import SHA256
        import uuid
        seed = str(uuid.uuid4()).encode('utf-8')
        self.key = SHA256.new(seed).digest()
        super(Repository, self).save(*args, **kwargs)


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
    import uuid
    random_id = str(uuid.uuid4())
    path = "uploads/history/%s/" % (random_id,)
    filename = str(instance.student.profile.sid) + "-" + filename
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
        (7, "C"),
        (8, "Java"),
        (9, "VB.NET"),
        (10, "C#"),
        (11, "Bash"),
        (12, "Objective-C"),
        (13, "MySQL"),
        (14, "Perl"),
        (15, "C++"),
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
    raw_code = models.FileField(upload_to=update_filename,
                                blank=True)
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
        Submission.objects.filter(student=self.student,
                                  assignment=self.assignment) \
            .update(is_last_submission=False)
        super(Submission, self).save(*args, **kwargs)


class EncryptedCode(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                limit_choices_to={'profile__is_prof': False},
                                on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment,
                                   on_delete=models.CASCADE,
                                   related_name="encrypted")
    code = models.FileField(upload_to='/upload/ef/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from .crypto import encrypt
        repo = Repository.objects.get(student=self.student,
                                      course=self.assignment.course,
                                      is_verified=True)
        key = repo.key
        name = self.code.name
        enc_code = encrypt(key=key, data=self.code.file.file,
                           size=self.code.file.size)
        self.code.file.file = enc_code
        self.code.name = name + '.joon'
        """
        from .crypto import decrypt
        dec_code, size = decrypt(key=key, data=self.code.file.file)
        self.code.file.file = dec_code
        self.code.file.truncate(size)
        self.code.name = name
        """
        super(EncryptedCode, self).save(*args, **kwargs)
