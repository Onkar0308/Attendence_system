from django.http import StreamingHttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import cv2
from pyzbar.pyzbar import decode
import time
from django.http import StreamingHttpResponse
import geocoder
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from geopy.distance import geodesic
from .models import Scanner

def home(request):
    return render(request, "index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        Lname = request.POST['Lname']
        Email = request.POST['Email']
        password = request.POST['password']
        conform_password = request.POST['conform_password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another username.")
            return redirect('home')

        if User.objects.filter(email=Email).exists():
            messages.error(request, "Email already exists.")
            return redirect('home')

        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters.")

        if password != conform_password:
            messages.error(request, "Passwords didn't match.")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric.")
            return redirect('home')

        myuser = User.objects.create_user(username, Email, password)
        myuser.first_name = fname
        myuser.last_name = Lname
        myuser.save()

        messages.success(request, "Your account has been successfully created.")

        # Welcome Email
        subject = "Welcome to Attendance System - Django Login"
        message = f"Hello {myuser.first_name}!!\n" \
                  f"Welcome to the attendance system!!\n" \
                  f"Thank you for visiting our website.\n" \
                  f"We have also sent a confirmation email. Please confirm your email address to activate your account.\n\n" \
                  f"Thank you."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        return redirect('signin')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, "index.html", {'fname': user.first_name})
        else:
            messages.error(request, "Bad Credentials")
            return redirect('home')

    return render(request, "login.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out successfully!")
    return redirect('home')



def generate_frames_generator():
    cap = cv2.VideoCapture(1)
    scanned_qr_codes = 0

    try:
        while cap.isOpened():
            success, frame = cap.read()

            frame = cv2.flip(frame, 1)

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detected_barcodes = decode(gray_frame)

            if not detected_barcodes:
                print("No barcode detected")
            else:
                for barcode in detected_barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    print(f"Barcode Type: {barcode_type}, Barcode Data: {barcode_data}")
                    scanned_qr_codes += 1

                    if scanned_qr_codes == 1:
                        try:
                            scanner_object = Scanner.objects.get(code=barcode_data)

                            if not scanner_object.attendance_marked:
                                # Mark attendance as present
                                scanner_object.attendance_marked = True
                                scanner_object.save()
                                print("Attendance Marked: Present")
                            else:
                                # Attendance already marked
                                print("Attendance Already Marked: Absent")
                        except Scanner.DoesNotExist:
                            # Barcode data does not match any Scanner object
                            print("Barcode Data does not match any record: Absent")

                        print("Exiting after scanning one QR code.")
                        break

            _, jpeg = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

            time.sleep(0.1)

            if scanned_qr_codes == 1:
                print("Scanning complete.")
                break

    except KeyboardInterrupt:
        pass

    finally:
        cap.release()
        cv2.destroyAllWindows()


# ... (rest of the code)

# views.py
def generate_frames(request):
    try:
        return StreamingHttpResponse(generate_frames_generator(), content_type='multipart/x-mixed-replace; boundary=frame')
    except KeyboardInterrupt:
        print("Streaming stopped due to KeyboardInterrupt.")
        return HttpResponseServerError("Internal Server Error")
    except Exception as e:
        print(f"Streaming stopped due to an exception: {str(e)}")
        return HttpResponseServerError("Internal Server Error: " + str(e))


# views.py
# ... (other imports and views)

# views.py
def mark_attendance(request):
    cap = cv2.VideoCapture(1)
    scanned_qr_codes = 0

    try:
        while cap.isOpened():
            success, frame = cap.read()

            frame = cv2.flip(frame, 1)

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detected_barcodes = decode(gray_frame)

            if not detected_barcodes:
                print("No barcode detected")
            else:
                for barcode in detected_barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    print(f"Barcode Type: {barcode_type}, Barcode Data: {barcode_data}")
                    scanned_qr_codes += 1

                    if scanned_qr_codes == 1:
                        try:
                            scanner_object = Scanner.objects.get(code=barcode_data)

                            if not scanner_object.attendance_marked:
                                # Mark attendance as present
                                scanner_object.attendance_marked = True
                                scanner_object.save()
                                print("Attendance Marked: Present")
                            else:
                                # Attendance already marked
                                print("Attendance Already Marked: Absent")
                        except Scanner.DoesNotExist:
                            # Barcode data does not match any Scanner object
                            print("Barcode Data does not match any record: Absent")

                        print("Exiting after scanning one QR code.")
                        break

            _, jpeg = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

            time.sleep(0.1)

            if scanned_qr_codes == 1:
                print("Scanning complete.")
                break

    except KeyboardInterrupt:
        pass

    finally:
        cap.release()
        cv2.destroyAllWindows()


# def generate_frames(request):
#     try:
#         return StreamingHttpResponse(generate_frames_generator(), content_type='multipart/x-mixed-replace; boundary=frame')
#     except KeyboardInterrupt:
#         print("Streaming stopped due to KeyboardInterrupt.")
#         return HttpResponseServerError("Internal Server Error")
#     except Exception as e:
#         print(f"Streaming stopped due to an exception: {str(e)}")
#         return HttpResponseServerError("Internal Server Error: " + str(e))


def scanner(request):
    try:
        return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
    except KeyboardInterrupt:
        print("Streaming stopped due to KeyboardInterrupt.")
        return HttpResponseServerError("Internal Server Error")
    except Exception as e:
        print(f"Streaming stopped due to an exception: {str(e)}")
        return HttpResponseServerError("Internal Server Error")


def geofence_check_view(request):
    geofence_center = (19.0728, 72.8826)   # Example coordinates for San Francisco
    geofence_radius = 2
# Geofence radius in kilometers

    current_location = get_current_location()
    inside_geofence = is_inside_geofence(current_location, geofence_center, geofence_radius)

    return render(request, 'geofence_check.html', {'inside_geofence': inside_geofence, 'current_location': current_location})


def get_current_location():
    try:
        # Get the current location using the device's IP address (requires internet connection)
        current_location = geocoder.ip('me').latlng
        return tuple(current_location)
    except Exception as e:
        print(f"Error getting current location: {str(e)}")
        return None


def is_inside_geofence(current_location, geofence_center, radius):

    try:
        distance = geodesic(current_location, geofence_center).kilometers
        return distance <= radius
    except Exception as e:
        print(f"Error calculating geofence distance: {str(e)}")
        return False

# def mark_attendance(request, scanned_code):
#     scanner_object = get_object_or_404(Scanner, code=scanned_code)
#
#     if not scanner_object.attendance_marked:
#         # Mark attendance as present
#         scanner_object.attendance_marked = True
#         scanner_object.save()
#         return HttpResponse("Attendance Marked: Present")
#     else:
#         # Attendance already marked
#         return HttpResponse("Attendance Already Marked: Absent")
