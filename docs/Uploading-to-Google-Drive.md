# Uploading to Google Drive

To upload a Docx file to Google Drive as a Google document, use
`foliant upload MyFile.docx` or `foliant build gdrive`, which is
a shortcut for generating a Docx file and uploading it.

For the upload to work, you need to have a so called *client secret* file.
Foliant looks for `client_secrets.json` file in the current directory.

Client secret file is obtained through Google API Console. You probably don't
need to obtain it yourself. The person who told you to use Foliant should
provide you this file as well. If not, here's how you get it:

1. Open [https://console.developers.google.com/](https://console.developers.google.com/) page in your browser
2. Open **Library** tab
3. Choose *Drive API* in *G Suite API* section
4. Press **Turn on** button
5. Open **Credentials** tab
6. Press **Create credentials** button
7. Choose *OAuth client ID*
8. Choose *Other* application type
9. Enter app name (any you want and understand in the future)
10. Press **OK** button
11. The line with data will appear. Press **Download json file** button

> **Important**
>
> Don't show, upload, or pass to third parties this json file. Is called secrets for a reason.
