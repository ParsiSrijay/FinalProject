from datetime import date
from django.shortcuts import render,redirect
import joblib
import numpy as np
from addshg.models import shg,installments,Loan
from twilio.rest import Client
from dateutil.relativedelta import *
from django.core import serializers
from django.http import HttpResponse

def signup(request):
    account_sid = 'ACcfa9f9139b29fd65341fee0d30afa33c'
    auth_token = 'd8c6b36ab9de7720cfe2366ddcf088e8'
    client = Client(account_sid, auth_token)
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    user=request.user.username
    if request.method == 'POST':
        if request.POST["action"]=="approve":
            print("1")
            name = request.POST['name']
            act = request.POST['act']
            amount = request.POST['amt']
            woman = request.POST['wb']
            location = request.POST['location']
            tp = request.POST['tp']
            rate = request.POST['rate']
            pd = request.POST['pd']
            ycj = request.POST['ycj']
            phno = request.POST['phno']
            phone = "+91"+str(phno)
            today = date.today()
            duedate = today + relativedelta(months=+1)
            client.messages.create(to=phone,
                                       from_="+16783593096",
                                       body="Loan Approved")
            s = shg(Name=name, Activity=act, Amount=amount, BalanceAmount=amount, Woman_beneficiaries=woman,
                        Location=location, TimePeriod=tp, Rate=rate, Registration_id_imo=request.user.username,
                        phno=phone,InstallDueDate=duedate)
            s.save()
            lr = Loan(Name=name, OpeningBalance=amount, LoanRepayment=0, Interest=0, ClosingBalance=amount,
                          RegIMO=request.user.username)
            lr.save()
            return render(request, 'approveSHG.html', {'content': "Loan Approved Successfully!", "reg": user})
        if request.POST['action']=="reject":
            phno = request.POST['phno']
            phone = "+91"+str(phno)
            client.messages.create(to=phone,
                                   from_="+16783593096",
                                   body="Loan Rejected")
            return render(request, 'approveSHG.html', {'content': "Loan Rejected!", "reg": user})
        if request.POST['action']=="check":
            name=request.POST['name']
            act=request.POST['act']
            amount=request.POST['amt']
            amt=int(amount)*100000
            woman=request.POST['wb']
            location=request.POST['location']
            tp=request.POST['tp']
            rate=request.POST['rate']
            reg=request.user.username
            pd=request.POST['pd']
            ycj=request.POST['ycj']
            phno=request.POST['phno']
            phno=str(phno)
            phone="+91"+phno
            action=act
            if pd=='Yes' or pd=='yes' or pd=='y':
                pd=1
            else:
                pd=0
            if act=='Tailoring':
                act=1
            elif act=='Handicraft':
                act=2
            elif act=='Handloom':
                act=3
            elif act=='Agriculture':
                act=4
            elif act=='Diary Activities':
                act=5
            elif act == 'Food Processing':
                act = 6
            else:
                act=7
                action="Others"
            today=date.today()
            duedate = today + relativedelta(months=+1)
            model = joblib.load('C:/Users/P SRIJAY/Desktop/sih/imo1.pkl')
            x=[int(amount),int(woman),int(ycj),int(tp),act,pd]
            x=np.array(x)
            x=x.reshape(1,-1)
            y_test=model.predict(x)
            if y_test[0]==1:
                return render(request, 'SHG.html',
                              {"YOE": ycj, "PD": pd, "Name": name, "Activity": action, "Amount": amt,
                               "Woman_beneficiaries": woman, "Location": location, "TimePeriod": tp, "Rate": rate,
                               "phno": phno,"Content":"Loan Accepted!!"})
            else:
                return render(request,'SHG.html',{"Content":"Loan Rejected!!","YOE":ycj,"PD":pd,"Name":name,"Activity":action,"Amount":amt,"Woman_beneficiaries":woman,"Location":location,"TimePeriod":tp,"Rate":rate,"phno":phno})
    else:
        return render(request,'approveSHG.html',{"reg":user})


def display(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    list_shg=shg.objects.values('Name','Amount','BalanceAmount','Activity','Score').filter(Registration_id_imo=request.user.username)
    list_misess=[]
    for i in list_shg:
        p=(10-i['Score'])
        list_misess.append(p)
    j=0
    s=[]
    for i in list_shg:
        dict={}
        dict['Name']=i['Name']
        dict['Amount']=i['Amount']
        dict['BalanceAmount']=i['BalanceAmount']
        dict['Activity']=i['Activity']
        dict['misses']=list_misess[j]
        j=j+1
        s.append(dict)
    return render(request,"displaySHG.html",{'shg':s})


def payinstallments(request):
    account_sid = 'ACcfa9f9139b29fd65341fee0d30afa33c'
    auth_token = 'd8c6b36ab9de7720cfe2366ddcf088e8'
    client = Client(account_sid, auth_token)
    list_shg=shg.objects.values('Name').filter(Registration_id_imo=request.user.username)
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    if request.method=='POST':
        id=request.POST['id']
        name=request.POST['Name']
        inst=request.POST['installments']
        reg=request.POST['reg']
        s=shg.objects.get(Name=name,Registration_id_imo=reg)
        openbal=s.BalanceAmount
        loaninst=inst
        rate=s.Rate/12
        time=s.TimePeriod
        interest= (openbal*rate*time)/100
        closebal=openbal-int(loaninst)+interest
        s.BalanceAmount=closebal
        today=date.today()
        duedate = s.InstallDueDate + relativedelta(months=+1)
        phone="+"+str(s.phno)
        if today<=s.InstallDueDate:
            client.messages.create(to=phone,
                                   from_="+16783593096",
                                   body="Installment Paid next installment due date"+str(duedate))
            s.InstallDueDate=duedate
        else:
            s.Score=s.Score-1
            client.messages.create(to=phone,
                                   from_="+16783593096",
                                   body="Installment Paid Late.Please pay next installment in time. Next installment due date" + str(duedate))
            s.InstallDueDate = duedate
        s.save()
        t = installments(Name=name, Installments=int(inst), Registration_id_imo=request.user.username)
        t.save()
        lr=Loan(Name=name,OpeningBalance=openbal,LoanRepayment=inst,Interest=interest,ClosingBalance=closebal,RegIMO=request.user.username,InstallDueDate=duedate)
        lr.save()
        return redirect('http://127.0.0.1:8000/portal/display')
    else:
        return render(request,'installments.html',{"reg":request.user.username,"name":list_shg})

def dispLR(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    name_list = Loan.objects.raw('SELECT DISTINCT Name,id from addshg_loan WHERE RegIMO=%s',[request.user.username])
    l = []
    for i in name_list:
        if i.Name not in l:
            l.append(i.Name)
    if request.method=="POST":
        name=request.POST['name']
        lr=Loan.objects.all().filter(Name=name,RegIMO=request.user.username)
        return render(request,"form.html",{"shg":lr,"name_list":l})
    else:
        return render(request,"form.html",{"name_list":l})


