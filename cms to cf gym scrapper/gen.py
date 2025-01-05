import csv

# Load the CSV file
def load_csv(file_name):
    data = []
    with open(file_name, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# Transform data to the desired format
def transform_data(data):
    contest_name = "SanSi Cup 2024"
    contest_duration = 240
    task_names = ["A", "B", "C", "D", "E", "F", "G"]

    # Map usernames to IDs
    user_map = {}
    submissions = []

    # Generate user map and submissions
    user_id_counter = 1
    for row in data:
        username = row['username']
        if username not in user_map:
            user_map[username] = user_id_counter
            user_id_counter += 1

        task = row['task']
        relative_time = row['relative_time']  # Convert to integer seconds
        status = "OK" if row['status'] == "Accepted" else "RJ"
        user_id = user_map[username]

        submissions.append(f"@s {user_id},{task},1,{relative_time},{status}")

    # Generate user declarations
    teams = [f"@t {user_id},0,1,{username}" for username, user_id in user_map.items()]

    # Generate header
    header = [
        f"@contest \"{contest_name}\"",
        f"@contlen {contest_duration}",
        f"@problems {len(task_names)}",
        f"@teams {len(user_map)}",
        f"@submissions {len(submissions)}"
    ]

    # Generate problem declarations
    problems = [f"@p {task},{name},20,0" for task, name in zip(task_names, [
        "Alalay", "Back to the Fruit Forest", "Christ of Discord", "World Domination", 
        "El Gift from Ronaldo", "Fiesta in the Mountains", "Global warming"])]

    # Combine all parts
    result = header + problems + teams + submissions
    return "\n".join(result)

# Save transformed data to a file
def save_to_file(output_file, content):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

# Main execution
def main():
    input_csv = "submissions.csv"  # Replace with your CSV file name
    output_file = "contest_data.txt"  # Output file name

    data = load_csv(input_csv)
    transformed_data = transform_data(data)
    save_to_file(output_file, transformed_data)
    print(f"Data successfully transformed and saved to {output_file}")

if __name__ == "__main__":
    main()
