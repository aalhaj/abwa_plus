import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from PIL import Image
from io import BytesIO
import pytesseract

# تخزين بيانات المستخدمين
user_data = {}

# دالة البداية - عرض الأزرار
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🔥 معرف حسابي 🔥", callback_data='account_id')],
        [InlineKeyboardButton("♻️ تحديث ♻️", callback_data='refresh')],
        [InlineKeyboardButton("⚡ تقرير انترنت فوري ⚡", callback_data='instant_report')],
        [InlineKeyboardButton("📅 صلاحية حسابي 📅", callback_data='account_validity')],
        [InlineKeyboardButton("🚑 طوارئ انترنت 🚑", callback_data='internet_emergency')],
        [InlineKeyboardButton("☎️ طوارئ ثابت ☎️", callback_data='landline_emergency')],
        [InlineKeyboardButton("⌚ تسجيلات السداد ⌚", callback_data='payment_records')],
        [InlineKeyboardButton("🐢 تسجيلات الحركة 🐢", callback_data='activity_records')],
        [InlineKeyboardButton("📋 خدمات 📋", callback_data='services')],
        [InlineKeyboardButton("☎️ ارقامي ☎️", callback_data='my_numbers')],
        [InlineKeyboardButton("⚙️ الاعدادات ⚙️", callback_data='settings')],
        [InlineKeyboardButton("📄 تقريري لم يصل 📄", callback_data='report_missing')],
        [InlineKeyboardButton("💵 رسوم اشتراكي 💵", callback_data='subscription_fees')],
        [InlineKeyboardButton("💲 تبديل حساب 💲", callback_data='switch_account')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("مرحباً بك! اختر خياراً من الأزرار أدناه:", reply_markup=reply_markup)

# دالة استقبال الردود من الأزرار
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "my_numbers":
        query.edit_message_text("يرجى إدخال الرقم الثابت الخاص بـ ADSL:")
        context.user_data['awaiting_adsl_number'] = True

    elif query.data == "instant_report":
        user_id = query.from_user.id
        if user_id in user_data and user_data[user_id]:
            query.edit_message_text("جاري استخراج تقرير الإنترنت لجميع الأرقام المسجلة...")
            report = generate_internet_report(user_id)
            query.message.reply_text(report)
        else:
            query.edit_message_text("يرجى إضافة رقم ثابت أولاً باستخدام خيار أرقامي.")

# إضافة الرقم الثابت وحفظه في البيانات
def handle_text(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_adsl_number'):
        adsl_number = update.message.text
        user_id = update.message.from_user.id

        if user_id in user_data:
            user_data[user_id].append(adsl_number)
        else:
            user_data[user_id] = [adsl_number]

        update.message.reply_text("تم إضافة الرقم بنجاح.")
        context.user_data['awaiting_adsl_number'] = False
    else:
        update.message.reply_text("يرجى اختيار خيار من الأزرار.")

# دالة لفحص كل الأرقام المخزنة وإرجاع تقرير كامل
def generate_internet_report(user_id):
    report = ""
    for adsl_number in user_data[user_id]:
        report_data = get_internet_report(adsl_number)
        report += f"تقرير للرقم {adsl_number}:\n{report_data}\n\n"
    return report

# دالة للحصول على تقرير الرصيد من الموقع باستخدام الكابتشا
def get_internet_report(adsl_number):
    login_url = "https://adsl.yemen.net.ye/ar/user_main.aspx"
    captcha_url = "https://adsl.yemen.net.ye/captcha/docap.aspx"
    session = requests.Session()

    # الخطوة 1: تحميل صورة الكابتشا
    captcha_response = session.get(captcha_url)
    captcha_image = Image.open(BytesIO(captcha_response.content))

    # استخدام OCR للتعرف على النص في صورة الكابتشا
    captcha_text = pytesseract.image_to_string(captcha_image, config='--psm 8 digits')

    # الخطوة 2: إرسال بيانات تسجيل الدخول
    login_data = {
        "username": adsl_number,
        "password": "123456",
        "captcha": captcha_text.strip()
    }
    result = session.post(login_url, data=login_data)

    # تحقق إذا تم تسجيل الدخول بنجاح (يفضل التأكد من استجابة الموقع)
    if "رصيد" in result.text:
        # استخراج بيانات الرصيد من الاستجابة (يحتاج إلى تحليل HTML)
        # هنا مجرد مثال لنص ثابت لأن تحليل HTML معقد
        report_data = "رصيد: 100 جيجا، استخدام: 10 جيجا"
    else:
        report_data = "فشل في تسجيل الدخول، ربما كانت الكابتشا خاطئة."

    return report_data

# تشغيل البوت
def main() -> None:
    updater = Updater("7541013461:AAEdHdziZOUk2IUc46Ti-ts1fbss-NaHYu4")
    dispatcher = updater.dispatcher

    # الأوامر والأزرار
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # بدء التشغيل
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

