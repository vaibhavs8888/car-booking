from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from register.models import registermodel,Booking
from register.serializers import registrationserializer,loginserializer,userprofileserializer,BookingSerializer,ChangePasswordSerializer
from rest_framework.response import Response
from rest_framework import status,authentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from register.renderes import registrationrenderes
from rest_framework_simplejwt.tokens import RefreshToken
from register.models import Car
from register.serializers import CarSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import make_aware

# Create your views here.

def get_token_for_user(user):
    refresh=RefreshToken.for_user(user)
    return{
        'Refresh':str(refresh),
        'access':str(refresh.access_token),
    }

class registrationview(APIView):
    renderer_classes=[registrationrenderes]
    def get(self, request):
        kk = registermodel.objects.all()
        serializer = registrationserializer(kk, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = registrationserializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            registerkr=serializer.save()
            token=get_token_for_user(registerkr)
            return Response({'Token':token,'msg':'You Are SuccessFully Registered'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class userloginview(APIView):
    renderer_classes=[registrationrenderes]
    def post(self,request):
        datalist=loginserializer(data=request.data)
        if datalist.is_valid(raise_exception=True):
           Email = datalist.validated_data.get('Email')
           password = datalist.validated_data.get('password')
           listdata = authenticate(username=Email, password=password)
           if listdata is not None:
               token=get_token_for_user(listdata)
               return Response({'Token':token,'MSG':'You Are SuccessFully LoggedIn!'},status=status.HTTP_200_OK)
           else:
               return Response({'errors':{'non_field_errors':['email and password is not matched']}},status=status.HTTP_404_NOT_FOUND)
        return Response(datalist.errors,status=status.HTTP_400_BAD_REQUEST)


           # may be error          
class userprofileview(APIView):
      renderer_classes=[registrationrenderes]
      permission_classes= [IsAuthenticated]
      authentication_classes = [JWTAuthentication]
      def get(self,request):
          serializer=userprofileserializer(instance=request.user)
          token=get_token_for_user(request.user)
          return Response({'token':token,"User_Profile":serializer.data},status=status.HTTP_200_OK)
           


class CarListView(APIView):
    renderer_classes=[registrationrenderes]
    def get(self, request):
        now = timezone.localtime()
        expired_cars = Car.objects.filter(is_booked=True, available_from__lte=now)
        for car in expired_cars:
            car.is_booked = False
            car.available_from = None
            car.save()
        
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)
    


class FindCarView(APIView):
    renderer_classes = [registrationrenderes]
    def post(self, request):
        pick_up_date = request.data.get("pick_up_date")
        pick_time = request.data.get("pick_time")
        drop_off_date = request.data.get("drop_off_date")
        drop_time = request.data.get("drop_time")

        # Combine date and time into datetime strings
        pick_datetime_str = f"{pick_up_date} {pick_time}"
        drop_datetime_str = f"{drop_off_date} {drop_time}"

        try:
            pick_datetime = datetime.strptime(pick_datetime_str, "%d-%m-%Y %H:%M")
            drop_datetime = datetime.strptime(drop_datetime_str, "%d-%m-%Y %H:%M")
        except ValueError:
            return Response({"error": "Invalid date or time format"}, status=400)

        # Convert to timezone aware (IST)
        pick_datetime = timezone.make_aware(
            pick_datetime, timezone.get_current_timezone()
        )
        drop_datetime = timezone.make_aware(
            drop_datetime, timezone.get_current_timezone()
        )

        # Validate: pickup time must be in the future
        current_time = timezone.localtime()
        if pick_datetime < current_time:
            return Response(
                {"error": "Pick-up time cannot be in the past."}, status=400
            )

        # Auto-unblock expired cars
        now = timezone.localtime()
        expired_cars = Car.objects.filter(is_booked=True, available_from__lte=now)
        for car in expired_cars:
            car.is_booked = False
            car.available_from = None
            car.save()

        # Filter cars in Pune
        cars = Car.objects.filter(city="Pune")

        # Collect available cars for requested time
        available_cars = []
        for car in cars:
    # Include all cars, but frontend can decide based on is_booked
    # Add cars that are free OR will be free before requested pickup
           if not car.is_booked or (
                car.available_from and car.available_from <= pick_datetime
                ):
                available_cars.append(car)
           else:
        # Include booked cars so frontend can show "booked until"
                available_cars.append(car)

        serializer = CarSerializer(available_cars, many=True)
        return Response(serializer.data)


class BookCarView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [registrationrenderes]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        data = request.data.copy()

        car_id = data.get("car_id")
        pickup_date = data.get("pick_up_date")
        pick_time = data.get("pick_time")
        dropoff_date = data.get("drop_off_date")
        drop_time = data.get("drop_time")

        
        try:
            pickup_datetime = datetime.strptime(f"{pickup_date} {pick_time}", "%d-%m-%Y %H:%M")
            dropoff_datetime = datetime.strptime(f"{dropoff_date} {drop_time}", "%d-%m-%Y %H:%M")
        except ValueError:
            return Response({"error": "Invalid date or time format"}, status=400)

        pickup_datetime = make_aware(pickup_datetime, timezone.get_current_timezone())
        dropoff_datetime = make_aware(dropoff_datetime, timezone.get_current_timezone())
        now = timezone.localtime()

        if pickup_datetime < now:
            return Response({"error": "Pick-up must be today or in the future"}, status=400)
        if pickup_datetime >= dropoff_datetime:
            return Response({"error": "Drop-off must be after pickup time"}, status=400)

        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response({"error": "Car does not exist"}, status=404)

        overlapping = Booking.objects.filter(
            car=car,
            pickup_date__lt=dropoff_datetime.date(),
            dropoff_date__gt=pickup_datetime.date()
        ).exclude(
            dropoff_date=pickup_datetime.date(),
            dropoff_time__lte=pickup_datetime.time()
        ).exists()

        if overlapping:
            return Response({"error": "Car already booked for the selected time"}, status=400)

        booking = Booking.objects.create(
            user=user,
            car=car,
            pickup_date=pickup_datetime.date(),
            pickup_time=pickup_datetime.time(),
            dropoff_date=dropoff_datetime.date(),
            dropoff_time=dropoff_datetime.time(),
            driving_licence=request.FILES.get('driving_licence'),
            residence_proof=request.FILES.get('residence_proof'),
            pan_card=request.FILES.get('pan_card'),
            aadhaar_card=request.FILES.get('aadhaar_card'),
            payment_screenshot=request.FILES.get('payment_screenshot')
        )
        required_docs = ['driving_licence', 'residence_proof', 'pan_card', 'aadhaar_card', 'payment_screenshot']
        for doc in required_docs:
            if not request.FILES.get(doc):
                return Response({"error": f"{doc.replace('_', ' ').title()} is required"}, status=400)

        car.is_booked = True
        car.available_from = dropoff_datetime
        car.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [registrationrenderes]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            # Logout from all devices after password change
            try:
                refresh_token = request.data.get("refresh")
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
            except:
                pass

            return Response({"detail": "Password changed successfully. Please log in again."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





