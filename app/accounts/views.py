from django.shortcuts import render, redirect
from .models import ledger, Payments, Receipts
from django.db.models import Avg, Count, Min, Sum, Max
# Create your views here.
from addshg.models import Loan, shg
from django.core import serializers
from django.http import HttpResponse
from dateutil.parser import parse
from datetime import datetime,date
from accounts.utils import render_to_pdf


def first(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    if request.method == "POST":
        account_name = request.POST['account']
        transctionType = request.POST['TransctionType']
        particulars = request.POST['particulars']
        amount = request.POST['amount']
        if account_name == "" or particulars == "" or amount == 0:
            return render(request, 'ledger.html', {"failure": "All the fields need to be entered"})
        l = ledger(AccountName=account_name, TransctionType=transctionType, Particulars=particulars, Amount=amount,
                   RegIMO=request.user.username)
        l.save()
        if transctionType=="Debit":
            l = ledger(AccountName=particulars, TransctionType="Credit", Particulars=account_name, Amount=amount,
                       RegIMO=request.user.username)
            l.save()
        else:
            l = ledger(AccountName=particulars, TransctionType="Debit", Particulars=account_name, Amount=amount,
                       RegIMO=request.user.username)
            l.save()
        return render(request, 'ledger.html', {"success": "Account Statement Added"})
    return render(request, 'ledger.html')


def disp(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    list_accounts = ledger.objects.raw('SELECT DISTINCT AccountName,id from accounts_ledger WHERE RegIMO=%s',
                                       [request.user.username])
    l = []
    for i in list_accounts:
        if i.AccountName not in l:
            l.append(i.AccountName)

    bal = []
    t = []
    if (request.method == "POST"):
        AccountName = request.POST['AccountName']
        Account = ledger.objects.all().filter(AccountName=AccountName, RegIMO=request.user.username)
        debit=0
        total=0
        credit=0
        ans=''
        for i in Account:
            if i.TransctionType=="Debit":
                debit=i.Amount
                total+=debit
            else:
                credit=i.Amount
                total-=credit
            if total<0:
                ans=str(abs(total))+' Cr'
            else:
                ans=str(total)+' Dr'


            bal.append(ans)
        k=1
        for i, j in zip(Account, bal):
            t.append({'i': i, 'j': j,'s':k})
            k+=1

        return render(request, 'dispLedger.html', {'list': l, 'name': AccountName, 'account': Account, 't': t})
    else:
        return render(request, 'dispLedger.html', {'list': l, 't': t})


def edit(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    edit_details = ledger.objects.filter(RegIMO=request.user.username)
    if request.method == "POST":
        if "edit-button" in request.POST:
            acc = request.POST["account"]
            ttype = request.POST["TransctionType"]
            part = request.POST["particulars"]
            amt = request.POST["amount"]
            l = ledger(AccountName=acc, TransctionType=ttype, Particulars=part, Amount=amt,
                       RegIMO=request.user.username)
            l.save()
            if ttype == "Debit":
                l = ledger(AccountName=part, TransctionType="Credit", Particulars=acc, Amount=amt,
                           RegIMO=request.user.username)
                l.save()
            else:
                l = ledger(AccountName=part, TransctionType="Debit", Particulars=acc, Amount=amt,
                           RegIMO=request.user.username)
                l.save()
            return render(request, "edit.html", {"success": "Successfully Updated"})
        acc = request.POST["account"]
        ttype = request.POST["TransctionType"]
        part = request.POST["particulars"]
        amt = request.POST["amount"]
        edit_l = ledger.objects.filter(AccountName=acc, TransctionType=ttype, Particulars=part, Amount=amt,
                                       RegIMO=request.user.username).delete()
        if ttype == "Debit":
            edit_l = ledger.objects.filter(AccountName=part, TransctionType="Credit", Particulars=acc,
                                           Amount=amt, RegIMO=request.user.username).delete()
        else:
            edit_l = ledger.objects.filter(AccountName=part, TransctionType="Debit", Particulars=acc,
                                           Amount=amt, RegIMO=request.user.username).delete()
        if request.POST["action"] == "delete":
            return render(request, "edit.html", {"success": "Successfully Deleted"})
        return render(request, "dispedit.html", {"an": acc, "tt": ttype, "part": part, "amt": amt})
    return render(request, "edit.html", {"details": edit_details})


def receipts(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    if request.method == 'POST':
        mem = request.POST['Memfees']
        fines = request.POST['Fines']
        rmkfunds = request.POST['Rmkfunds']
        prin = request.POST['Principal']
        intr = request.POST['Interests']
        openbal = request.POST['Openingbal']
        shgloans = request.POST['Shgloans']
        fees = request.POST['Feesandcharges']
        misc = request.POST['Misc']
        sal = request.POST['Salaries']
        adexp = request.POST['Adminexpenses']
        stat = request.POST['Stationery']
        mis = request.POST['Micellaneous']
        closingbal = request.POST['closingbal']
        p = Payments(Shgloans=shgloans, Closingbal=closingbal, Feesandcharges=fees, Salaries=sal, Adminexpenses=adexp,
                     Stationery=stat, Micellaneous=mis, RegIMO=request.user.username)
        p.save()
        r = Receipts(Memfees=mem, Fines=fines, Rmkfunds=rmkfunds, Principal=prin, Interests=intr, Openingbal=openbal,
                     RegIMO=request.user.username, Micellaneous=misc)
        r.save()
        return render(request, "receipts.html", {"content": "Successfully Added"})
    else:
        amt = Loan.objects.filter(RegIMO=request.user.username).aggregate(princ=Sum('LoanRepayment'))
        intr = Loan.objects.filter(RegIMO=request.user.username).aggregate(interest=Sum('Interest'))
        ShgLoan = shg.objects.filter(Registration_id_imo=request.user.username).aggregate(shgl=Sum('Amount'))
        principal_amount = amt['princ']
        total_intr = intr['interest']
        amt = ShgLoan['shgl']
        return render(request, "receipts.html", {"principal": principal_amount, "interest": total_intr, "Amount": amt})


def RandPDisplay(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    total = Receipts.objects.filter(RegIMO=request.user.username).aggregate(ob=Max('Openingbal'), mf=Sum('Memfees'),
                                                                            fines=Sum('Fines'), rf=Sum('Rmkfunds'),
                                                                            ms=Sum('Micellaneous'))
    total_amt = Loan.objects.filter(RegIMO=request.user.username).aggregate(princ=Sum('LoanRepayment'),
                                                                            interest=Sum('Interest'))
    pay_total = Payments.objects.filter(RegIMO=request.user.username).aggregate(cb=Min('Closingbal'),
                                                                                shgl=Sum('Shgloans'),
                                                                                fac=Sum('Feesandcharges'),
                                                                                sal=Sum('Salaries'),
                                                                                ae=Sum('Adminexpenses'),
                                                                                sta=Sum('Stationery'),
                                                                                ms=Sum('Micellaneous'))
    total_loan = shg.objects.filter(Registration_id_imo=request.user.username).aggregate(shgl=Sum('Amount'))
    receipts_total = total['ob'] + total['mf'] + total['fines'] + total['rf'] + total['ms'] + total_amt['princ'] + \
                     total_amt['interest']
    payments_total = pay_total['cb'] + pay_total['fac'] + pay_total['sal'] + pay_total['ae'] + pay_total['sta'] + \
                     pay_total['ms'] + total_loan['shgl']
    if receipts_total > payments_total:
        ex = receipts_total - payments_total
        return render(request, "RPdisp.html",
                      {"RP": total, "RPAmt": total_amt, "PT": pay_total, "loan": total_loan, "excess1": ex,
                       "bal": receipts_total})
    else:
        ex = payments_total - receipts_total
        return render(request, "RPdisp.html",
                      {"RP": total, "RPAmt": total_amt, "PT": pay_total, "loan": total_loan, "excess2": ex,
                       "bal": payments_total})


def IandEDisplay(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    if request.method=="POST":
        From=request.POST["From"]
        From1=datetime.strptime(From, "%Y-%m-%d")
        From=datetime.strptime(From, "%Y-%m-%d").date()
        To=request.POST["To"]
        To1=datetime.strptime(To, "%Y-%m-%d")
        To=datetime.strptime(To, "%Y-%m-%d").date()
        int_dates=[]
        il=Loan.objects.values("Date").filter(RegIMO=request.user.username)
        for i in il:
            if i['Date'].date()>From and i['Date'].date()<=To and i['Date'] not in int_dates:
                int_dates.append(i['Date'])
        interest=0
        for i in range(len(int_dates)):
            inr=Loan.objects.filter(RegIMO=request.user.username,Date=int_dates[i]).aggregate(intr=Sum('Interest'))
            interest=inr['intr']+interest
        l=Receipts.objects.values("Date").filter(RegIMO=request.user.username)
        dates=[]
        mf=0
        fines=0
        ms=0
        for i in l:
            if i["Date"] > From and i["Date"]<=To and i['Date'] not in dates:
                dates.append(i["Date"])
        for i in range(len(dates)):
            m=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Memfees'))
            mf=mf+m['mf']
            f=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Fines'))
            fines=fines+f['mf']
            m=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Micellaneous'))
            ms=ms+m['mf']
        p=Payments.objects.values("Date").filter(RegIMO=request.user.username)
        datesp=[]
        fac=0
        sal=0
        ae=0
        ms1=0
        for i in p:
            if i['Date'] > From and i["Date"]<=To and i['Date'] not in datesp:
                datesp.append(i['Date'])
        for i in range(len(datesp)):
            f=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Feesandcharges'))
            fac=fac+f["fac"]
            s=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Salaries'))
            sal=sal+s['fac']
            a=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Adminexpenses'))
            ae=ae+a['fac']
            m=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Micellaneous'))
            ms1=ms1+m['fac']
        income=(interest+fines+mf+ms)
        exp=int(fac+sal+ae+ms1)
        total={}
        total['mf']=int(mf)
        total['fines']=int(fines)
        total['ms']=int(ms)
        total_amt={}
        total_amt["interest"]=int(interest)
        pay_total={}
        pay_total['fac']=int(fac)
        pay_total['sal']=int(sal)
        pay_total['ae']=int(ae)
        pay_total['ms']=int(ms1)
        if income>exp:
            ex=income-exp
            return render(request,"IEdisp.html",{"RP": total, "RPAmt": total_amt, "PT": pay_total, "excess1": ex, "bal": income,"From":From,"To":To})
        else:
            ex=exp-income
            return render(request, "IEdisp.html",
                          {"RP": total, "RPAmt": total_amt, "PT": pay_total, "excess2": ex, "bal": exp,"From":From,"To":To})
    total_amt = Loan.objects.filter(RegIMO=request.user.username).aggregate(interest=Sum('Interest'))
    total = Receipts.objects.filter(RegIMO=request.user.username).aggregate(mf=Sum('Memfees'), fines=Sum('Fines'),
                                                                            ms=Sum('Micellaneous'))
    pay_total = Payments.objects.filter(RegIMO=request.user.username).aggregate(fac=Sum('Feesandcharges'),
                                                                                sal=Sum('Salaries'),
                                                                                ae=Sum('Adminexpenses'),
                                                                                ms=Sum('Micellaneous'))
    income_total = total_amt['interest'] + total['fines'] + total['mf'] + total['ms']
    exp_total = pay_total['ae'] + pay_total['sal'] + pay_total['fac'] + pay_total['ms']
    if income_total > exp_total:
        ex = income_total - exp_total
        return render(request, "IEdisp.html",
                      {"RP": total, "RPAmt": total_amt, "PT": pay_total, "excess1": ex, "bal": income_total})
    else:
        ex = exp_total - income_total
        return render(request, "IEdisp.html",
                      {"RP": total, "RPAmt": total_amt, "PT": pay_total, "excess2": ex, "bal": exp_total})


def BalanceSheet(request):
    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    if request.method=="POST":
        From=request.POST["From"]
        From=datetime.strptime(From, "%Y-%m-%d").date()
        To=request.POST["To"]
        To=datetime.strptime(To, "%Y-%m-%d").date()
        shg_date=[]
        sh=shg.objects.values("Date").filter(Registration_id_imo=request.user.username)
        for i in sh:
            if i['Date']>From and i['Date']<=To and i['Date'] not in shg_date:
                shg_date.append(i['Date'])
        shgl=0
        print(shg_date)
        for i in range(len(shg_date)):
            sl=shg.objects.filter(Registration_id_imo=request.user.username,Date=shg_date[i]).aggregate(shgl=Sum('Amount'))
            shgl=shgl+sl['shgl']
        int_dates=[]
        il=Loan.objects.values("Date").filter(RegIMO=request.user.username)
        for i in il:
            if i['Date'].date()>From and i['Date'].date()<=To and i['Date'] not in int_dates:
                int_dates.append(i['Date'])
        interest=0
        principal=0
        for i in range(len(int_dates)):
            inr=Loan.objects.filter(RegIMO=request.user.username,Date=int_dates[i]).aggregate(intr=Sum('Interest'))
            interest=inr['intr']+interest
            pri=Loan.objects.filter(RegIMO=request.user.username,Date=int_dates[i]).aggregate(intr=Sum('LoanRepayment'))
            principal=principal+pri['intr']
        l=Receipts.objects.values("Date").filter(RegIMO=request.user.username)
        dates=[]
        mf=0
        fines=0
        ms=0
        openBal=0
        funds=0
        for i in l:
            if i["Date"] > From and i["Date"]<=To and i["Date"] not in dates:
                dates.append(i["Date"])
        for i in range(len(dates)):
            o=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(ob=Max('Openingbal'))
            if openBal<o['ob']:
                openBal=o['ob']
            m=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Memfees'))
            mf=mf+m['mf']
            f=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Fines'))
            fines=fines+f['mf']
            rmkf=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Rmkfunds'))
            funds=funds+rmkf['mf']
            m=Receipts.objects.filter(RegIMO=request.user.username,Date=dates[i]).aggregate(mf=Sum('Micellaneous'))
            ms=ms+m['mf']
        receipts_total=openBal+int(mf)+int(fines)+int(funds)+int(ms)+principal+int(interest)
        p=Payments.objects.values("Date").filter(RegIMO=request.user.username)
        datesp=[]
        fac=0
        sal=0
        ae=0
        ms1=0
        sta=0
        cb=0
        for i in p:
            if i['Date'] > From and i["Date"]<=To and i["Date"] not in datesp:
                datesp.append(i['Date'])
        for i in range(len(datesp)):
            c = Payments.objects.filter(RegIMO=request.user.username, Date=datesp[i]).aggregate(
                cb=Min('Closingbal'))
            if cb==0:
                cb=c['cb']
            elif cb>c['cb']:
                cb=c['cb']
            f=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Feesandcharges'))
            fac=fac+f["fac"]
            s=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Salaries'))
            sal=sal+s['fac']
            a=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Adminexpenses'))
            ae=ae+a['fac']
            m=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Micellaneous'))
            ms1=ms1+m['fac']
            st=Payments.objects.filter(RegIMO=request.user.username,Date=datesp[i]).aggregate(fac=Sum('Stationery'))
            sta=sta+st['fac']
        payments_total=int(cb+fac+sal+ae+ms1+sta+shgl)
        income=int(interest+fines+mf+ms)
        exp=int(fac+sal+ae+ms1)
        total={}
        total['mf']=int(mf)
        total['fines']=int(fines)
        total['ms']=int(ms)
        total['ob']=int(openBal)
        total['rf']=int(funds)
        total_amt={}
        total_amt["interest"]=int(interest)
        total_amt["princ"]=principal
        pay_total={}
        pay_total['fac']=int(fac)
        pay_total['sal']=int(sal)
        pay_total['ae']=int(ae)
        pay_total['ms']=int(ms1)
        pay_total['cb']=int(cb)
        pay_total['sta']=int(sta)
        total_loan={}
        total_loan['shgl']=shgl
        ex1 = 0
        ex2 = 0
        c = 0
        if receipts_total > payments_total:
            ex1 = receipts_total - payments_total
        else:
            ex2 = payments_total - receipts_total
        ex3 = 0
        ex4 = 0
        d = 0
        if income > exp:
            ex3 = income - exp
        else:
            ex4 = exp - income
        cap = shgl+sta+cb
        assests = principal+openBal+funds
        if ex1 > ex2:
            cap = cap + ex1
            c = 1
        else:
            assests = assests + ex2
        if ex4 > ex3:
            d = 1
            cap = cap + ex4
        else:
            assests = assests + ex3
        return render(request, "balsheet.html",
                      {"loan": total_loan, "RP": total, "RPAmt": total_amt, "PT": pay_total, "cap_amt": cap,
                       "assests_total": assests, "ex1": ex1, "ex2": ex2, "ex3": ex3, "ex4": ex4, "c": c, "d": d,"From":From,"To":To})
    total = Receipts.objects.filter(RegIMO=request.user.username).aggregate(ob=Max('Openingbal'), mf=Sum('Memfees'),
                                                                            fines=Sum('Fines'), rf=Sum('Rmkfunds'),
                                                                            ms=Sum('Micellaneous'))
    total_amt = Loan.objects.filter(RegIMO=request.user.username).aggregate(princ=Sum('LoanRepayment'),
                                                                            interest=Sum('Interest'))
    pay_total = Payments.objects.filter(RegIMO=request.user.username).aggregate(cb=Min('Closingbal'),
                                                                                shgl=Sum('Shgloans'),
                                                                                fac=Sum('Feesandcharges'),
                                                                                sal=Sum('Salaries'),
                                                                                ae=Sum('Adminexpenses'),
                                                                                sta=Sum('Stationery'),
                                                                                ms=Sum('Micellaneous'))
    total_loan = shg.objects.filter(Registration_id_imo=request.user.username).aggregate(shgl=Sum('Amount'))
    receipts_total = total['ob'] + total['mf'] + total['fines'] + total['rf'] + total['ms'] + total_amt['princ'] + \
                     total_amt['interest']
    payments_total = pay_total['cb'] + pay_total['fac'] + pay_total['sal'] + pay_total['ae'] + pay_total['sta'] + \
                     pay_total['ms'] + total_loan['shgl']
    income_total = total_amt['interest'] + total['fines'] + total['mf'] + total['ms']
    exp_total = pay_total['ae'] + pay_total['sal'] + pay_total['fac'] + pay_total['ms']
    ex1 = 0
    ex2 = 0
    c = 0
    if receipts_total > payments_total:
        ex1 = receipts_total - payments_total
    else:
        ex2 = payments_total - receipts_total
    ex3 = 0
    ex4 = 0
    d = 0
    if income_total > exp_total:
        ex3 = income_total - exp_total
    else:
        ex4 = exp_total - income_total
    cap = total_loan['shgl'] + pay_total['sta'] + pay_total['cb']
    assests = total_amt['princ'] + total['ob'] + total['rf']
    if ex1 > ex2:
        cap = cap + ex1
        c = 1
    else:
        assests = assests + ex2
    if ex4 > ex3:
        d = 1
        cap = cap + ex4
    else:
        assests = assests + ex3
    return render(request, "balsheet.html",
                  {"loan": total_loan, "RP": total, "RPAmt": total_amt, "PT": pay_total, "cap_amt": cap,
                   "assests_total": assests, "ex1": ex1, "ex2": ex2, "ex3": ex3, "ex4": ex4, "c": c, "d": d})


def FinRecords(request):
    return render(request, "financial_index.html")


def CashAccountDisp(request):
    AccountName = "Cash"
    Account = ledger.objects.all().filter(AccountName=AccountName, RegIMO=request.user.username)
    bal_debit = ledger.objects.filter(AccountName=AccountName, TransctionType="Debit",
                                      RegIMO=request.user.username).aggregate(debit=Sum('Amount'))
    bal_credit = ledger.objects.filter(AccountName=AccountName, TransctionType="Credit",
                                       RegIMO=request.user.username).aggregate(credit=Sum('Amount'))
    d = 0
    c = 0
    print(bal_debit)
    debit = bal_debit['debit']
    credit = bal_credit['credit']
    if credit == None:
        credit = 0
    if debit == None:
        debit = 0
    total = max(debit, credit)
    if debit > credit:
        d = debit - credit
        return render(request, 'cashAcc.html',
                      {'account': Account, 'debit': d, 'total': total})
    else:
        c = credit - debit
        return render(request, 'cashAcc.html', {'account': Account, 'credit': c, 'total': total})


def generatepdf(request):

    if not request.user.is_authenticated:
        return redirect('http://127.0.0.1:8000/login')
    total=Receipts.objects.filter(RegIMO=request.user.username).aggregate(ob=Max('Openingbal'),mf=Sum('Memfees'),fines=Sum('Fines'),rf=Sum('Rmkfunds'),ms=Sum('Micellaneous'))
    total_amt=Loan.objects.filter(RegIMO=request.user.username).aggregate(princ=Sum('LoanRepayment'),interest=Sum('Interest'))
    pay_total=Payments.objects.filter(RegIMO=request.user.username).aggregate(cb=Min('Closingbal'),shgl=Sum('Shgloans'),fac=Sum('Feesandcharges'),sal=Sum('Salaries'),ae=Sum('Adminexpenses'),sta=Sum('Stationery'),ms=Sum('Micellaneous'))
    total_loan=shg.objects.filter(Registration_id_imo=request.user.username).aggregate(shgl=Sum('Amount'))
    receipts_total=total['ob']+total['mf']+total['fines']+total['rf']+total['ms']+total_amt['princ']+total_amt['interest']
    payments_total=pay_total['cb']+pay_total['fac']+pay_total['sal']+pay_total['ae']+pay_total['sta']+pay_total['ms']+total_loan['shgl']

    itotal_amt = Loan.objects.filter(RegIMO=request.user.username).aggregate(interest=Sum('Interest'))
    itotal = Receipts.objects.filter(RegIMO=request.user.username).aggregate(mf=Sum('Memfees'),fines=Sum('Fines'),ms=Sum('Micellaneous'))
    ipay_total = Payments.objects.filter(RegIMO=request.user.username).aggregate(fac=Sum('Feesandcharges'),sal=Sum('Salaries'),ae=Sum('Adminexpenses'),ms=Sum('Micellaneous'))
    income_total=total_amt['interest']+total['fines']+total['mf']+total['ms']
    exp_total=pay_total['ae']+pay_total['sal']+pay_total['fac']+pay_total['ms']

    cap=total_loan['shgl']+pay_total['sta']+pay_total['cb']
    assests=total_amt['princ']+total['ob']+total['rf']



    if ((receipts_total>payments_total) and (income_total<exp_total)):
        print('hi')
        ex=receipts_total-payments_total
        iex=exp_total-income_total
        pdf=render_to_pdf("rppdf.html",{"RP":total,"RPAmt":total_amt,"PT":pay_total,"loan":total_loan,"excess1":ex,"bal":receipts_total,"iRP":itotal,"iRPAmt":itotal_amt,"iPT":ipay_total,"iexcess2":iex,"ibal":exp_total,"cap_amt":cap+ex+iex,"assests_total":assests,"c":1,"d":1})
    elif ((receipts_total>payments_total) and (income_total>exp_total)):
        ex=receipts_total-payments_total
        iex=income_total-exp_total
        pdf=render_to_pdf("rppdf.html",{"RP":total,"RPAmt":total_amt,"PT":pay_total,"loan":total_loan,"excess1":ex,"bal":receipts_total,"iRP": itotal, "iRPAmt":itotal_amt, "iPT": ipay_total, "iexcess1": iex,"ibal":income_total,"cap_amt":cap+ex,"assests_total":assests+iex,"c":1,"d":0})

    elif(receipts_total<payments_total and income_total>exp_total):
        ex=payments_total-receipts_total
        iex=income_total-exp_total
        pdf=render_to_pdf("rppdf.html",{"RP":total,"RPAmt":total_amt,"PT":pay_total,"loan":total_loan,"excess1":ex,"bal":receipts_total,"iRP": itotal, "iRPAmt":itotal_amt, "iPT": ipay_total, "iexcess1": iex,"ibal":income_total,"cap_amt":cap,"assests_total":assests+iex,"c":0,"d":0})

    elif(receipts_total<payments_total and income_total<exp_total):
        ex=payments_total-receipts_total
        iex=exp_total-income_total
        pdf=render_to_pdf("rppdf.html",{"RP":total,"RPAmt":total_amt,"PT":pay_total,"loan":total_loan,"excess2":ex,"bal":payments_total,"iRP": itotal, "iRPAmt":itotal_amt, "iPT": ipay_total, "iexcess2": iex,"ibal":exp_total,"cap_amt":cap,"assests_total":assests+ex+iex,"c":0,"d":1})

    #if(pdf==None):
    #    print("hi")
    if pdf:
        response=HttpResponse(pdf,content_type='application/pdf')
        filename="Accounts.pdf"
        content="inline; filename='%s'" %(filename)
        download=request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
        return HttpResponse("Not Found")
