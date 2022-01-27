from django.shortcuts import render
from newBackend import myResponse
from rest_framework.views import APIView
from wxapi import models as md
from . import models
import bcrypt
# Create your views here.
def loginCheck(func):
    def decorated(self, *args, **kwargs):
        request = args[0]
        if 'user' not in request.session or request.session['user'] == "":
            return myResponse.AuthError("未登录")
        else:
            return func(self, *args, **kwargs)
    return decorated


class login(APIView):
    def post(self,request):
        data = request.data
        username = data['username']
        password = data['password']
        account = models.User.objects.filter(username = username)
        if account.count() == 0:
            return myResponse.Error("无此账户或密码错误")
        account = account[0]
        hash = bcrypt.hashpw(password=password.encode("utf8"),salt=bytes.fromhex(account.salt))
        if hash.hex() != account.passwordHashWithSalt:
            return myResponse.Error("无此账户或密码错误")
        request.session['user'] = account.id
        return myResponse.OK("登录成功")
    
class signIn(APIView):
    @loginCheck
    def get(self,request):
        pass
    @loginCheck
    def post(self,request):
        data = request.data
        uuid = data['uuid']
        return myResponse.OK()

class scanCode(APIView):
    #@loginCheck
    def put(self,request):
        try:
            data = request.data
            uuid = data['uuid']
            #uuid = request.query_params['uuid']
            thisAppointment = md.Appointment.objects.get(uuid=uuid)
            if(thisAppointment.status == 1):
                thisAppointment.status = 2
            elif(thisAppointment.status == 2):
                return myResponse.Error("已签到")
            elif(thisAppointment.status >= 3):
                return myResponse.Error("已处理完成或用户已取消服务")
            thisAppointment.save()
        except:
            return myResponse.Error("无uuid或无此预约")
        return myResponse.OK(msg="签到成功")

class startService(APIView):
    #@loginCheck
    def put(self, request):
        try:
            data = request.data
            uuid = data['uuid']
            #uuid = request.query_params['uuid']
            thisAppointment = md.Appointment.objects.get(uuid=uuid)
            if (thisAppointment.status == 1):
                return myResponse.Error("请先签到")
            elif (thisAppointment.status == 2):
                thisAppointment.status = 3
            elif (thisAppointment >= 3):
                return myResponse.Error("已处理完成或用户已取消服务")
            thisAppointment.save()
        except:
            return myResponse.Error("无uuid或无此预约")
        return myResponse.OK(msg="开始服务")