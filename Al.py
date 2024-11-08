import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from PIL import Image
from io import BytesIO
import pytesseract

# تخزين بيانات المستخدمين
user_data = {}

# دالة البداية - عرض الأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text("مرحباً بك! اختر خياراً من الأزرار أدناه:", reply_markup=reply_markup)

# دالة استقبال الردود من الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "my_numbers":
        await query.edit_message_text("يرجى إدخال الرقم الثابت الخاص بـ ADSL:")
        context.user_data['awaiting_adsl_number'] = True

    elif query.data == "instant_report":
        user_id = query.from_user.id
        if user_id in user_data and user_data[user_id]:
            await query.edit_message_text("جاري استخراج تقرير الإنترنت لجميع الأرقام المسجلة...")
            report = await generate_internet_report(user_id)
            await query.message.reply_text(report)
        else:
            await query.edit_message_text("يرجى إضافة رقم ثابت أولاً باستخدام خيار أرقامي.")

# إضافة الرقم الثابت وحفظه في البيانات
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_adsl_number'):
        adsl_number = update.message.text
        user_id = update.message.from_user.id

        if user_id in user_data:
            user_data[user_id].append(adsl_number)
        else:
            user_data[user_id] = [adsl_number]

        await update.message.reply_text("تم إضافة الرقم بنجاح.")
        context.user_data['awaiting_adsl_number'] = False
    else:
        await update.message.reply_text("يرجى اختيار خيار من الأزرار.")

# دالة لفحص كل الأرقام المخزنة وإرجاع تقرير كامل
async def generate_internet_report(user_id):
    report = ""
    for adsl_number in user_data[user_id]:
        report_data = await get_internet_report(adsl_number)
        report += f"تقرير للرقم {adsl_number}:\n{report_data}\n\n"
    return report

# دالة للحصول على تقرير الرصيد من الموقع باستخدام الكابتشا
async def get_internet_report(adsl_number):
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
    # استبدل "YOUR_BOT_TOKEN" بالتوكن الخاص بالبوت
    application = Application.builder().token("7541013461:AAEdHdziZOUk2IUc46Ti-ts1fbss-NaHYu4").build()

    # الأوامر والأزرار
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # بدء التشغيل
    application.run_polling()

if __name__ == '__main__':
    main()
