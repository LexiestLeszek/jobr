# Run goo.py to find and save jobs to a txt file
# run job.py to apply for each job url form the file

from playwright.sync_api import sync_playwright
import time

def job_lever(full_name, email, phone, current_company, linkedin_profile, cv_file, url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Change 'chromium' to 'firefox' or 'webkit' if preferred
        context = browser.new_context()

        page = context.new_page()
        page.goto(url)

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
    
    with open('urls.txt', 'r') as file:
        urls = file.read().splitlines()
    
    for url in urls:
        job_lever(full_name, email, phone, current_company, linkedin_profile, cv_file, url)
