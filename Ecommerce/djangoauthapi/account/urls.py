from django.urls import path
from account import views
urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('product/', views.ProductView.as_view(), name='product'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='productdetail'),
    path('add-to-cart/', views.AddCartView.as_view(), name='AddtoCart'),
    path('add-to-cart/<int:pk>/', views.AddCartView.as_view(), name='AddtoCart'),
    path('show-cart/', views.ShowCartView.as_view(), name='ShowCart'),
    path('category/<str:val>/', views.CategoryView.as_view(), name='category'),
    path('address/', views.AddressView.as_view(), name='show-address'),
    path('orderplaced/', views.OrderPlacedView.as_view(), name='orderplaced'),
    path('changepassword/', views.UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', views.SendPasswordResetEmailView.as_view() , name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', views.UserPasswordResetView.as_view() , name='reset-password'),
]
