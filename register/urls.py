from django.urls import path
from django.views import View
from register.views import userloginview,userprofileview,CarListView,FindCarView,BookCarView,registrationview,ChangePasswordView

urlpatterns=[ 
    path('register/',registrationview.as_view(),name='Register'),
    path('login/',userloginview.as_view(),name='Login'),
    path('profile/',userprofileview.as_view(),name='User_Profile'),
    path('cars/', CarListView.as_view(), name='car-list'),
    path('findcar/', FindCarView.as_view(), name='find_car'),
    path('bookcar/', BookCarView.as_view(), name='book_car'),
    path('changepass/', ChangePasswordView.as_view(), name='change-password'),
]            









