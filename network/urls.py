from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('freelancer/<str:username>/', views.freelancer, name="freelancer"),
    path('upload', views.upload, name='upload'),
    path('search', views.search, name='search'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('events/<int:year>/<int:month>/',
         views.events, name='events'),
    path('events/<int:year>/<int:month>/<int:day>',
         views.events_date, name='events_date'),
    path('create_event/', views.create_event, name='create_event'),
    path('send-friend-request/<int:user_id>/',
         views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/',
         views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/',
         views.reject_friend_request, name='reject_friend_request'),
    path('friends/', views.friends_list, name='friends'),
    path('jobs/', views.job_listing_list, name='jobs'),
    path('create_job_listing/', views.create_job_listing,
         name='create_job_listing'),
    path('job_listing/<int:job_listing_id>/',
         views.job_listing_detail, name='job_listing_detail'),
    path('apply_for_job/<int:job_listing_id>/',
         views.apply_for_job, name='apply_for_job'),
    path('order/', views.order, name='order'),
    path('payments', views.payments, name='payments'),
    path('payment_list', views.payment_list, name='payment_list'),
    path('sell', views.sell, name='sell'),
    path('statistics', views.statistics, name='statistics'),
    path('statistics/<str:period>/', views.statistics, name='statistics'),
    path('toggle_follow/<int:user_id>/',
         views.toggle_follow, name='toggle_follow'),
    path('update_rating/', views.update_rating, name='update_rating'),
]
