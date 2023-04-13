import requests
from bs4 import BeautifulSoup

# Step 1: Retrieve webpage content
url = "https://downsub.com/?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DRzakMIZJ0YI"
response = requests.get(url)
html_content = response.text
print(html_content)

# Step 2: Parse the webpage
soup = BeautifulSoup(html_content, "html.parser")
download_link = soup.find_all('p')
print(download_link)

# Step 3: Download the subtitles
# subtitles_response = requests.get(download_link)
# with open("subtitles.srt", "wb") as subtitles_file:
#     subtitles_file.write(subtitles_response.content)
#
