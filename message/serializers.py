from email import message
import re
from rest_framework import serializers
from .models import Message, Attachment


class AttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['file']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='email')
    attachments = AttachmentsSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        exclude = ['invisible_to', 'starred', 'important', 'spam', 'archive', 'trash']
    
    def validate(self, attrs):
        receivers_emails = attrs.get('receivers', None)
        if receivers_emails is None:
            raise serializers.ValidationError({'receivers':'this list may not be empty'})
        receivers_emails = receivers_emails.split(",")
        if len(receivers_emails) > 20:
            raise serializers.ValidationError({'too_many_receivers':'you can send to 20 persons max'})
        email_pattern = r'^[-\w\.]+@([\w-]+\.)+[\w-]{2,4}$'
        for email in receivers_emails:
            if not re.match(email_pattern, str(email).strip()):
                raise serializers.ValidationError({'wrong_email_address':email})
        attachments = self.context["attachments"]
        if len(attachments) > 4:
            raise serializers.ValidationError({'files_limit_exceeded' : 'Only 4 files can be attached to an email at once'})
        for file in attachments:
            extension = file.name.split('.')[-1]
            if extension not in ['jpg', 'jpeg', 'mp4', 'pdf', 'doc', 'docx', 'dotx', 'xls', 'xlsx', 'ppt', 'pptx']:
                raise serializers.ValidationError({"wrong_file_format" : "Only pictures, videos, pdfs, word, excel and powerpoint files are accepted"})
        return super().validate(attrs)
    
    def create(self, validated_data):
        message = Message(**validated_data)
        message.save()
        attachments = self.context['attachments']
        for file in attachments:
            Attachment.objects.create(message=message, file=file)
        return message

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['starred'] = instance.starred.filter(id=self.context['request'].user.id).exists()
        representation['important'] = instance.important.filter(id=self.context['request'].user.id).exists()
        representation['spam'] = instance.spam.filter(id=self.context['request'].user.id).exists()
        representation['archive'] = instance.archive.filter(id=self.context['request'].user.id).exists()
        representation['trash'] = instance.trash.filter(id=self.context['request'].user.id).exists()
        return representation


class DraftMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='email')
    attachments = AttachmentsSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        exclude = ['invisible_to', 'starred', 'important', 'spam', 'archive', 'trash']
    
    def validate(self, attrs):
        receivers = attrs.get('receivers', getattr(self.instance, 'receivers', None))
        attachments = self.context.get("attachments", None)
        if self.instance is None:
            object = attrs.get('object', None)
            text = attrs.get('text', None)
            if not any([receivers, object, text, attachments]):
                raise serializers.ValidationError("all fields are empty")
        if 'receivers' in attrs:
            receivers = receivers.split(',')
            email_pattern = r'^[-\w\.]+@([\w-]+\.)+[\w-]{2,4}$'
            for i in range(len(receivers)-1, -1, -1):
                if not re.match(email_pattern, str(receivers[i]).strip()):
                    del receivers[i]
            attrs["receivers"] =  ','.join(receivers)
            receivers = attrs.get("receivers", None)
        if self.instance is not None:
            sent = attrs.get("sent", None)
            if sent is True and receivers in [None, '']:
                raise serializers.ValidationError("receivers not valid")
        if len(attachments) > 4:
            raise serializers.ValidationError({'files_limit_exceeded' : 'Only 4 files can be attached to an email at once'})
        for file in attachments:
            extension = file.name.split('.')[-1]
            if extension not in ['jpg', 'jpeg', 'mp4', 'pdf', 'doc', 'docx', 'dotx', 'xls', 'xlsx', 'ppt', 'pptx']:
                raise serializers.ValidationError({"wrong_file_format" : "Only pictures, videos, pdfs, word, excel and powerpoint files are accepted"})
        return super().validate(attrs)

    def create(self, validated_data):
        message = Message(**validated_data)
        message.sent=False
        message.save()
        attachments = self.context['attachments']
        for file in attachments:
            Attachment.objects.create(message=message, file=file)
        return message
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'attachments' in self.context:
            Attachment.objects.filter(message=instance).delete()
            attachments = self.context.get("attachments")
            for file in attachments:
                Attachment.objects.create(message=instance, file=file)
        return instance
            
    