import requests
from bs4 import BeautifulSoup

# Define URLs
base_url = "http://eval.ohsansi.umss.edu.bo"
login_url = f"{base_url}/bigbrother/login?next=%2F"
target_url = f"{base_url}/bigbrother"  # Adjust this to the desired page after login

# Start a session
session = requests.Session()

# Step 1: Get the login page to fetch the CSRF token
login_page = session.get(login_url)
soup = BeautifulSoup(login_page.text, 'html.parser')

# Extract the CSRF token
csrf_token = soup.find('input', {'name': '_xsrf'})['value']

print(csrf_token)

# Step 2: Prepare the login payload
payload = {
    'username': 'admin',  # Replace with your actual username
    'password': 'c5sansimmhwg.',  # Replace with your actual password
    '_xsrf': csrf_token,
    'next': '/'  # Provided in the form as a hidden input
}

# Step 3: Send the login POST request
response = session.post(login_url, data=payload)

# Check if login was successful
if response.status_code == 200:
    print("Login successful!")
else:
    print("Login failed. Check credentials or CSRF handling.")


# Base URL
base_url = "http://eval.ohsansi.umss.edu.bo/bigbrother/submission/"

# Define range of IDs
begin = 602  # Starting ID
end = 2094    # Ending ID

# Global variables
contest_start_time = "2024-12-21 18:13:00.000000"  # Replace with the actual start time of the contest

task_mapping = {
    'abbreviations': 'D',
	'globalwarming': 'G',
	'laguna':	'A',
	'montanas':	'F',
	'sigma':	'C',
	'tunari':	'B',
	'el_regalo_del_ronaldo':	'E'
}

from datetime import datetime

# Function to traverse and scrape pages
def scrape_submissions(start, stop):
    results = []  # To store the extracted data

    # Convert contest start time to a datetime object
    contest_start_dt = datetime.strptime(contest_start_time, "%Y-%m-%d %H:%M:%S.%f")

    for submission_id in range(start, stop + 1):
        url = f"{base_url}{submission_id}"
        print(f"Accessing {url}...")

        # Request the page
        response = session.get(url)

        # Check if page is valid (status code 200)
        if response.status_code == 200:
            print(f"Processing submission ID {submission_id}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract submission time
            submission_time_text = soup.find('td', string="Submission time").find_next('td').text.strip()
            submission_time_dt = datetime.strptime(submission_time_text, "%Y-%m-%d %H:%M:%S.%f")

            # Calculate relative time in seconds
            relative_time = (submission_time_dt - contest_start_dt).total_seconds()
            relative_time = int(relative_time * 14400/16500)

            # Extract username
            username = soup.find('td', string="User").find_next('td').text.strip()
            
            task = task_mapping[soup.find('td', string="Task").find_next('td').text.strip()]
    
            judge_status = soup.find('td', string="Status").find_next('td').text.strip()

            status = "Rejected"
            if "Scored" in judge_status:
                # Extract score from the Status field (e.g., "Scored (100.0 / 100.0)")
                score = float(judge_status.split('(')[1].split('/')[0].strip())
                status = "Accepted" if score == 100 else "Rejected"

            # Store the extracted information
            results.append({
                'task': task,
                'relative_time': relative_time,
                'username': username,
                'status': status,
            })
        else:
            print(f"Submission ID {submission_id} not found (status code {response.status_code}).")

    return results



# Call the function and define your range
data = scrape_submissions(begin, end)

# Print the results
for entry in data:
    print(entry)

# Optional: Save the data to a CSV file
import csv
with open('submissions.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['task', 'relative_time', 'username', 'status'])
    writer.writeheader()
    writer.writerows(data)

print("Data saved to submissions.csv")
