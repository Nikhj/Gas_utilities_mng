from django.shortcuts import render, redirect,HttpResponse
from django.http import JsonResponse

from django.contrib import messages
from django.db import connection as conn
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import base64
import datetime


def add_role_id_to_context(request):
    try:
        if 'customer_id' in request.session:
            role_id = 100
        elif 'admin_id' in request.session:
            role_id = 101
        return {"role_id":role_id}
    except:
        return {"role_id":100}

def check_connection_no(customer_id):
    

  
    
    fetch_query = ''' select connection_no,status from connection_details where customer_id = %s'''
    values = (customer_id,)

    cursor = conn.cursor()
    cursor.execute(fetch_query,values)
    results = cursor.fetchone()

    if results == None:
        return "NOT_EXIST"
    elif results[1] == 'pending':
        return "Pending"
    else:
        return "Exist"


    
    


def fetch_dashboard_data(request):
    if request.method == "GET":
        customer_id = request.session['customer_id']

        conn_status = check_connection_no(customer_id)


        if conn_status=='Exist':

            fetch_query ='''select cd.connection_no, cd.distributor_name,up.first_name,up.last_name,cd.dob,cd.house_no,cd.area,cd.city,cd.state,cd.pincode,cd.phone_no,up.mobile_no,up.email,cd.total_refill,cd.used_refill,cd.status from userprofile as up \
            inner join connection_details as cd on up.customer_id = cd.customer_id where up.customer_id =%s;'''
            values = (customer_id,)
            

            cursor = conn.cursor()
            cursor.execute(fetch_query,values)
            result = cursor.fetchone()
            label_value = ("connection_no","distributor_name","first_name","last_name","dob","house_no","area","city","state","pincode","phone_no","mobile_no","email","total_refill","used_refill","status")

            customer_data = dict(zip(label_value,result))

        else:
            customer_data = {"status":conn_status}

        return JsonResponse(customer_data)




def home(request):
    if request.method == "GET":
        if 'customer_id' in request.session:
            
            return render(request,"dashboard.html",{"role_id":100})
        
        else:
            return redirect(user_login)

        # return render(request,"home.html")
    

def admin_home(request):
    if request.method == "GET":
        if 'admin_id' in request.session:

            fetch_con_query = '''select count(*) from connection_details where status = "pending" \
                            union all\
                            select count(*) from connection_details where status = "approved"
                            union all
                            select count(*) from connection_details 
                            union all
                            select count(*) from booking_tb where status = "pending" \
                            union all\
                            select count(*) from booking_tb where status = "approved"
                            union all
                            select count(*) from booking_tb  '''
            
            cursor = conn.cursor()
            cursor.execute(fetch_con_query)   
            result = cursor.fetchall()
            cursor.close()
            print(result)

            data = {}
            data['role_id'] = 101
            data['con_pending'] = result[0][0]
            data['con_approved'] = result[1][0]
            data['con_total'] = result[2][0]
            data['booking_pending'] = result[3][0]
            data['booking_approved'] = result[4][0]
            data['booking_total'] = result[5][0]


            return render(request,"admin_dashboard.html",data)
        else:
            return redirect(user_login)

def user_login(request):
    if request.method == 'POST':
        email_id = request.POST['email']
        password = request.POST['password']

        get_query = "select * from UserProfile where email = %s and cust_password = %s" 
        values = (email_id,password)

        cursor = conn.cursor()
        cursor.execute(get_query,values)   
        result = cursor.fetchone()

        cursor.close()

        if result:   
            if result[6]==100:
                request.session['customer_id'] = result[0]
                
                return redirect(home)
            
            if result[6] == 101:
                request.session['admin_id'] = result[0]
                
                return redirect(admin_home)
                
    
    if 'customer_id' in request.session:
        del request.session['customer_id']
    if  'admin_id' in request.session:
        del request.session['admin_id']
        
            
    return render(request, 'login.html')



