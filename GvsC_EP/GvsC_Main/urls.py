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
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/$', views.tournaments_details, name='tournament_details'),
    # ex: /tournaments/5/next_round
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/next_round/$', views.tournaments_next_round, name='index'),
    # ex: /tournaments/5/submit_result
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/submit_result/$', views.tournaments_report_match_result, name='index'),
    # ex: /tournaments/5/enroll_player
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/enroll_player/$', views.tournaments_enroll_player, name='tournaments_enroll_player'),
    # ex: /tournaments/5/enroll_new_player
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/enroll_new_player/$', views.tournaments_enroll_new_player, name='tournaments_enroll_new_player'),
    # ex: /tournaments/5/enroll_new_player
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/remove_player/$', views.tournaments_remove_player,
        name='tournaments_remove_player'),
    # ex: /tournaments/5/enroll_new_player
    url(r'^tournaments/(?P<tournament_id>[0-9]+)/drop_player/$', views.tournaments_drop_player,
        name='tournaments_drop_player'),
]