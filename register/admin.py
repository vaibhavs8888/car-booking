from django.contrib import admin
from register.models import registermodel,Car,Booking
from django.utils.html import format_html
from datetime import datetime
from django.utils import timezone

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Email', 'Mobile_no', 'Date_Of_Birth',)
    # ... other config ...
    
    search_fields = ('Email','Name',)
    ordering = ('Email',)



class CarAdmin(admin.ModelAdmin):
    list_display = (
        'car_name', 'id', 'city', 'is_booked', 'available_from',
         'pickup_datetime', 'dropoff_datetime'
    )
    list_filter = ('is_booked', 'available_from')
    search_fields = ('car_name',)
    readonly_fields = ('city',)
    actions = ['cancel_booking']

    def get_latest_booking(self, obj):
         now = timezone.now()
         bookings = Booking.objects.filter(car=obj).order_by('-pickup_date', '-pickup_time')

         for booking in bookings:
             pickup_naive = datetime.combine(booking.pickup_date, booking.pickup_time)
             dropoff_naive = datetime.combine(booking.dropoff_date, booking.dropoff_time)

        # Make datetimes timezone-aware
             pickup = timezone.make_aware(pickup_naive, timezone.get_current_timezone())
             dropoff = timezone.make_aware(dropoff_naive, timezone.get_current_timezone())

             if dropoff >= now:
                return booking
         return None
    
    
    def pickup_datetime(self, obj):
        booking = self.get_latest_booking(obj)
        if booking:
            return f"{booking.pickup_date} {booking.pickup_time}"
        return "—"

    def dropoff_datetime(self, obj):
        booking = self.get_latest_booking(obj)
        if booking:
            return f"{booking.dropoff_date} {booking.dropoff_time}"
        return "—"

    def cancel_booking(self, request, queryset):
        """Cancel bookings and clear status."""
        count = 0
        for car in queryset:
            # Delete future or current bookings
            now = timezone.now()
            Booking.objects.filter(car=car).filter(
                dropoff_date__gte=now.date()
            ).delete()

            # Reset booking status
            car.is_booked = False
            car.available_from = None
            car.save()
            count += 1

        self.message_user(request, f"Booking cancelled for {count} car(s).")

    cancel_booking.short_description = "Cancel selected car bookings"


class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'car', 'user', 'pickup_date', 'pickup_time', 'dropoff_date', 'dropoff_time',
         'driving_licence', 'residence_proof',
        'pan_card', 'aadhaar_card', 'payment_screenshot'
    )

    def document_links(self, obj):
        links = []
        for field in ['driving_licence', 'residence_proof', 'pan_card', 'aadhaar_card', 'payment_screenshot']:
            file = getattr(obj, field)
            if file:
                links.append(f'<a href="{file.url}" target="_blank">{field}</a>')
        return format_html('<br>'.join(links))
    document_links.short_description = 'Documents'
    
    def document_previews(self, obj):
        previews = []
        for field in ['driving_licence', 'residence_proof', 'pan_card', 'aadhaar_card', 'payment_screenshot']:
            file = getattr(obj, field)
            if file:
                if field == 'payment_screenshot':  # For images
                    previews.append(f'<h3>{field.title()}</h3><img src="{file.url}" style="max-width: 300px; max-height: 300px;">')
                else:  # For PDFs and other files
                    previews.append(f'<h3>{field.title()}</h3><a href="{file.url}" target="_blank">View {field}</a>')
        return format_html('<br>'.join(previews))
    document_previews.short_description = 'Document Previews'
    # def view_driving_licence(self, obj):
    #     if obj.driving_licence:
    #         return format_html("<a href='{}' target='_blank'>View</a>", obj.driving_licence.url)
    #     return "Not uploaded"
    # view_driving_licence.short_description = "Driving Licence"

    # def view_pune_residence_proof(self, obj):
    #     if obj.pune_residence_proof:
    #         return format_html("<a href='{}' target='_blank'>View</a>", obj.pune_residence_proof.url)
    #     return "Not uploaded"
    # view_pune_residence_proof.short_description = "Pune Residence Proof"

    # def view_pan_card(self, obj):
    #     if obj.pan_card:
    #         return format_html("<a href='{}' target='_blank'>View</a>", obj.pan_card.url)
    #     return "Not uploaded"
    # view_pan_card.short_description = "PAN Card"

    # def view_adhar_card(self, obj):
    #     if obj.adhar_card:
    #         return format_html("<a href='{}' target='_blank'>View</a>", obj.adhar_card.url)
    #     return "Not uploaded"
    # view_adhar_card.short_description = "Aadhar Card"

    # def view_screenshot_of_payment(self, obj):
    #     if obj.screen_shot_Of_Payment:
    #         return format_html("<a href='{}' target='_blank'>View</a>", obj.screen_shot_Of_Payment.url)
    #     return "Not uploaded"
    # view_screenshot_of_payment.short_description = "Payment Screenshot"






admin.site.register(Car, CarAdmin)
admin.site.register(registermodel, RegistrationAdmin)
admin.site.register(Booking, BookingAdmin)