def user_registration(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        mobile_no = request.POST['phone_no']
        password = request.POST['password']
                
        query = '''INSERT INTO gas_utilities_db.UserProfile (first_name, last_name, email, mobile_no, cust_password ) \
        VALUES (%s, %s, %s, %s, %s);'''

        values = (first_name,last_name,email,mobile_no,password)
  
        cursor = conn.cursor()
        cursor.execute(query,values)
        conn.commit()
        cursor.close()

        return redirect('user_login')  # Redirect to the login page
    
    if 'customer_id' in request.session:
        del request.session['customer_id']
    if  'admin_id' in request.session:
        del request.session['admin_id']

    return render(request, 'registration.html')  

def add_connection(request):
    if request.method == "GET":
        if 'customer_id' in request.session:
            customer_id = request.session['customer_id']

            fetch_query = ''' select first_name,last_name,email,mobile_no from gas_utilities_db.UserProfile where customer_id = %s'''
            values = (customer_id,)

            cursor = conn.cursor()
            cursor.execute(fetch_query,values)
            results = cursor.fetchone()
            cursor.close()

            connection_data = {"first_name":results[0],"last_name":results[1],"email":results[2],"mobile_number":results[3]}         
            return render(request,"connection.html",connection_data)
        else:
            return redirect(user_login)
    elif request.method == "POST":
        distributor_name = request.POST['distributor_name']
        dob = request.POST['dob']
        house_no = request.POST['house_no']
        area = request.POST['area']
        city = request.POST['city']
        state = request.POST['state']
        pin_code = request.POST['pinCode']
        phone_no = request.POST['phone']
        adhar_no = request.POST['adhar']
        adhar_img = request.FILES['document_image']

        image_content = adhar_img.read()
        base64_image = base64.b64encode(image_content).decode('utf-8')
       

        prefix = "data:image/png;base64,"
        new_byteimage = prefix+base64_image




        
        insert_query = '''insert into gas_utilities_db.connection_details(customer_id,distributor_name,dob,house_no,area,city,state,pincode,phone_no,aadhar_no,aadhar_no_img) \
                          values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
        
        values=(request.session['customer_id'],distributor_name,dob,house_no,area,city,state,pin_code,phone_no,adhar_no,new_byteimage)
        try:
            cursor = conn.cursor()
            cursor.execute(insert_query,values)
            conn.commit()
            cursor.close()
        except IntegrityError:
            messages.error(request, 'connection already exists!!!')

        return redirect(home)
    
def get_connection_no(customer_id):
    

    fetch_query = ''' select connection_no from connection_details where customer_id = %s '''
    values = (customer_id,)

    cursor = conn.cursor()
    cursor.execute(fetch_query,values)
    results = cursor.fetchone()
    
    if results:
        return customer_id
    else:
        return False  
    

def booking_page(request):
    if request.method == "GET":
        if 'customer_id' in request.session:
            customer_id = request.session['customer_id']

            conn_status = check_connection_no(customer_id)

            if conn_status == 'Exist':
            
                connection_no = get_connection_no(customer_id)
                if connection_no:
                    fetch_query = '''select cd.distributor_name,up.first_name,up.last_name,cd.connection_no from userprofile as up \
                    inner join connection_details as cd on cd.customer_id = up.customer_id where up.customer_id = %s;'''
                    values = (customer_id,)

                    cursor = conn.cursor()
                    cursor.execute(fetch_query,values)
                    results = cursor.fetchone()

                    booking_details = {}
                    booking_details['distributor_name'] = results[0]
                    booking_details['customer_name'] = results[1]+ ' '+results[2]
                    booking_details['connection_no'] = results[3]

                    return render(request,"booking.html",booking_details)
                else:
                    messages.error(request, 'connection does not exists!!!')
                    return redirect(home)
            else:
                return redirect(home)
        else:
            return redirect(user_login)
        

def get_refill_count(connection_no):
    select_query = ''' select total_refill,used_refill from connection_details where connection_no = %s;'''
    values = (connection_no,)

    cursor = conn.cursor()
    cursor.execute(select_query,values)
    results = cursor.fetchone()
    cursor.close()

    return results


@csrf_exempt
def booking_data(request):
    if request.method == "GET":
        
        connection_no = request.GET['connection_no']
       
        fetch_data = ''' select booking_no , booking_date , total_amount, subsidy_amount,delivered_date,status from booking_tb where connection_no = %s; '''
        values = (connection_no,)

        cursor = conn.cursor()
        cursor.execute(fetch_data,values)
        results = cursor.fetchall()
        
        cursor.close()
        index = [i for i in range(len(results))]
        results = dict(zip(index,results))
        print("results:",results)
        response_data = JsonResponse(results)
        return response_data

        # return JsonResponse(request,results,safe=False)
    elif request.method == "POST":
        connection_no = request.POST['connection_no']
        total_amount = request.POST['total_amount']
        subsidy_amount = request.POST['subsidy_amount']
        booking_date = request.POST['booking_date']


        
        total_refill,used_refill = get_refill_count(connection_no)
        used_refill +=1

        if used_refill <= total_refill:
            insert_query = ''' insert into gas_utilities_db.booking_tb(connection_no,booking_date,total_amount,subsidy_amount) \
                            values(%s,%s,%s,%s); '''
            values = (connection_no,booking_date,total_amount,subsidy_amount)

            update_query = '''update connection_details set used_refill = %s where connection_no = %s;'''
            up_values = (used_refill,connection_no)

            cursor = conn.cursor()
            cursor.execute(insert_query,values)
            cursor.execute(update_query,up_values)
            conn.commit()
            cursor.close()

                        
            return JsonResponse({"status":"passed","message":"Booked Successfully"})
        else:
            return JsonResponse({"status":"Failed","message":"Refill count exceeds"})




    
def admin_view_connection(request):
    if request.method =="GET":
        if 'admin_id' in request.session:
            fetch_query = '''select cd.connection_no, cd.distributor_name,up.first_name,up.last_name,cd.house_no,cd.city,cd.state,cd.pincode,cd.registration_date,approved_date,cd.status from userprofile as up \
                inner join connection_details as cd on up.customer_id = cd.customer_id;'''
            
            cursor = conn.cursor()
            cursor.execute(fetch_query)
            results = cursor.fetchall()
            cursor.close()

        
            return render(request,"admin_connections.html",{"results":results})
        else:
            return redirect(user_login)
    

def admin_connection_details(request,connection_id):
    if request.method =="GET":
        if 'admin_id' in request.session:
            fetch_query = '''select cd.connection_no,cd.distributor_name,up.first_name,up.last_name,cd.dob,up.email,cd.phone_no,
                        up.mobile_no,cd.house_no,cd.area, cd.city,cd.state,cd.pincode,cd.aadhar_no,cd.aadhar_no_img,cd.registration_date,
                        cd.status from connection_details as cd inner join userprofile as up on up.customer_id=cd.customer_id
                        where connection_no=%s '''
            
            Values = (connection_id,)
            cursor = conn.cursor()
            cursor.execute(fetch_query,Values)
            results = cursor.fetchone()
            label_tup=("connection_no","distributor_name","first_name","last_name","dob","email","phone_no","mobile_no","house_no","area","city","state","pincode","aadhar_no","aadhar_no_img","registration_date","status")
            data = dict(zip(label_tup,results))
            cursor.close()

        
            return render(request,'view_connection.html',data)
        else:
            return redirect(user_login)
    
    elif request.method =="POST":
        connection_no = request.POST['connection_no']
        status = request.POST['status']

        if status == "approved" or status=="rejected":
            today_date = datetime.datetime.now()
            
            insert_query = '''update  connection_details set approved_date = %s , status = %s where connection_no = %s'''
            values = (today_date,status,connection_no)
            cursor = conn.cursor()
            cursor.execute(insert_query,values)
            conn.commit()
            cursor.close()    

        return redirect(admin_view_connection)
    


def admin_view_booking(request):
    if request.method =="GET":
        if 'admin_id' in request.session:
            fetch_query = '''SELECT bd.booking_no,bd.connection_no, up.first_name, up.last_name, bd.booking_date,bd.delivered_date,bd.status
                    FROM userprofile AS up
                    INNER JOIN (
                        SELECT bt.booking_no, bt.connection_no, bt.booking_date, bt.delivered_date, bt.status, cd.customer_id
                        FROM booking_tb AS bt
                        INNER JOIN connection_details AS cd ON bt.connection_no = cd.connection_no
                    ) AS bd ON up.customer_id = bd.customer_id;'''
            
            cursor = conn.cursor()
            cursor.execute(fetch_query)
            results = cursor.fetchall()
            cursor.close()

            
            return render(request,"admin_booking.html",{"results":results})    
        else:
            return redirect(user_login)  
        

        
def admin_confirm_booking(request,booking_no):
    if request.method =="GET":
        if 'admin_id' in request.session:
            fetch_query = '''select data.distributor_name, data.booking_no,data.connection_no,up.first_name,up.last_name, 
                            data.total_amount,data.subsidy_amount,data.total_refill,data.used_refill,data.booking_date,data.status from userprofile as up 
                            inner join (
                            select cd.distributor_name,cd.customer_id, bt.booking_no,bt.connection_no,bt.total_amount,bt.subsidy_amount,cd.total_refill,
                            cd.used_refill,bt.booking_date,bt.status from booking_tb as bt inner join connection_details as cd on bt.connection_no = cd.connection_no
                            ) as data on data.customer_id = up.customer_id where data.booking_no = %s;'''
            
            Values = (booking_no,)
            cursor = conn.cursor()
            cursor.execute(fetch_query,Values)
            results = cursor.fetchone()
            label_tup=("distributor_name","booking_no","connection_no","first_name","last_name","total_amount","subsidy_amount","total_refill","used_refill","booking_date","status")
            data = dict(zip(label_tup,results))
            cursor.close()

        
            return render(request,'view_booking.html',data)
        else:
            return redirect(user_login)
    
    elif request.method =="POST":
        booking_no = request.POST['bookingNo']
        status = request.POST['status']

        if status == "approved" or status=="rejected":
            today_date = datetime.datetime.now()
            
            insert_query = '''update  booking_tb set delivered_date = %s , status = %s where booking_no = %s'''
            values = (today_date,status,booking_no)
            cursor = conn.cursor()
            cursor.execute(insert_query,values)
            conn.commit()
            cursor.close()    

        return redirect(admin_view_booking)


def start_fun(request):
    return redirect(user_login)

def logout(request):
    try:
        if 'customer_id' in request.session:
            del request.session['customer_id']
        elif 'admin_id' in request.session:
            del request.session['admin_id']
        return redirect(user_login)
    except:
        return redirect(user_login)


        
       









