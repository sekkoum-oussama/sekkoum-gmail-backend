from urllib.parse import urlencode
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.db.models import Q
from message.models import Message
from message.permissions import IsOwnerOrReadOnly
from message.utils import send_email
from .serializers import MessageSerializer, DraftMessageSerializer
from google.auth.exceptions import RefreshError
from django.shortcuts import redirect
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.conf import settings
from django.utils import timezone

class MessageListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def create(self, request, *args, **kwargs):
        attachments = request.FILES.getlist("attachments", None)
        serializer = self.serializer_class(data=request.data, context={"attachments" : attachments, "request":request})
        serializer.is_valid(raise_exception=True)
        try:
            send_email(request, request.data.get('receivers'), request.data.get('object', None), request.data.get('text', ''), attachments)
        except RefreshError:
            params={
                "scope" : ' '.join(settings.SOCIALACCOUNT_PROVIDERS['google']['SCOPE']),
                "response_type" : "code",
                "redirect_uri" : "http://localhost:8000",
                "client_id" : "38195798029-sdjmqjh6u5cgk30o54nv6fue38al2u83.apps.googleusercontent.com",
                "access_type" : "offline", 
            }
            print("redirected")
            encoded_params = urlencode(params)
            return redirect(f'{GoogleOAuth2Adapter.authorize_url}?{encoded_params}')
        except Exception as error:
            print(error)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = Message.objects.filter(
            receivers__icontains=self.request.user.email,
            sent=True,
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset
        
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user, sent=True, sent_at=timezone.now())


class MessageRetrive(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            id=self.kwargs['pk'],
            receivers__icontains=self.request.user.email,
            sent=True
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset


class SentMessages(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            sender=self.request.user,
            sent=True
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset


class SentMessage(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            id=self.kwargs['pk'],
            sender=self.request.user,
            sent=True
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset



class DraftMessages(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DraftMessageSerializer

    def create(self, request, *args, **kwargs):
        attachments = request.FILES.getlist("attachments", None)
        receivers_emails = request.data.get("receivers_emails", None)
        serializer = self.serializer_class(data=request.data, partial=True, context={"attachments" : attachments, "request":request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = Message.objects.filter(
            sender=self.request.user,
            sent=False
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset
    
    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user)


class DraftMessage(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DraftMessageSerializer
    queryset = Message.objects.filter(sent=False)
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        attachments = request.FILES.getlist("attachments", None)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={"attachments" : attachments, "request":request})
        serializer.is_valid(raise_exception=True)
        sent = serializer.validated_data.get('sent', None)
        if sent and not instance.sent:
            # Send email and update 'sent' field to True if the email is sent successfully
            try:
                receivers = serializer.validated_data.get('receivers', instance.receivers)
                object = serializer.validated_data.get('object', instance.object)
                text = serializer.validated_data.get('text', instance.text)
                send_email(request, receivers, object, text, attachments)
            except RefreshError:
                params={
                    "scope" : ' '.join(settings.SOCIALACCOUNT_PROVIDERS['google']['SCOPE']),
                    "response_type" : "code",
                    "redirect_uri" : "http://localhost:8000",
                    "client_id" : "38195798029-sdjmqjh6u5cgk30o54nv6fue38al2u83.apps.googleusercontent.com",
                    "access_type" : "offline", 
                }
                encoded_params = urlencode(params)
                return redirect(f'{GoogleOAuth2Adapter.authorize_url}?{encoded_params}')
            except Exception as error:
                print(f'Errror => {error}')
                return Response(status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data
            validated_data['sent'] = True
            validated_data['sent_at'] = timezone.now()

        self.perform_update(serializer)
        return Response(serializer.data)

class StarredMessages(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            starred=self.request.user
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset


class ImportantMessages(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            important=self.request.user
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user) | Q(spam=self.request.user))
        return queryset


class SpamMessages(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            spam=self.request.user
        ).exclude(Q(invisible_to=self.request.user) | Q(trash=self.request.user))
        return queryset 


class TrashMessages(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        queryset = Message.objects.filter(
            trash=self.request.user
        ).exclude(invisible_to=self.request.user)
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addToStarred(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.starred.add(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def removeFromStarred(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.starred.remove(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addToImportant(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.important.add(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def removeFromImportant(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.important.remove(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addToSpam(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.spam.add(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def removeFromSpam(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.spam.remove(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addToTrash(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.trash.add(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def removeFromTrash(request, pk):
    message = get_object_or_404(Message,id=pk)
    message.trash.remove(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addToInvisible(request, pk):
    message = get_object_or_404(Message,id=pk)
    if message.trash.filter(pk=request.user.id).exists():
        message.trash.remove(request.user)
        message.invisible_to.add(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)