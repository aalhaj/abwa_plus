
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image
import pytesseract
import io

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s • %(name)s • %(levelname)s • %(message)s', level=logging.INFO)

# تخزين الأرقام
user_data = {}

# دالة /start
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🔥 معرف حسابي 🔥", callback_data='1')],
        [InlineKeyboardButton("♻️ تحديث ♻️", callback_data='2')],
        [InlineKeyboardButton("⚡ تقرير انترنت فوري ⚡", callback_data='3')],
        [InlineKeyboardButton("📅 صلاحية حسابي 📅", callback_data='4')],
        [InlineKeyboardButton("🚑 طوارئ انترنت 🚑", callback_data='5')],
        [InlineKeyboardButton("☎️ طوارئ ثابت ☎️", callback_data='6')],
        [InlineKeyboardButton("⌚ تسجيلات السداد ⌚", callback_data='7')],
        [InlineKeyboardButton("🐢 تسجيلات الحركة 🐢", callback_data='8')],
        [InlineKeyboardButton("📋 خدمات 📋", callback_data='9')],
        [InlineKeyboardButton("☎️ ارقامي ☎️", callback_data='10')],
        [InlineKeyboardButton("⚙️ الاعدادات ⚙️", callback_data='11')],
        [InlineKeyboardButton("📄 تقريري لم يصل 📄", callback_data='12')],
        [InlineKeyboardButton("💵 رسوم اشتراكي 💵", callback_data='13')],
        [InlineKeyboardButton("💲 تبديل حساب 💲", callback_data='14')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('أهلاً بك! اختر خياراً:', reply_markup=reply_markup)

# دالة لالتقاط الأزرار
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == '10':
        query.edit_message_text(text="أدخل الرقم الثابت الخاص بـ ADSL:")
        return 'WAITING_FOR_NUMBER'
    
    elif query.data == '3':
        if context.user_data.get('adsl_numbers'):
            report_internet(query, context)
        else:
            query.edit_message_text(text="لا توجد أرقام مخزنة.")

# دالة لتخزين الرقم
def store_number(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    number = update.message.text
    if user_id not in user_data:
        user_data[user_id] = []
    user_data[user_id].append(number)
    update.message.reply_text(f"تم تخزين الرقم: {number}")

# دالة لفحص الأرقام
def report_internet(query, context):
    # تنفيذ الطلب إلى الموقع
    for number in context.user_data.get('adsl_numbers'):
        # هنا يتم تنفيذ عمليات تسجيل الدخول والتحقق من الرصيد باستخدام OCR
        # مثال على كيفية استخدام OCR
        captcha_image = requests.get("https://adsl.yemen.net.ye/captcha/docap.aspx").content
        captcha_text = ocr_captcha(captcha_image)  # دالة لتحويل الصورة إلى نص
        
        # تنفيذ الطلب باستخدام الرقم وكلمة المرور
        payload = {'username': number, 'password': '123456', 'captcha': captcha_text}
        response = requests.post("https://adsl.yemen.net.ye/ar/user_main.aspx", data=payload)

        # معالجة الاستجابة
        if response.ok:
            # استخراج البيانات المطلوبة من الاستجابة
            # مثال: الرصيد
            balance = extract_balance(response.text)  # دالة لاستخراج الرصيد
            
            context.bot.send_message(chat_id=query.message.chat_id, text=f"رصيدك هو: {balance}")
        else:
            context.bot.send_message(chat_id=query.message.chat_id, text="حدث خطأ أثناء التحقق من الرصيد.")

# دالة OCR
def ocr_captcha(captcha_image):
    image = Image.open(io.BytesIO(captcha_image))
    captcha_text = pytesseract.image_to_string(image, config='--psm 8 outputbase digits')
    return captcha_text.strip()

# دالة لاستخراج الرصيد
def extract_balance(response_text):
    # تحليل النص لاستخراج الرصيد
    # يجب استخدام تعبيرات عادية أو أدوات تحليل HTML
    return "مثال على الرصيد"

def main():
    updater = Updater("7541013461:AAEdHdziZOUk2IUc46Ti-ts1fbss-NaHYu4")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.text & ~filters.command, store_number))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
