import csv
import json
import requests
from bs4 import BeautifulSoup

duplicates = [
    ('university/Universidad%20Mayor%20de%20San%20Simon%20-%20Sistemas', 'Universidad Mayor de San Simon - Sistemas')
    ('university/Pontificia%20Universidad%20Cat%C3%B3lica%20del%20Per%C3%BA', 'Pontificia Universidad Católica del Perú')
]

# get countries from countries.txt
def get_countries():
    countries = []
    with open('countries.txt') as f:
        for line in f:
            countries.append(line.strip())
    return countries

# Base URL for the Competitive Programmers Hall of Fame
base_url = 'https://www.cphof.org/'

def get_universities_from_country(country):
    # Construct URL for a specific country's page on the Hall of Fame
    country_url = base_url + 'countrydata/' + country
    
    # Fetch the content of the country page
    response = requests.get(country_url)
    data = response.json()
    # Extract university names and their participation info
    universities = set()
    for participant in data:
        if json.loads(participant['icpc'])[3]:
            participant_href = participant['name'].split('\"')[1][1:]
            profile_url = base_url + participant_href

            html_content = requests.get(profile_url).text
            soup = BeautifulSoup(html_content, 'html.parser')

            university_links = soup.find_all('a', href=lambda href: href and href.startswith("/university"))
            university_tuples = [(link.get('href')[1:], link.text)  for link in university_links]

            universities.update(university_tuples)

    for duplicate in duplicates:
        if duplicate in universities:
            universities.remove(duplicate)
    return list(universities)

def get_teams_by_university(university_url, university_name, country):
    # Construct URL for a specific university's page on the Hall of Fame
    university_url = base_url + university_url
    
    # Fetch the content of the university page
    response = requests.get(university_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    
    country_links = soup.find_all('a', href=lambda href: href and href.startswith("/country"))
    print(country_links)
    if(country_links[0].get('href') != '/country/' + country):
        return 0
    print('pass')

    tbody = soup.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        number_of_rows = len(rows)
    else:
        number_of_rows = 0
    print(university_name, number_of_rows)
    print(university_url)
    return number_of_rows

# Main process
country_participations = {}

countries_of_interest = get_countries()
with open('university_participations.csv', mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    
    # Write the header row
    csv_writer.writerow(['Country', 'University Name', 'University URL', 'Number of Teams'])

    countries_of_interest = get_countries()
    for country in countries_of_interest:
        print('#' * 20)
        print(country)
        print('#' * 20)

        universities = get_universities_from_country(country)
        total_teams = 0
        for university in universities:

            teams = get_teams_by_university(university[0], university[1], country)
            total_teams += teams
            
            # Write each university's data to the CSV file
            csv_writer.writerow([country, university[1], base_url + university[0], teams])
        
        country_participations[country] = total_teams

    # Optionally, you can write the total teams per country at the end of the file
    csv_writer.writerow([])
    csv_writer.writerow(['Country', 'Total Teams'])
    for country, teams in country_participations.items():
        csv_writer.writerow([country, teams])