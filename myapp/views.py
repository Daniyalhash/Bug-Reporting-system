from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import sqlite3
from django.http import JsonResponse
from pathlib import Path
from django.core.mail import send_mail


BASE_DIR = Path(__file__).resolve().parent.parent

def home(request):
    return render(request,'index.html')


# Create your views here.
@csrf_exempt

def addBug(request):
    return render(request,'addBug.html')


def email(request):
    return render(request,'email.html')

@csrf_exempt
def update_record(request,ReporterID):

    if request.method == 'POST':
        reporterName1 = request.POST.get('reporterName1')
        bugType1 = request.POST.get('bugType1')
        reason1 = request.POST.get('bugReason1')
        siteName1 = request.POST.get('siteName1')
        siteLink1 = request.POST.get('siteLink1')
        ownerEmail1 = request.POST.get('ownerEmail1')
        
        with sqlite3.connect(BASE_DIR/'data.db') as db:
            cursor=db.cursor()
            query = """
                UPDATE Form
                SET ReporterName = ?,
                    BugType = ?,
                    Reason = ?,
                    SiteName = ?,
                    SiteLink = ?,
                    OwnerEmail = ?
                WHERE ReporterID = ? 
            """
            values = (reporterName1, bugType1, reason1, siteName1, siteLink1, ownerEmail1, ReporterID )
            cursor.execute(query, values)
        
    return redirect('/record')
    
    
def delete_record(request,ReporterID):

    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        query = "DELETE FROM Form WHERE ReporterID = ?"
        cursor.execute(query, (ReporterID,))
             
    return redirect('/record')


def get_counts(request):
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(DISTINCT ReporterName) FROM Form")
        reporter_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Form")
        bugs_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Form WHERE status = 'Reported'")
        reported_count = cursor.fetchone()[0]

    counts = {
        'reporter_count': reporter_count,
        'bugs_count': bugs_count,
        'reported_count': reported_count,
    }

    return JsonResponse(counts)


def record(request):
    # context = get_counts(request)
    # print("here",context)
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        cursor1=db.cursor()
        cursor2=db.cursor()
        cursor3=db.cursor()

        query = "SELECT ReporterID, ReporterName, BugType, Reason, SiteName, SiteLink, OwnerEmail,status FROM Form"
        cursor.execute(query)
        row = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

            # Prepare the data as a list of dictionaries
        record = []
        for row in row:
            r = dict(zip(column_names, row))
            record.append(r)
            
            
        query1 = "SELECT DISTINCT ReporterName FROM Form"
        cursor1.execute(query1)
        row1 = cursor1.fetchall()
        column_names1 = [description[0] for description in cursor.description]

            # Prepare the data as a list of dictionaries
        record1 = []
        for row in row1:
            r = dict(zip(column_names1, row))
            record1.append(r)
            
            
        query2 = "SELECT ReporterName, COUNT(*) AS Records FROM Form GROUP BY ReporterName"
        cursor2.execute(query2)
        
        row2 = cursor2.fetchall()
        # print(row2)
        column_names2 = [description[0] for description in cursor2.description]

        record2 = []
        for row in row2:
            r = dict(zip(column_names2, row))
            record2.append(r)

        cursor3.execute("SELECT DISTINCT bugType FROM Form;")
        record3 = [row[0] for row in cursor3.fetchall()]
    # print(context[0])
    return render(request,'record.html',{'record':record,'record1':record1,'record2':record2, 'record3':record3 })


def bug_types_view(request):
    print("*"*10)
    # Connect to the SQLite database
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        
        # Fetch all unique bug types from the 'Form' table
        cursor.execute("SELECT DISTINCT bugType FROM Form;")
        bug_types = [row[0] for row in cursor.fetchall()]

    return render(request, 'record.html', {'bugTypes': bug_types})

