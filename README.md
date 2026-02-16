# 🎵 Mashup Service: Automated Audio Mixing Web App

A full-stack web application that automates the creation of audio
mashups.

This tool takes a singer's name, downloads a specified number of their
songs from YouTube, trims them to a set duration, merges them into a
single continuous audio track, compresses the result, and emails it
directly to the user.

------------------------------------------------------------------------

## 🚀 Live Deployment

-   **Web Service:**
    https://huggingface.co/spaces/pranavvaish20/Mashup-Services
-   **Author:** Pranav Vaish\
-   **LinkedIn:** https://www.linkedin.com/in/pranavvaish20/

------------------------------------------------------------------------

## 🛠️ How It Works (Pipeline Overview)

### 1️⃣ Input Handling

The user provides: - Singer Name - Number of Videos (N) - Duration (Y
seconds) - Email ID

### 2️⃣ YouTube Search & Filtering

-   Uses `yt-dlp` for search and extraction
-   Filters long videos (\>10 mins)
-   Uses `YOUTUBE_COOKIES` for authentication

### 3️⃣ Audio Processing

-   Extracts best quality audio
-   Converts to MP3 using FFmpeg
-   Trims first Y seconds using moviepy
-   Merges all clips

### 4️⃣ Delivery

-   Compresses into ZIP
-   Sends via Gmail SMTP using App Password

------------------------------------------------------------------------

## 📊 Sample Test Case

  Parameter      Value
  -------------- ---------------
  Singer         Arijit Singh
  Videos (N)     10
  Duration (Y)   20 seconds
  Final Length   \~200 seconds

------------------------------------------------------------------------

## 💻 Tech Stack

-   Python 3.11
-   Flask
-   moviepy
-   ffmpeg
-   yt-dlp
-   Docker
-   smtplib

------------------------------------------------------------------------

## ⚙️ Local Setup

### Clone Repo

``` bash
git clone https://github.com/pranavvaish20/Mashup-Services.git
cd Mashup-Services
```

### Install Dependencies

``` bash
pip install -r requirements.txt
```

### Configure .env

``` env
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
YOUTUBE_COOKIES=your_cookies
```

### Run App

``` bash
python app.py
```

Visit: http://127.0.0.1:5000

------------------------------------------------------------------------

## 🛡️ License

MIT License

------------------------------------------------------------------------

⭐ Star the repository if you find it useful!
