import cv2
import pytesseract
from PIL import Image
import numpy as np

# تحميل صورة الكابتشا
captcha_image_path = 'https://adsl.yemen.net.ye/captcha/docap.aspx'  # استبدل بالمسار الصحيح للصورة
captcha_image = cv2.imread(captcha_image_path)

# تحويل الصورة إلى اللون الرمادي
gray_image = cv2.cvtColor(captcha_image, cv2.COLOR_BGR2GRAY)

# تطبيق فلتر لتقليل الضوضاء
denoised_image = cv2.medianBlur(gray_image, 3)

# تطبيق تقنية الكشف عن الحواف لتحسين الصورة
edges = cv2.Canny(denoised_image, 100, 200)

# استخراج النص باستخدام pytesseract
captcha_text = pytesseract.image_to_string(edges, config='--psm 6 outputbase digits')

print("CAPTCHA: ", captcha_text.strip())
