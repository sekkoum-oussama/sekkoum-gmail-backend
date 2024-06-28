from message import views
from django.urls import path


urlpatterns = [
    path('sent/', views.SentMessages.as_view(), name='sent_messages'),
    path('sent/<int:pk>/', views.SentMessage.as_view(), name='sent_message'),
    path('draft/', views.DraftMessages.as_view(), name='draft_messages'),
    path('draft/<int:id>/', views.DraftMessage.as_view(), name='draft_message'),
    path('starred/', views.StarredMessages.as_view(), name=('starred_messages')),
    path('important/', views.ImportantMessages.as_view(), name='important_messages'),
    path('spam/', views.SpamMessages.as_view(), name='spam_messages'),
    path('trash/', views.TrashMessages.as_view(), name='trash_messages'),
    path('addstarr/<int:pk>/', views.addToStarred, name='add_starr'),
    path('removestarr/<int:pk>/', views.removeFromStarred, name='remove_starr'),
    path('addimportant/<int:pk>/', views.addToImportant, name='add_important'),
    path('removeimportant/<int:pk>/', views.removeFromImportant, name='remove_important'),
    path('addspam/<int:pk>/', views.addToSpam, name='add_spam'),
    path('removespam/<int:pk>/', views.removeFromSpam, name='remove_spam'),
    path('addtotrash/<int:pk>/', views.addToTrash, name='add_trash'),
    path('removefromtrash/<int:pk>/', views.removeFromTrash, name='remove_trash'),
    path('addtoinvisible/<int:pk>/', views.addToInvisible, name='add_invisible'),
    path('inbox/<int:pk>/', views.MessageRetrive.as_view(), name='message_details'),
    path('', views.MessageListCreate.as_view(), name='messages'),
]