from django.shortcuts import render
from newBackend import myResponse
from rest_framework.views import APIView
from wxapi import models as md
from . import models
import bcrypt,hashlib
import os,base64
import pdfcrowd
from django.http import HttpResponse

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
            for i in range(len(thisevent)):
                appointment_uuid = thisevent[i].appointment_uuid_id
                appointment_client = md.Appointment.objects.filter(uuid = appointment_uuid)  #在appointment中查找appointment记录
                appointments.append(dict(dealStatus=thisevent[i].status,id=appointment_client[0].id,sourcesInfo=appointment_client[0].sourcesInfo,\
                                         problemType=appointment_client[0].problemType,applyTime=appointment_client[0].applyTime,username=manageName,\
                                         uuid=appointment_uuid))
                #print(appointment_client[0].sourcesInfo[0])
            return myResponse.OK(msg="数据获取成功",data=dict(username=manageName,appointments=appointments))
        except Exception as e:
            print("%s"%e)
        return myResponse.Error(msg="数据获取失败")

class submitTicket(APIView):
    def get(self,request):
        print("get is starting")
        return myResponse.OK()

    def post(self,request):
        try:
            print("post is starting")
            data = request.data['dics']
            #处理图片路径
            img_urls = ""
            #存储模式 out_imgs/username/uuid/[imgs]
            if not os.path.exists("out_imgs"):
                os.system("mkdir out_imgs")
            if not os.path.exists("out_imgs/%s" % (data['username'])):
                os.system("mkdir out_imgs/%s" % (data['username']))
            if not os.path.exists("out_imgs/%s/%s" % (data['username'],data['uuid'])):
                os.system("mkdir out_imgs/%s/%s" % (data['username'],data['uuid']))
            else:
                import shutil#用于删除目录
                path = "mkdir out_imgs/%s/%s" % (data['username'],data['uuid'])
                shutil.rmtree(path)  # 删除目录 如果该目录非空也能删除
                os.system("mkdir out_imgs/%s/%s" % (data['username'], data['uuid']))

            len_url = len(data['imgurl'])
            for i in range(len_url):
                img_data = base64.b64decode(data['imgurl'][i][22:])
                img_url = "out_imgs/%s/%s/%s.png"%(data['username'],data['uuid'],i)
                if i != len_url - 1:
                    img_urls += (img_url+'#')
                else:
                    img_urls += img_url
                with open(img_url, "wb") as fh:
                    fh.write(img_data)
                    fh.close()

            print(len(data['imgurl']))


            thisAppointment = models.SummaryAppointment.objects.filter(appointment_uuid_id=data['uuid'],
                manage_username_id=data['username'])
            if thisAppointment.count() == 0:
                models.SummaryAppointment(
                    imgurl=img_urls,
                    problem=data['problem'],
                    problemType=data['problemType'],
                    inspection=data['inspection'],
                    processAndWays=data['processAndWays'],
                    finalEffect=data['finalEffect'],
                    companions=data['companions'],
                    appointment_uuid_id=data['uuid'],
                    manage_username_id=data['username'],
                    pcbrand=data['pcbrand'],
                    pcmodel=data['pcmodel'],
                ).save()
                # 修改用户Appointment状态
                thisAppointment2 = md.Appointment.objects.get(uuid=data['uuid'])
                thisAppointment2.status = 4
                thisAppointment2.save()
                # 修改服务端Appointment状态
                thisAppointment3 = models.DealAppointment.objects.get(appointment_uuid_id=data['uuid'],manage_username_id=data['username'])
                thisAppointment3.status = 2
                thisAppointment3.save()
                return myResponse.OK(msg="成功写入工单总结")
            else:
                #如果存在表单则修改记录
                thisAppointment1 = models.SummaryAppointment.objects.get(appointment_uuid_id=data['uuid'],manage_username_id=data['username'])
                thisAppointment1.imgurl=img_urls
                thisAppointment1.problem=data['problem']
                thisAppointment1.problemType=data['problemType']
                thisAppointment1.inspection=data['inspection']
                thisAppointment1.processAndWays=data['processAndWays']
                thisAppointment1.finalEffect=data['finalEffect']
                thisAppointment1.companions=data['companions']
                thisAppointment1.appointment_uuid_id=data['uuid']
                thisAppointment1.manage_username_id=data['username']
                thisAppointment1.pcbrand = data['pcBrand'],
                thisAppointment1.pcmodel = data['pcmodel'],
                thisAppointment1.save()
                #修改用户Appointment状态
                thisAppointment2 = md.Appointment.objects.get(uuid=data['uuid'])
                thisAppointment2.status = 4
                thisAppointment2.save()
                #修改服务端Appointment状态
                thisAppointment3 = models.DealAppointment.objects.get(appointment_uuid_id=data['uuid'],manage_username_id=data['username'])
                thisAppointment3.status = 2
                thisAppointment3.save()
                return myResponse.OK(msg="成功修改记录")
        except Exception as e:
            print("ERROR len(imgurl)=%d"%(len(img_urls)))
            print("ERROR MSG AS %s"%e)
            return myResponse.Error(msg="ERROR")