@csrf_exempt
def saveform(request):
    print("*"*20)
    if request.method == 'POST':
        reporterName = request.POST.get('reporterName')
        bugType = request.POST.get('bugType')
        reason = request.POST.get('bugReason')
        siteName = request.POST.get('siteName')
        siteLink = request.POST.get('siteLink')
        ownerEmail = request.POST.get('ownerEmail')
        status = "Not reported"
        with sqlite3.connect(BASE_DIR / 'data.db') as db:
            cursor = db.cursor()

            # Get the last inserted reporter ID from the database
            query_last_id = "SELECT ReporterID FROM Form ORDER BY ReporterID DESC LIMIT 1"
            cursor.execute(query_last_id)
            result = cursor.fetchone()

            if result is not None:
                last_id = int(result[0])
                new_id = str(last_id + 1).zfill(4)  # Increment the last ID and pad with leading zeros
            else:
                new_id = "0001"  # If there are no existing records, start with 0001
           
            query = """INSERT INTO Form (ReporterID, ReporterName, BugType, Reason, SiteName, SiteLink, OwnerEmail, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            values = (new_id, reporterName, bugType, reason, siteName, siteLink, ownerEmail, status)
            cursor.execute(query, values)
            db.commit()  # Add this line to commit the changes to the database

    return render(request, 'addBug.html')

def email(request):
    
    # with connection.cursor() as cursor:
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()    
        # cursor.execute("SELECT DISTINCT ReporterID, ReporterName FROM Form")
        cursor.execute("SELECT DISTINCT ReporterName FROM Form WHERE status in ('Not reported')")

        reporters = cursor.fetchall()
        print("here",reporters)
        dict = {'reporters': reporters}
        print(dict.items())
    return render(request, 'email.html', dict)

def fetch_bug_types(request):
    reporterName = request.GET.get('reporter')
    print(reporterName)
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        # cursor.execute("SELECT DISTINCT BugType FROM Form WHERE ReporterID = %s", [reporter_id])
        cursor.execute("SELECT DISTINCT BugType FROM Form WHERE ReporterName = ?", (reporterName,))
        bug_types = cursor.fetchall()
        # print(bug_types)
    return JsonResponse({'bug_types': bug_types})

def fetch_site_names(request):
    reporterName = request.GET.get('reporterName')
    bug_type = request.GET.get('bug_type')
    # print(reporterName, bug_type)
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT SiteName FROM Form WHERE ReporterName = ? AND BugType = ?", (reporterName, bug_type))
        site_names = cursor.fetchall()
        # print(site_names)
    return JsonResponse({'site_names': site_names})

def fetch_owner_email(request):
    print("inside the owner email")
    reporterName = request.GET.get('reporter')
    bug_type = request.GET.get('bug_type')
    site_name = request.GET.get('site_name')
    print(reporterName, site_name)
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT OwnerEmail FROM Form WHERE ReporterName = ? AND BugType = ? AND SiteName = ?", (reporterName, bug_type, site_name))
        # owner_names = cursor.fetchall()
        owner_email = cursor.fetchone()
        print(owner_email)
    return JsonResponse({'owner_email': owner_email})

@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        owner_email = request.POST.get('owner_email')

        # Send the email
        send_mail(subject, message, 'streetboys9191@gmail.com', [owner_email])

        # Return a JSON response indicating success
        return JsonResponse({'message': 'Email sent successfully.'})
    else:
        # Return an error response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method.'})
    
@csrf_exempt
def update_status(request):
    reporter_name = request.POST.get('reporter_name')
    bug_type = request.POST.get('bug_type')
    site_name = request.POST.get('site_name')

    print(reporter_name,
    bug_type,
    site_name)
    with sqlite3.connect(BASE_DIR / 'data.db') as db:
        cursor = db.cursor()
        cursor.execute("UPDATE Form SET status = 'Reported' WHERE ReporterName = ? AND BugType = ? AND SiteName = ?;", (reporter_name, bug_type, site_name))
        # site_names = cursor.fetchall()
        # print(site_names)
    return JsonResponse({'message': 'Status updated successfully'})