import telebot
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
import os
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
import os
import shutil

# توکن بات تلگرام
bot = telebot.TeleBot('8229602776:AAEUDYXiqqP6nuN3IPvTZTBcwF6bIt2htro')

# مسیر ذخیره موقت فایل‌ها
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ذخیره فایل MP3 و تصویر
user_files = {}


@bot.message_handler(content_types=['audio', 'photo'])
def handle_files(message):
    chat_id = message.chat.id

    if message.audio:
        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        mp3_path = os.path.join(DOWNLOAD_FOLDER, f"{chat_id}_music.mp3")
        with open(mp3_path, 'wb') as f:
            f.write(downloaded_file)
        user_files[chat_id] = {'mp3': mp3_path}
        bot.reply_to(
            message, "فایل MP3 دریافت شد. حالا لطفاً عکس کاور را بفرست.")

    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = os.path.join(DOWNLOAD_FOLDER, f"{chat_id}_cover.jpg")
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)
        if chat_id in user_files and 'mp3' in user_files[chat_id]:
            user_files[chat_id]['image'] = image_path
            embed_cover_and_send(chat_id, user_files[chat_id], message)


def embed_cover_and_send(chat_id, files, message):
    try:
        input_path = files['mp3']
        image_path = files['image']
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{chat_id}_output.mp3")

        # 1. کپی فایل MP3 برای ویرایش
        shutil.copy(input_path, output_path)

        # 2. بارگذاری فایل جدید با mutagen
        audio = MP3(output_path, ID3=ID3)

        # 3. حذف تگ‌های قبلی کاور (APIC)
        if audio.tags is None:
            audio.add_tags()
        else:
            audio.tags.delall('APIC')  # 🔥 حذف همه کاورها

        # 4. افزودن کاور جدید
        with open(image_path, 'rb') as img:
            audio.tags.add(
                APIC(
                    encoding=3,               # UTF-8
                    mime='image/jpeg',        # یا 'image/png' بسته به نوع تصویر
                    type=3,                   # cover (front)
                    desc='Cover',
                    data=img.read()
                )
            )


        # 5. ذخیره فایل
        audio.save(v2_version=3)  # برای سازگاری با اکثر پلیرها

        # 6. ارسال فایل نهایی
        with open(output_path, 'rb') as audio_file, open(image_path, 'rb') as thumb_file:
            bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                caption="✅ فایل نهایی با کاور جدید آماده است!",
                thumb=thumb_file,
                
            )

    except Exception as e:
        bot.send_message(chat_id, f"خطا هنگام افزودن کاور: {e}")
# شروع ربات
print("Bot is running...")
bot.infinity_polling()