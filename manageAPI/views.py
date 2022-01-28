from django.shortcuts import render
from newBackend import myResponse
from rest_framework.views import APIView
from wxapi import models as md
from . import models
import bcrypt,hashlib
# Create your views here.
def loginCheck(func):
    def decorated(self, *args, **kwargs):
        request = args[0]
        if 'user' not in request.session or request.session['user'] == "":
            return myResponse.AuthError("未登录")
        else:
            return func(self, *args, **kwargs)
    return decorated

#register权限 auth: 1 普通用户 2 社团其它部门成员 3 系维成员 4 管理员 5 root
#权限初始化为1 暂时直接由数据库改权限
class register(APIView):
    def post(self,request):
        data = request.data
        username = data['username']
        password = hashlib.sha512(data['password'].encode("utf8")).hexdigest()
        salt = bcrypt.gensalt()
        saltStr = salt.hex()
        password_with_salt = bcrypt.hashpw(str(password).encode("utf8"),salt).hex()
        account = models.User.objects.filter(username = username)
        if account.count() == 0:
            models.User(
                username=username,
                passwordHashWithSalt=password_with_salt,
                salt=saltStr,
                auth=1,
                nickname="normal",
            ).save()
            return myResponse.OK("成功注册用户")
        else:
            return myResponse.Error("用户名已存在")

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
        hash_hex = hash.hex()
        #if hash.hex() != account.passwordHashWithSalt:
        if hash_hex[0:58] != account.salt:
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
    def post(self,request):#创建事件表
        try:
            #data = request.query_params
            data = request.data
            uuid = data["uuid"]
            username = data["username"]
            print(uuid,username)
            this = models.DealAppointment.objects.filter(manage_username_id=username,appointment_uuid_id=uuid)
            print(this)
            if this.count() == 0:
                models.DealAppointment(
                    manage_username_id=username,
                    appointment_uuid_id=uuid,
                    status=1,
                ).save()
            else:
                this.delete()
                models.DealAppointment(
                    manage_username_id=username,
                    appointment_uuid_id=uuid,
                    status=1,
                ).save()
            return myResponse.OK(msg="成功创建事件表")
        except Exception as e:
            print("%s"%e)
            return myResponse.Error(msg="事件表创建失败")
        finally:
            pass

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

class myAppointment(APIView):
    def post(self,request):
        try:
            appointments = []
            manageName = request.data['username']
            thisevent = models.DealAppointment.objects.filter(manage_username_id=manageName) #返回一个工作人员所有接的单的记录
            # print("I Love Len",str(len(thisevent)))
            for i in range(len(thisevent)):
                appointment_uuid = thisevent[i].appointment_uuid_id
                appointment_client = md.Appointment.objects.filter(uuid = appointment_uuid)  #在appointment中查找appointment记录
                appointments.append(dict(id=appointment_client[0].id,sourcesInfo=appointment_client[0].sourcesInfo,\
                                         problemType=appointment_client[0].problemType,applyTime=appointment_client[0].applyTime))
                #print(appointment_client[0].sourcesInfo[0])
            return myResponse.OK(msg="数据获取成功",data=dict(username=manageName,appointments=appointments))
        except Exception as e:
            print("%s"%e)
        return myResponse.Error(msg="数据获取失败")