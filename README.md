# g Downloader

Welcome to the **g Downloader** project! This powerful tool allows you to effortlessly download all your emails, including every attachment, from an active Gmail session. It then securely packs them into a 7z archive protected by a randomly generated password and offers the flexibility to either upload the archive to gofile.io or store it locally. 

## Key Features

- **Seamless Integration**: Authenticates using the Gmail API to securely access your emails.
- **Comprehensive Downloads**: Fetches all emails and attachments from your Gmail account.
- **Intuitive Organization**: Organizes emails by year, month, and day for easy navigation.
- **Secure Archiving**: Compresses the downloaded emails into a 7z archive with a randomly generated password for added security.
- **Flexible Storage Options**: Choose to either upload the archive to gofile.io or store it locally.
- **User-Friendly Interface**: Utilizes a simple command-line interface with clear prompts for user inputs.
- **Cleanup**: Ensures no temporary files are left behind, maintaining a clean working environment.

## How It Works

1. **Authentication**: Users are prompted to select their `credentials.json` file for Gmail API authentication.
2. **Download Emails**: The script downloads all emails and attachments, organizing them in a structured folder format.
3. **Archive Creation**: The emails are compressed into a 7z archive secured with a randomly generated password.
4. **Storage Options**: Users can choose to upload the archive to gofile.io or store it in a selected local directory.
5. **Cleanup**: All temporary files are deleted, and users have the option to delete the downloaded emails from their Gmail account.

## Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/Mefiseru/g-Downloader.git
cd g-Downloader
pip install -r req.txt
```

## Usage
Run the script using Python:

```bash
python g-downloader.py
```
Follow the on-screen prompts to authenticate, download emails, and choose your storage option.

## Dependencies
- **google-api-python-client**
- **google-auth-httplib2**
- **google-auth-oauthlib**
- **tkinter** OPTIONAL Only for executable compilation
- **py7zr**
- **requests**

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0). For more details, see the [LICENSE](https://github.com/Mefiseru/g-Downloader?tab=GPL-3.0-1-ov-file) file.

## Contributing
I welcome contributions to enhance the functionality and usability of this project. Feel free to fork the repository, make your changes, and submit a pull request.

## Support
For any issues or questions, please open an issue on GitHub or contact me directly.

**g Downloader** - Secure, Organize, and Store Your Emails Effortlessly!
