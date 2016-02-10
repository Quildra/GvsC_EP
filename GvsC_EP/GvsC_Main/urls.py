from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^events/$', views.events_index, name='index'),
    # ex: /events/5/
    url(r'^events/(?P<event_id>[0-9]+)/$', views.events_details, name='index'),
    # ex: /tournaments/
    url(r'^tournaments/$', views.tournaments_index, name='index'),
    # ex: /tournaments/5/
    #url(r'^tournaments/(?P<tournament_id>[0-9]+)/$', views.tournaments_details, name='index'),
]