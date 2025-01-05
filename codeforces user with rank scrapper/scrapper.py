import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Function to convert the "format-humantime" string to a datetime object
def parse_humantime(humantime_str):
    return datetime.strptime(humantime_str, "%b/%d/%Y %H:%M")

candidates = []

for page in range(78, 86):
    print("looking for page", page)
    url = 'https://codeforces.com/ratings/page/' + str(page)
    print(url)

    current_time = datetime.now()
    max_last_visit_diff = timedelta(hours=6)
    max_registered_diff = timedelta(days=240)  # Approximately 8 months
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        target_class = "rated-user user-cyan"
        elements = soup.find_all(class_=target_class)

        for element in elements:
            user_url = 'https://codeforces.com' + element.get('href')
            user_response = requests.get(user_url)
            if user_response.status_code == 200:
                user_soup = BeautifulSoup(user_response.text, "html.parser")
                user_elements = user_soup.find_all(class_="format-humantime")
                if len(user_elements) >= 2:
                    # last_visit_time = parse_humantime(user_elements[0]['title'])
                    registered_time = parse_humantime(user_elements[1]['title'])
                    
                    # Calculate time differences
                    # last_visit_diff = current_time - last_visit_time
                    registered_diff = current_time - registered_time

                    # Check if the user satisfies the conditions
                    if registered_diff <= max_registered_diff:
                        friend_icon = user_soup.find("img", src="//codeforces.org/s/62180/images/icons/star_yellow_24.png")
                        if friend_icon:
                            friend_count_element = friend_icon.find_parent()
                            friend_count_text = friend_count_element.text
                            friend_count = int(friend_count_text.split(":")[1].strip().split()[0])
                            if friend_count < 5:
                                candidates.append(element.text)
                                print(element.text)
                else:
                    registered_time = parse_humantime(user_elements[0]['title'])
                    # print(last_visit_time, registered_time)
                    
                    # Calculate time differences
                    registered_diff = current_time - registered_time

                    # Check if the user satisfies the conditions
                    if registered_diff <= max_registered_diff:
                        friend_icon = user_soup.find("img", src="//codeforces.org/s/62180/images/icons/star_yellow_24.png")
                        if friend_icon:
                            friend_count_element = friend_icon.find_parent()
                            friend_count_text = friend_count_element.text
                            friend_count = int(friend_count_text.split(":")[1].strip().split()[0])
                            if friend_count < 5:
                                candidates.append(element.text)
                                print(element.text)
            else:
                print(f"User request failed with status code: {user_response.status_code}")
    else:
        print(f"Request failed with status code: {response.status_code}")

# write candidates to file for later use
with open('candidates.txt', 'w') as f:
    for item in candidates:
        f.write("%s\n" % item)
