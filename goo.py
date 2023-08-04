from googlesearch import search

# fill this in with your job preferences!
PREFERENCES = {
    "position_title": "Product Manager",
    "location": "Europe, UK"
}

# 'main' method to iterate through search results and extract lever.co URLs
def getURLs():
    query = f"{PREFERENCES['position_title']} remote site:lever.co"
    allLinks = []

    for url in search(query, num_results=1000):
        if "lever.co" in url:
            allLinks.append(url)

    return allLinks

# Function to save URLs to a text file
def save_to_txt(urls, filename):
    with open(filename, "w") as file:
        for url in urls:
            file.write(url + "\n")

# for testing purpose
lever_urls = getURLs()
save_to_txt(lever_urls, "urls.txt")
