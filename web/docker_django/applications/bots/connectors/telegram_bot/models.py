from django.db import models


class Question(models.Model):
    TYPE_DO = 1
    TYPE_AM = 2
    TYPE_IN = 3
    TYPES = (
        (TYPE_DO, 'type_do'),
        (TYPE_AM, 'type_am'),
        (TYPE_IN, 'type_in'),
    )

    type_question = models.PositiveSmallIntegerField(
        choices=TYPES, null=True)
    question_text = models.CharField(max_length=200)
    answer_text = models.CharField(max_length=200)
    cost = models.PositiveSmallIntegerField()


class UsersQuestion(models.Model):
    user_id = models.PositiveIntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)


class UserInformation(models.Model):
    user_id = models.PositiveIntegerField()
    date_registered = models.DateField()
    score = models.PositiveIntegerField()
