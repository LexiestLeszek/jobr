from playwright.sync_api import sync_playwright
import time
from PIL import Image
from scipy.ndimage import gaussian_filter
import numpy
import pytesseract
from PIL import ImageFilter

def solve_captcha(filename):
    # thresold1 on the first stage
    th1 = 140
    th2 = 140  # threshold after blurring
    sig = 1.5  # the blurring sigma
    from scipy import ndimage

    original = Image.open(filename)
    original.save("original.png")  # reading the image from the request
    black_and_white = original.convert("L")  # converting to black and white
    black_and_white.save("black_and_white.png")
    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    first_threshold.save("first_threshold.png")
    blur = numpy.array(first_threshold)  # create an image array
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    blurred.save("blurred.png")
    final = blurred.point(lambda p: p > th2 and 255)
    final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final = final.filter(ImageFilter.SHARPEN)
    final.save("final.png")
    number = pytesseract.image_to_string(Image.open('final.png'), lang='eng',
                                         config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789').strip()

    print("RESULT OF CAPTCHA:")
    print(number)
    print("===================")
    return number

def apply_to_job_posting(full_name, email, phone, current_company, linkedin_profile, cv_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Change 'chromium' to 'firefox' or 'webkit' if preferred
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://jobs.lever.co/spinai/526e677a-8b02-4c30-bcdc-cc3a2a8aca3c/apply")  # Replace 'job-posting-url' with the actual job posting URL

        # navigate to the application page
        page.click('.template-btn-submit')

        # Fill in the form fields
        page.fill('input[name="name"]', full_name)
        page.fill('input[name="email"]', email)
        page.fill('input[name="phone"]', phone)
        page.fill('input[name="org"]', current_company)
        page.fill('input[name="urls[LinkedIn]"]', linkedin_profile)

        # Upload CV file
        page.set_input_files('input[name="resume"]', cv_file)

        page.click('button[type="submit"]')

        # Close the browser
        context.close()
        browser.close()

if __name__ == "__main__":
    full_name = "Leszek Mielnikow"
    email = "leszekmel@gmail.com"
    phone = "+393314244485"
    current_company = "Claira.io"
    linkedin_profile = "https://www.linkedin.com/in/leszek-mielnikow/"
    cv_file = "resume.pdf"  # Make sure your CV file is named correctly and located in the same folder as the script

    apply_to_job_posting(full_name, email, phone, current_company, linkedin_profile, cv_file)
