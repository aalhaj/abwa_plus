
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image
import pytesseract
import io

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s • %(name)s • %(levelname)s • %(message)s', level=logging.INFO)

# تخزين الأرقام
user_data = {}

# دالة /start
async def start(update: Update, context: CallbackContext) -> None:
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
    await update.message.reply_text('أهلاً بك! اختر خياراً:', reply_markup=reply_markup)

# دالة لالتقاط الأزرار
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == '10':
        await query.edit_message_text(text="أدخل الرقم الثابت الخاص بـ ADSL:")
        return 'WAITING_FOR_NUMBER'
    
    elif query.data == '3':
        if context.user_data.get('adsl_numbers'):
            await report_internet(query, context)
        else:
            await query.edit_message_text(text="لا توجد أرقام مخزنة.")

# دالة لتخزين الرقم
async def store_number(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    number = update.message.text
    if user_id not in user_data:
        user_data[user_id] = []
    user_data[user_id].append(number)
    await update.message.reply_text(f"تم تخزين الرقم: {number}")

# دالة لفحص الأرقام
async def report_internet(query, context):
    for number in context.user_data.get('adsl_numbers'):
        captcha_image = requests.get("https://adsl.yemen.net.ye/captcha/docap.aspx").content
        captcha_text = ocr_captcha(captcha_image)
        
        payload = {'username': number, 'password': '123456', 'captcha': captcha_text}
        response = requests.post("https://adsl.yemen.net.ye/ar/user_main.aspx", data=payload)

        if response.ok:
            balance = extract_balance(response.text)
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"رصيدك هو: {balance}")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="حدث خطأ أثناء التحقق من الرصيد.")

# دالة OCR
def ocr_captcha(captcha_image):
    image = Image.open(io.BytesIO(captcha_image))
    captcha_text = pytesseract.image_to_string(image, config='--psm 8 outputbase digits')
    return captcha_text.strip()

# دالة لاستخراج الرصيد
def extract_balance(response_text):
    return "مثال على الرصيد"

async def main():
    application = ApplicationBuilder().token("7541013461:AAEdHdziZOUk2IUc46Ti-ts1fbss-NaHYu4").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, store_number))
    application.add_handler(CallbackContext(button))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
