
# Google search for jobs
from googlesearch import search

# fill this in with your job preferences!
PREFERENCES = {
    "position_title": "Product Manager",
    "location": "Europe, UK"
}

# 'main' method to iterate through search results and extract lever.co URLs
def getURLs():
    query = f"{PREFERENCES['position_title']} job postings site:lever.co"
    allLinks = []

    for url in search(query, num_results=10):
        if "lever.co" in url:
            allLinks.append(url)

    return allLinks

# for testing purpose
lever_urls = getURLs()
print(lever_urls, sep="\n")
