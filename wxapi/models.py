
from django.db import models

# Create your models here.

class TimeSlot(models.Model):
    Date = models.DateField(blank=False)
    Start = models.DateTimeField(blank=False)
    End = models.DateTimeField(blank=True, null=True)
    AllowNumber = models.IntegerField(blank=False)
    def __str__(self):
        return str(self.id) + "-" + self.Date.strftime("%Y-%m-%d %w") + " " + str(
            self.Start.strftime("%H:%M:%S")) + "-" + (self.End).strftime("%H:%M:%S")


class Appointment(models.Model):
    uuid = models.CharField(max_length=100)
    openID = models.CharField(max_length=100)
    sourcesInfo = models.JSONField(null=True)
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    problemType = models.CharField(max_length=200, default="")
    describe = models.TextField()
    applyTime = models.DateTimeField(auto_now_add=True, null=True)
    status = models.IntegerField(default=1)
    """
    0:预约取消
    1:预约成功
    2:签到成功
    3:正在维修
    4:维修完成
    5:预约失效
    """



class mainProblemType(models.Model):
    type = models.CharField(max_length=200, default="")
    message = models.TextField(default="",blank=True)

    def __str__(self):
        return self.type


class subProblemType(models.Model):
    type = models.CharField(max_length=200, default="")
    mainType = models.ForeignKey(mainProblemType, on_delete=models.CASCADE)
    def __str__(self):
        return self.mainType.type + "-" + self.type