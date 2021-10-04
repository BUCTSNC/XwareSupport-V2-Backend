from os import name
from django.db.models import fields
from newBackend.settings import TIME_ZONE
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from wxapi.models import *
import datetime,time
from django.utils import timezone

class mainProblemSerializers(ModelSerializer):
    class Meta:
        model = mainProblemType
        fields = ['id', 'type', 'subs', "message"]

    subs = serializers.SerializerMethodField()

    def get_subs(self, data):
        ret = []
        allsub = subProblemType.objects.filter(mainType_id=data.id)
        for sub in allsub:
            ret.append(sub.type)
        return ret


class subProblemSerializers(ModelSerializer):
    class Meta:
        model = subProblemType
        fields = ['type']


class timeSlotSerializers(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", 'date', 'slot', 'existAndContain']
    date = serializers.SerializerMethodField()
    slot = serializers.SerializerMethodField()
    existAndContain = serializers.SerializerMethodField()

    def get_date(self, data):
        return data.Date.strftime("%Y-%m-%d") + " " + "({})".format(numberToWeekDay(data.Date.strftime("%w")))

    def get_slot(self, data):
        return str(time.strftime("%H:%M:%S",time.localtime(data.Start.timestamp()))) + "-" + str(time.strftime("%H:%M:%S",time.localtime(data.End.timestamp())))

    def get_existAndContain(self, data):
        exist = Appointment.objects.filter(slot_id=data.id).count()
        return str(exist) + " / " + str(data.AllowNumber)

class appointmentSerializers(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id','problemType','status','timeSlot','uuid','name','stuNO']
    timeSlot = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    stuNO = serializers.SerializerMethodField()
    def get_timeSlot(self,data):
        slot = data.slot
        return slot.Date.strftime("%Y-%m-%d") + " " + "({})".format(numberToWeekDay(slot.Date.strftime("%w"))) +" "+\
        str(time.strftime("%H:%M:%S",time.localtime(slot.Start.timestamp()))) + "-" + \
        str(time.strftime("%H:%M:%S",time.localtime(slot.End.timestamp())))
    def get_name(self,data):
        return data.sourcesInfo['name']
    def get_stuNO(self,data):
        return data.sourcesInfo['stuNO']

class appointmentDetailSerializers(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id','problemType','status','timeSlot','uuid',"sourcesInfo",'timeSlot','describe','applyTime']
    timeSlot = serializers.SerializerMethodField()
    #bug
    def get_timeSlot(self,data):
        slot = data.slot
        return slot.Date.strftime("%Y-%m-%d") + " " + "({})".format(numberToWeekDay(slot.Date.strftime("%w"))) +" "+\
        str(time.strftime("%H:%M:%S",time.localtime(slot.Start.timestamp()))) + "-" + \
        str(time.strftime("%H:%M:%S",time.localtime(slot.End.timestamp())))


def numberToWeekDay(num):
    dic = {
        "1": "星期一",
        "2": "星期二",
        "3": "星期三",
        "4": "星期四",
        "5": "星期五",
        "6": "星期六",
        "0": "星期日",
    }
    return dic[num]
