import os
import base64
import random
import string
import py7zr
import requests
import json
import pickle
import io
import mimetypes
import datetime
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for accessing Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    token_path = os.path.join(tempfile.gettempdir(), 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Please choose your credentials.json file")
            root = tk.Tk()
            root.withdraw()
            credentials_path = filedialog.askopenfilename(title="Select credentials.json file", filetypes=[("JSON files", "*.json")])
            if not credentials_path:
                print("No file selected. Exiting.")
                exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def save_attachment(part, msg_id, service, path):
    try:
        att_id = part['body']['attachmentId']
        att = service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()
        data = att['data']
        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
        with open(path, 'wb') as f:
            f.write(file_data)
        print(f"Saved attachment: {path}")
    except Exception as e:
        print(f"An error occurred while saving attachment: {e}")

def save_text_content(data, path):
    try:
        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
        with open(path, 'wb') as f:
            f.write(file_data)
        print(f"Saved text content: {path}")
    except Exception as e:
        print(f"An error occurred while saving text content: {e}")

def handle_message_part(part, msg_id, service, base_path):
    if part.get('filename'):
        save_attachment(part, msg_id, service, os.path.join(base_path, part['filename']))
    else:
        mime_type = part.get('mimeType')
        body = part.get('body', {})
        data = body.get('data')

        if mime_type == 'text/plain' and data:
            save_text_content(data, os.path.join(base_path, f"{msg_id}.txt"))
        elif mime_type == 'text/html' and data:
            save_text_content(data, os.path.join(base_path, f"{msg_id}.html"))
        elif mime_type == 'multipart':
            for subpart in part.get('parts', []):
                handle_message_part(subpart, msg_id, service, base_path)

def parse_email_date(date_str):
    # Remove parenthesized content and timezone abbreviations
    if '(' in date_str:
        date_str = date_str.split('(')[0].strip()
    if 'GMT' in date_str:
        date_str = date_str.replace('GMT', '').strip()
    # Try parsing with various formats
    for date_format in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S", "%d %b %Y %H:%M:%S"]:
        try:
            return datetime.datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    print(f"Failed to parse date: {date_str}")
    return None

def download_emails(service):
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])
    
    temp_dir = tempfile.mkdtemp()

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message.get('payload', {})
        headers = message.get('payload', {}).get('headers', [])
        
        date_str = next(header['value'] for header in headers if header['name'] == 'Date')
        date_obj = parse_email_date(date_str)
        
        if date_obj:
            year = date_obj.strftime("%Y")
            month = date_obj.strftime("%m")
            day = date_obj.strftime("%d")
        else:
            year, month, day = 'unknown', 'unknown', 'unknown'
        
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        safe_subject = ''.join(c for c in subject if c.isalnum() or c in ' _-').rstrip()

        base_path = os.path.join(temp_dir, year, month, day, f"{safe_subject}_{msg_id}")

        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        parts = payload.get('parts', [])
        
        if not parts:
            body = payload.get('body', {}).get('data')
            if body:
                save_text_content(body, os.path.join(base_path, f"{msg_id}.txt"))
        else:
            for part in parts:
                handle_message_part(part, msg_id, service, base_path)

    return temp_dir, messages

def create_7z(folder, password, archive_path):
    try:
        print(f"Creating 7z archive at {archive_path} with password.")
        with py7zr.SevenZipFile(archive_path, 'w', password=password) as archive:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder)
                    if file_path != archive_path:  # Exclude the archive file itself
                        print(f"Adding {file_path} as {arcname}")
                        archive.write(file_path, arcname)
        print(f"7z archive created at {archive_path}")
    except Exception as e:
        print(f"An error occurred while creating 7z archive: {e}")

def upload_to_gofile(archive_path):
    print(f"Uploading {archive_path} to gofile.io.")
    with open(archive_path, 'rb') as file:
        response = requests.post('https://api.gofile.io/uploadFile', files={'file': file})
    result = response.json()
    print(f"Upload complete. Download link: {result['data']['downloadPage']}")
    return result['data']['downloadPage']

def store_locally(archive_path):
    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.askdirectory(title="Select the folder to save the 7z file")
    if save_path:
        final_path = os.path.join(save_path, os.path.basename(archive_path))
        shutil.move(archive_path, final_path)
        print(f"The 7z file has been stored at: {final_path}")
        return final_path
    return None

def delete_temp_files(temp_dir):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Deleted temporary directory: {temp_dir}")
    token_path = os.path.join(tempfile.gettempdir(), 'token.pickle')
    if os.path.exists(token_path):
        os.remove(token_path)
        print(f"Deleted token file: {token_path}")

def delete_emails(service, messages):
    for msg in messages:
        service.users().messages().delete(userId='me', id=msg['id']).execute()
    print("All downloaded emails have been deleted from your Gmail account.")

def main():
    service = get_gmail_service()
    temp_dir, messages = download_emails(service)
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    
    archive_filename = 'emails.7z'
    archive_path = os.path.join(temp_dir, archive_filename)
    create_7z(temp_dir, password, archive_path)
    
    print(f'Random Password: {password}')
    
    choice = input("Do you want to upload the 7z file to gofile.io or store it locally? (Enter 'upload' or 'local'): ").strip().lower()
    
    if choice == 'upload':
        download_link = upload_to_gofile(archive_path)
        print(f'Download Link: {download_link}')
    elif choice == 'local':
        final_path = store_locally(archive_path)
        if final_path:
            print(f'The 7z file has been stored at: {final_path}')
    else:
        print("Invalid choice. Exiting.")
        return
    
    delete_choice = input("Do you want to delete all downloaded emails from your Gmail account? (Enter 'yes' or 'no'): ").strip().lower()
    
    if delete_choice == 'yes':
        delete_emails(service, messages)
        print("All downloaded emails have been deleted from your Gmail account.")
    else:
        print("Emails were not deleted from your Gmail account.")
    
    delete_temp_files(temp_dir)

if __name__ == '__main__':
    main()
