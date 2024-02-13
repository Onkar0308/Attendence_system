from django.db import models

class Scanner(models.Model):
    code = models.CharField(max_length=100, unique=True)
    attendance_marked = models.BooleanField(default=False)

    class Meta:
        db_table = "Scanner"

    def __str__(self):
        return self.code
