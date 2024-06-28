from email import encoders
from io import BytesIO
import mimetypes
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from django.http import HttpResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def create_message(sender, to, subject, body, files=None):
    
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message['from'] = sender
    
    message.attach(MIMEText(body))
    
    if files:
        for file in files:
            file_name = file.name
            content_type, encoding = mimetypes.guess_type(file_name)
            if content_type is None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            with BytesIO(file.read()) as f:
                payload = f.read()
            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(payload)
            attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
            encoders.encode_base64(attachment)
            message.attach(attachment)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
    except HttpError as error:
        message = None
        print('An error occurred here: %s' % error)
        raise HttpError()
    return message

def send_email(request, to, subject, body, files=None):
    # Get the user's credentials
    social_account = request.user.socialaccount_set.filter(provider='google').first()
    credentials = Credentials.from_authorized_user_info(
        info= {
            'refresh_token' : social_account.socialtoken_set.first().token_secret,
            'client_secret' : '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',
            'client_id' : '38195798029-sdjmqjh6u5cgk30o54nv6fue38al2u83.apps.googleusercontent.com'
        }
    )

    # Create a Gmail API client
    service = build('gmail', 'v1', credentials=credentials)

    # Send a message
    try:
        message = create_message(request.user.email, to, subject, body, files)
        message = send_message(service, 'me', message)
        '''if message is not None:
            message = (service.users().messages().get(userId='me', id=message['id'], format='full').execute())
            print(message['payload'])
            headers = message['payload']['headers']
            print(message['payload'])
            for header in headers:
                if header['name'] == 'X-Failed-Recipients':
                    print("bad email")
                    raise Exception('Bad email')'''
    except HttpError:
        raise HttpError()
        
