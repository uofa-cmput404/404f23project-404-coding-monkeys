# DFB pg. 177
from django.urls import path
from inbox import views


urlpatterns = [
    path("", views.inbox_view, name="inbox"),
    path("follow_request", views.follow_request_handler, name="send_follow_req"),
    path('<str:author_id>/posts/<int:inbox_index>', views.inbox_post, name='inbox_post_view'),
]

# note there is no login/ or logout/, because django handles their views automatically