class download(APIView):
    def get(self,request):
        import pdfkit
        data = request.query_params
        uuid = data['uuid']
        username = data['username']


        # 第一个参数可以是列表，放入多个域名，第二个参数是生成的 PDF 名称
        config_pdf = pdfkit.configuration(wkhtmltopdf=r'D:\pdfkit\wkhtmltopdf\bin\wkhtmltopdf.exe')
        #config_pdf = pdfkit.configuration(wkhtmltopdf=r'/usr/local/bin/wkhtmltopdf')

        #pdf = pdfkit.from_url('http://39.107.139.29:8000/manageAPI/pdf?username=%s&uuid=%s'%(username,uuid), 'pdfdownload/search.pdf', configuration=config_pdf)
        pdf = pdfkit.from_url('http://127.0.0.1:8000/manageAPI/pdf?username=%s&uuid=%s' % (username, uuid),'pdfdownload/search.pdf', configuration=config_pdf)
        with open("pdfdownload/search.pdf",'rb') as f:
            pdfbytes = f.read()
            f.close()
        return HttpResponse(pdfbytes,content_type="application/pdf")

    def post(self,request):
        return myResponse.OK(msg="TESTING POST")


class createPdf(APIView):
    def get(self,request):
        print("pdf get")
        data = request.query_params
        print("老子是data:",data)
        UUID = data['uuid']
        USERNAME = data['username']
        print(UUID,USERNAME)
        try:
            thisAppointment1 = models.SummaryAppointment.objects.get(appointment_uuid_id=UUID,manage_username_id=USERNAME)
            #thisAppointment1 = models.SummaryAppointment.objects.get(appointment_uuid_id="fa246569-7a5e-3a12-8459-35accd3a5dd8",manage_username_id="kingdom")
            print(thisAppointment1.finalEffect)
            thisAppointment2 = md.Appointment.objects.get(uuid=UUID)
            b1 = b2 = b3 = b4 = '0'
            if "硬件" in thisAppointment1.problemType:
                b1 = '1'
            if '软件' in thisAppointment1.problemType:
                b2 = '1'
            if '网络' in thisAppointment1.problemType:
                b3 = '1'
            if b1=='0' and b2=='0' and b3=='0' or '其它' in thisAppointment1.problemType:
                b4 = '1'
        except Exception as e:
            print("E%s"%e)
        return render(request,r"templates/X-ware.html", {"brand": thisAppointment1.pcbrand,"model":thisAppointment1.pcmodel,"name":thisAppointment2.sourcesInfo['name'],
                                                         'stuNO':thisAppointment2.sourcesInfo['stuNO'],'phone':thisAppointment2.sourcesInfo['phone'],
                                                         'date':str(thisAppointment2.applyTime)[:10],'problem':thisAppointment1.problem,
                                                         'inspection':thisAppointment1.inspection,'processAndWays':thisAppointment1.processAndWays,
                                                         'finalEffect':thisAppointment1.finalEffect,'companions':thisAppointment1.companions,
                                                         'b1':b1,'b2':b2,'b3':b3,'b4':b4})


    def post(self,request):
        print("pdf post")
        data = request.data
        UUID = data['uuid']
        USERNAME = data['username']
        postdata = UUID+USERNAME
        print("postdata"+postdata)
        return render(request, r"template/new/X-ware.html", {"data": postdata})


        # client = pdfcrowd.HtmlToPdfClient('kingsdom', '4a02f83e3d2c26519d80cf227c1d180d')
        # pdf = client.convertUrlToFile("http:/39.107.139.29:8000/manageAPI/pdf","pdfdownload/123.pdf")
        #print("sss:"+pdf)
        # data = request.data
        # uuid = data['uuid']
        # username = data['username']
        # print("uuid:"+uuid,"username:"+username)

        #return myResponse.OK()

class modifyAppointment(APIView):
    def delete(self,request):
        try:
            data = request.data
            uuid = data['uuid']
            username = data['username']
            #修改两个表单的状态
            thisAppointment1 = models.DealAppointment.objects.get(appointment_uuid_id=uuid,manage_username_id=username)
            thisAppointment1.status = 0
            thisAppointment1.save()

            thisAppointment2 = md.Appointment.objects.get(uuid=uuid)
            thisAppointment2.status = 0
            thisAppointment2.save()

            return myResponse.OK(msg="cancelwork success")
        except Exception as e:
            return myResponse.Error(msg=e)

    def post(self,request):
        try:
            uuid = request.data['uuid']
            username = request.data['username']
            thisAppointment = models.SummaryAppointment.objects.get(appointment_uuid_id=uuid,manage_username_id=username)
            return myResponse.OK(msg="getDataSuccess",data=dict(problem=thisAppointment.problem, problemType=thisAppointment.problemType, \
                                inspection=thisAppointment.inspection, process=thisAppointment.processAndWays,finalEffect=thisAppointment.finalEffect, \
                                companions=thisAppointment.companions, pcbrand=thisAppointment.pcbrand,pcmodel=thisAppointment.pcmodel,uuid=thisAppointment.appointment_uuid_id,\
                                username=thisAppointment.manage_username_id))
        except Exception as e:
            print("ERROR %s"%e)
            return myResponse.OK(msg="初始化",
                                 data=dict(problem="", problemType="", inspection="",process="",finalEffect="", companions="", pcbrand="",\
                                           pcmodel="", uuid="",username=""))



