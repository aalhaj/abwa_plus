def solve_captcha():
    captcha_url = 'https://adsl.yemen.net.ye/captcha/docap.aspx'
    response = requests.get(captcha_url)
    image = Image.open(io.BytesIO(response.content))
    captcha_text = pytesseract.image_to_string(image)
    return captcha_text
