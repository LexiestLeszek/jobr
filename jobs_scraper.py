from playwright.sync_api import sync_playwright
import time

# fill this in with your job preferences!
PREFERENCES = {
    "position_title": "Product Manager",
    "location": "London, UK"
}

# helper method to give user time to log into glassdoor
def login(page):
    page.goto('https://www.glassdoor.com/index.htm')

    # keep waiting for user to log-in until the URL changes to user page
    while True:
        if "member" in page.url:
            break

    return True # return once this is complete

# navigate to appropriate job listing page
def go_to_listings(page):
    # wait for the search bar to appear
    page.wait_for_selector("//*[@id='scBar']")

    try:
        # look for search bar fields
        position_field = page.query_selector("//*[@id='sc.keyword']")
        location_field = page.query_selector("//*[@id='sc.location']")
        location_field.fill("")
        
        # fill in with pre-defined data
        position_field.fill(PREFERENCES['position_title'])
        location_field.fill(PREFERENCES['location'])

        # wait for a little so location gets set
        time.sleep(1)
        page.click("button[type='submit']")

        # close a random popup if it shows up
        try:
            page.click("//*[@id='JAModal']/div/div[2]/span")
        except:
            pass

        return True

    # note: please ignore all crappy error handling haha
    except:
        return False

# aggregate all url links in a set
def aggregate_links(page):
    allLinks = [] # all hrefs that exist on the page

    # wait for page to fully load
    page.wait_for_selector("//*[@id='MainCol']/div[1]/ul")

    time.sleep(5)

    # parse the page source using beautiful soup
    page_source = page.content()
    soup = BeautifulSoup(page_source)

    # find all hrefs
    allJobLinks = soup.findAll("a", {"class": "jobLink"})
    allLinks = [jobLink['href'] for jobLink in allJobLinks]
    allFixedLinks = []

    # clean up the job links by opening, modifying, and 'unraveling' the URL
    for link in allLinks:
        # first, replace GD_JOB_AD with GD_JOB_VIEW
        # this will replace the Glassdoor hosted job page to the proper job page
        # hosted on most likely Greenhouse or Lever
        link = link.replace("GD_JOB_AD", "GD_JOB_VIEW")

        # if there is no glassdoor prefix, add that
        # for example, /partner/jobListing.htm?pos=121... needs the prefix
        if link[0] == '/':
            link = f"https://www.glassdoor.com{link}"

        # then, open up each url and save the result url
        # because we got a 403 error when opening this normally, we have to establish the user agent
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        request = urllib.request.Request(link, headers=headers)

        try:
            # the url is on glassdoor itself, but once it's opened, it redirects - so let's store that
            response = urllib.request.urlopen(request)
            newLink = response.geturl()

            # if the result url is from glassdoor, it's an 'easy apply' one and worth not saving
            # however, this logic can be changed if you want to keep those
            if "glassdoor" not in newLink:
                print(newLink)
                print('\n')
                allFixedLinks.append(newLink)
        except Exception:
            # horrible way to catch errors but this doesnt happen regularly (just 302 HTTP error)
            print(f'ERROR: failed for {link}')
            print('\n')

    # convert to a set to eliminate duplicates
    return set(allFixedLinks)

# 'main' method to iterate through all pages and aggregate URLs
def getURLs():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        success = login(page)
        if not success:
            # close the page if it gets stuck at some point - this logic can be improved
            page.close()
            context.close()
            browser.close()
            return

        success = go_to_listings(page)
        if not success:
            page.close()
            context.close()
            browser.close()
            return

        allLinks = set()
        page = 1
        next_url = ''
        while page < 5: # pick an arbitrary number of pages so this doesn't run infinitely
            print(f'\nNEXT PAGE #: {page}\n')

            # on the first page, the URL is unique and doesn't have a field for the page number
            if page == 1:
                # aggregate links on first page
                allLinks.update(aggregate_links(page))

                # find next page button and click it
                next_page = page.query_selector("//*[@id='FooterPageNav']/div/ul/li[3]/a")
                this_page = next_page.get_attribute('href')

                # use regex to parse out the page number
                m = re.search('(?P<url>[^;]*?)(?P<page>.htm\?p=)(?P<pagenum>.)', this_page)

                # for page 2 onwards, there's a different page structure that we need to convert from
                # (idk why it's like this tho)
                # from: .../jobs-SRCH_IL.0,13_IC1147401_KE14,33.htm?p=2
                # to: .../jobs-SRCH_IL.0,13_IC1147401_KE14,33_IP2.htm
                page += 1 # increment page count
                next_url = f"{m.group('url')}_IP{page}.htm" # update url with new page number
                time.sleep(1) # just to give things time

            # same patterns from page 2 onwards
            if page >=2 :
                # open page with new URL
                page.goto(next_url)
                # collect all the links
                allLinks.update(aggregate_links(page))
                # run regex to get all reusable parts of URL
                m = re.search('(?P<url>[^;]*?)(?P<pagenum>.)(?P<html>.htm)', next_url)
                # increment page number for next time
                page += 1
                # update URL
                next_url = f"{m.group('url')}{page}.htm"

        page.close()
        context.close()
        browser.close()
        return allLinks

# for testing purpose
getURLs()