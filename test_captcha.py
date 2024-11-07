import requests
from PIL import Image, ImageEnhance
from io import BytesIO
import pytesseract

# تحميل صورة الكابتشا
captcha_url = "https://adsl.yemen.net.ye/captcha/docap.aspx"
response = requests.get(captcha_url)

# فتح الصورة باستخدام PIL
captcha_image = Image.open(BytesIO(response.content))

# تحسين جودة الصورة (تحويل إلى رمادي وزيادة التباين)
captcha_image = captcha_image.convert('L')  # تحويل إلى اللون الرمادي
enhancer = ImageEnhance.Contrast(captcha_image)
captcha_image = enhancer.enhance(2)  # زيادة التباين

# التعرف على النص باستخدام pytesseract
captcha_text = pytesseract.image_to_string(captcha_image, config='--psm 6 digits')

print("نص الكابتشا المستخرج:", captcha_text)
