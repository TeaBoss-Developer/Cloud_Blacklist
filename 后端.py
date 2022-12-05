import json
from types import MethodDescriptorType
import requests
import random
import os
from flask import Flask, jsonify,request,send_from_directory
from datetime import datetime
from Method import Method
import _thread
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
@app.route('/', methods=['GET'])
def home():
    mode = request.args.get("mode","heartbeat")
    reported_qq = request.args.get("rpted_qq","")
    report_qq = request.args.get("rpt_qq","")
    reason = request.args.get("reason","")
    url = request.args.get("url","")#多个url用|分割
    cheak_p = request.args.get("cheak_qq","")
    password = request.args.get("pwd","")
    task_id = request.args.get("task_id","")
    ban_reason = request.args.get("b_reason","")
    img_name = request.args.get("img_name","")
    #图片名规则 举报人QQ-任务编号-Random数字(5位)
    #任务保存文件TaskList.txt  格式[任务编号]_[被举报QQ]_[举报QQ]_[原因] 多个url使用|分割
    #通过任务后数据保存文件 被举报QQ.txt  格式:[任务编号]_[举报QQ]_[原因]_[审核员ID]_审核原因 多个url使用|分割
    #----审核端----
    #正确返回 {"task_count":[任务数] , "complete_count" : [完成任务数],"未处理开始ID" : [需要处理的第一个] , "msg" : "请用/?mode=readtask&task_id=[处理id]&ac=[账号]&pwd=[密码]"}
    #返回 3 当前无任务
    #返回 4 服务器繁忙
    #返回 5 管理端登录返回 不存在账户
    #返回 6 密码错误
    #返回 7 账号封禁
    if(mode == "getkey"):
        array_datetime = str(datetime.now()).split(" ")[0].split("-");
        strs = str(int(array_datetime[0])*1.5).replace('.','')+str(int(array_datetime[1])*5)+str(int(array_datetime[2])*8)+str(int(gethour())*4)
        return(strs)
    if(mode == "report"):
        read = open("TaskList.txt","r")
        yuan = read.read()
        read.close()
        if(reported_qq == "" or report_qq == "" or reason == "" or url==""):
            return jsonify({"状态码" : 400, "问题" : "有参数为空" ,"msg" : "请检查您的数据,主要问题已显示在前面."})
        if(reported_qq not in yuan):
            taskid = Get_Task_id()
            string = taskid+"_"+reported_qq+"_"+report_qq+"_"+reason+"\n";
            file = open("TaskList.txt",'a');
            file.write(string)
            file.close()
            return jsonify({"状态码" : 200, "任务编号" : taskid ,"msg" : "提交成功啦~感谢您为净化网络环境所做的贡献.wp必司马"})
        if(reported_qq in yuan and os.path.exists(reported_qq+".txt")):
            return jsonify({"状态码" : 2,"msg" : "该用户已经举报且审核通过"})
        if(not os.path.exists(reported_qq+".txt")):
            return jsonify({"状态码" : 1,"msg" : "该用户已经举报但尚未审核"})
    if(mode == "read"):
        if(not os.path.exists(reported_qq+".txt")):
            return jsonify({"状态码" : 404,"msg" : "您所查询的QQ未存在档案"})
        else:
            file = open(reported_qq+".txt","r")
            read= file.read()
            file.close()
            ar = read.split("_")
            return jsonify({"状态码" : 200 , "任务编号" : ar[0],"举报QQ" : ar[2],"原因" : ar[3],"URL":ar[3],"审核员":ar[4],"审核原因" : ar[5]})
    if(mode == "reads"):
        if(os.path.exists(reported_qq+".txt")):
            return({"stauts" : True})
        else:
            return({"stauts" : False})
    if(mode == "cheakorders"):
        ar = open("TaskList.txt",'r').read().split("\n")
        return jsonify({"状态码" : 200 ,"task_count":len(ar), "complete_count" : Get_Com_Task(),"未处理开始ID" : ar[0].split("_")[0] , "msg" : "请用/?mode=readtask&ac=[账号]&pwd=[密码]进行读取第一条任务"})
    if(mode == "readtask"):
        file = open("TaskList.txt",'r').read().split("\n")[0].split("_")
        return jsonify({"状态码" : 200 ,"任务编号" : file[0] ,"举报人QQ" : file[1] , "被举报人" : file[2], "举报原因" : file[3]})
    if(mode == "uploadimg"):
        if("|" in url):
            ar = url.split("|")
            for urll in ar:
                Method.download_web(urll,Method.RunPath()+"\\图片\\"+reported_qq+"_"+Random_key()+".jpg")
        else:
            Method.download_web(url,Method.RunPath()+"\\图片\\"+reported_qq+"_"+Random_key()+".jpg")
        return jsonify({"状态" : "Success"})
    if(mode == "getimg"):
        return send_from_directory("图片\\",img_name)
    if(mode == "listdir"):
        return(str(os.listdir(Method.RunPath()+"\\图片\\")))
    if(mode == "reg"):
        if(reason == Get_Key()):
            Method.WriteIni(Method.RunPath()+"\\账号","审核员","User",cheak_p)
            Method.WriteIni(Method.RunPath()+"\\账号","审核员","PWD",password)
            return jsonify({"状态码" : 200 , "信息" : "注册成功"})
    else:
        return jsonify({"状态码" : -1, "问题" : "模式错误" ,"msg" : "请检查您上传的数据,主要问题已显示在前面."})
def Get_Key():
    array_datetime = str(datetime.now()).split(" ")[0].split("-");
    strs = str(int(array_datetime[0])*1.5).replace('.','')+str(int(array_datetime[1])*5)+str(int(array_datetime[2])*8)+str(int(gethour())*4)
    return(strs)
def Get_Task_id():
    array_datetime = str(datetime.now()).split(" ")[0].split("-");
    re = array_datetime[0]+array_datetime[1]+array_datetime[2]+Random_key()
    return(re)
def Get_Com_Task():
    num = 0
    ar = os.listdir(Method.RunPath()+"\\图片\\")
    for i in ar:
        if(".txt" in i):
            num+=1
    return(num)
def Random_key():
    list = ["0","1","2","3","4","5","6","7","8","9"]
    s = ""
    a=1
    while(a<=5):
        s+=random.choice(list)
        a+=1
    return(s)
def gethour():
    return(str(datetime.now()).split(":")[0].split("-")[2].split(" ")[1])
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2220)