from requests.api import request
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
import json,requests,time,datetime
from wxapi import myResponse
from wxapi.serializer import timeSlotSerializers,mainProblemSerializers,appointmentSerializers,appointmentDetailSerializers
from wxapi import models
import uuid
appConfigs = json.load(open("./appConfig.json","r")) # 读取微信小程序appID与appSecret
# Create your views here.

# 登录检查装饰器
def loginCheck(func):
    def decorated(self, *args, **kwargs):
        request = args[0]
        if 'openID' not in request.session or request.session['openID'] == "":
            return myResponse.AuthError("未登录")
        else:
            return func(self, *args, **kwargs)
    return decorated

class login(APIView):
    def get(self,request):
        return Response({'code':200})

    def post(self,request):
        data = request.data
        if 'jscode' not in data:
            return myResponse.Error("无jscode")
        wxRes = json.loads(requests.get(
            "https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code"
            .format(appConfigs['appId'],appConfigs['appSecret'],data['jscode'])
        ).text)
        request.session['openID'] = wxRes['openid'] #记录session
        return myResponse.OK(msg="登陆成功")


class TimeslotList(APIView):
    def get(self, request):
        now = datetime.datetime.now()
        timeslots = models.TimeSlot.objects.filter(End__gte=now)
        ret = []
        for slot in timeslots:
            nowAppointCount = slot.appointment_set.count()
            if slot.AllowNumber > nowAppointCount:
                ret.append(slot)
        if len(ret) == 0:
            return myResponse.Error("当前无可用时间段")
        return myResponse.OK(data=timeSlotSerializers(ret, many=True).data)

        
class ProblemType(APIView):
    def get(self, request):
        problemtypes = models.mainProblemType.objects.all()
        ser = mainProblemSerializers(problemtypes, many=True)
        data = ser.data
        return myResponse.OK(data=data)

class Appointment(APIView):
    def get(self, request):
        try:
            uuid = request.query_params['uuid']
            thisAppointment = models.Appointment.objects.get(uuid = uuid)
        except:
            return myResponse.Error("无uuid或无此预约")
        if thisAppointment.openID != request.session['openID']:
            return myResponse.AuthError("您无权查看该预约")
        return myResponse.OK(data=appointmentDetailSerializers(thisAppointment).data)
    @loginCheck
    def post(self, request):
        rawData = dict(request.data)
        try:
            sourcesInfo = rawData['info']
            problemType = rawData['form']['problemType']
            problemDetail = rawData['form']['problemDetail']
        except:
            return myResponse.Error("信息未填写成功")
        try:
            thisTimeslot = models.TimeSlot.objects.get(id = rawData['form']['timeSlotId'])
        except:
            return myResponse.Error("时间端获取失败")
        UUID = uuid.uuid3(uuid.NAMESPACE_OID,json.dumps(sourcesInfo)+str(time.time()))
        #获取提交表单本地时间
        applyTime = str(thisTimeslot)
        applyTime = applyTime[2:12] + applyTime[14:]
        newAppointment = models.Appointment(
            uuid=UUID,
            openID=request.session['openID'],
            sourcesInfo=sourcesInfo,
            problemType=problemType,
            describe=problemDetail,
            status=1,
            applyTime=applyTime,
            slot=thisTimeslot
        )
        newAppointment.save()
        return myResponse.OK(msg="预约成功",data={"newAppointmentID":newAppointment.id})

    @loginCheck
    def put(self, request):
        rawData = dict(request.data)
        try:
            uuid = rawData['uuid']
            thisAppointment = models.Appointment.objects.get(uuid=uuid)
        except Exception as e:
            # print("probleme=", e)
            return myResponse.Error("无uuid或无此预约")
        if thisAppointment.openID != request.session['openID']:
            return myResponse.AuthError("您无权操作该预约")

        try:
            sourcesInfo = rawData['info']
            problemType = rawData['form']['problemType']
            problemDetail = rawData['form']['problemDetail']
            new_slot_id = rawData['form']['timeSlotId']
            old_id = thisAppointment.id
        except:
            return myResponse.Error("信息未填写成功")
        try:
            thisTimeslot = models.TimeSlot.objects.get(id=rawData['form']['timeSlotId'])
        except:
            return myResponse.Error("时间端获取失败")
        #获取提交表单本地时间
        submitTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #获取预约时间段
        applyTime = str(thisTimeslot)
        applyTime = applyTime[2:12] + applyTime[14:]
        modifiedAppointment = models.Appointment(
            uuid=uuid,
            openID=request.session['openID'],
            sourcesInfo=sourcesInfo,
            problemType=problemType,
            describe=problemDetail,
            status=1,
            slot_id=new_slot_id,
            submitTime=submitTime,
            applyTime=applyTime,
            id=old_id #保证修改时的id不变
        )
        modifiedAppointment.save()
        return myResponse.OK(data=appointmentDetailSerializers(modifiedAppointment).data)

    @loginCheck
    def delete(self, request):
        try:
            uuid = request.query_params['uuid']
            thisAppointment = models.Appointment.objects.get(uuid=uuid)
        except:
            return myResponse.Error("无uuid或无此预约")
        if thisAppointment.openID != request.session['openID']:
            return myResponse.AuthError("您无权操作该预约")
        thisAppointment.status = 0
        thisAppointment.save()
        return myResponse.OK(data=appointmentDetailSerializers(thisAppointment).data)

class myAppointmentList(APIView):
    @loginCheck
    def get(self,request):
        Appointments = models.Appointment.objects.filter(openID = request.session['openID'])
        return myResponse.OK(data=appointmentSerializers(Appointments,many=True).data)

# class getPersonalInfo(APIView):
#     @loginCheck
#     def get(self,request):
#         try:
#             uuid = request.query_params['uuid']
#             # print("getPersonalInfo-uuid:",uuid)
#             thisAppointment = models.Appointment.objects.get(uuid=uuid)
#             #print(thisAppointment.sourcesInfo)
#         except:
#             return myResponse.Error("无uuid或无此预约")
#         return myResponse.OK(data=dict(personalInfo=thisAppointment.sourcesInfo,problemType=thisAppointment.problemType,timeSlotId=thisAppointment.slot_id,describe=thisAppointment.describe,applyTime=thisAppointment.applyTime))
#
#
#
#
