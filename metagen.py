import sqlite3
import json
import os
from juvo.auto_build import auto_build
from juvo.run_orchestra_auto import run_orchestra_auto

def chatbot_response(user_input):
    """Generate a response based on user input."""
    responses = {
        "hello": "Hi there! How can I help you today?",
        "how are you": "I'm just a program, but I'm doing great! How about you?",
        "bye": "Goodbye! Have a great day!",
        "help": "Sure, let me know what you need help with!",
        "what are the options": "You can 'list' orchestras, 'describe <name>' an orchestra, 'run <name>' an orchestra, or 'build' a new one.",
        "options": "You can 'list' orchestras, 'describe <name>' an orchestra, 'run <name>' an orchestra, or 'build' a new one."
    }

    # Normalize input
    user_input = user_input.lower()
    # Return predefined response or a default one
    return responses.get(user_input, "I'm sorry, I don't understand that. Can you rephrase?")

def initialize_database():
    """Ensures the SQLite database is initialized with orchestra data."""
    conn = sqlite3.connect("orchestra.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orchestras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            date TEXT,
            json_data TEXT
        )
    """)

    # Insert sample data if the table is empty
    cursor.execute("SELECT COUNT(*) FROM orchestras")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Symphony of Stars", "An orchestra that performs celestial-themed music.", "2024-01-15", json.dumps({"type": "celestial", "theme": "stars"})),
            ("Harmonic Horizons", "A group focused on blending classical and modern styles.", "2024-02-20", json.dumps({"type": "blend", "theme": "horizons"})),
            ("Melody Makers", "A family-friendly orchestra with lighthearted performances.", "2024-03-10", json.dumps({"type": "family", "theme": "melody"}))
        ]
        cursor.executemany("INSERT INTO orchestras (name, description, date, json_data) VALUES (?, ?, ?, ?)", sample_data)

    conn.commit()
    conn.close()

def get_orchestra_list():
    """Fetches the list of orchestras from SQLite."""
    conn = sqlite3.connect("orchestra.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, description, date, json_data FROM orchestras")
    rows = cursor.fetchall()
    orchestras = []
    for row in rows:
        orchestras.append({
            "name": row[0],
            "description": row[1],
            "date": row[2],
            "json_data": json.loads(row[3])
        })

    conn.close()
    return orchestras

def run_orchestra(name, description, llm_config, config_list, config_file_or_env):
    """Fetches and prepares to run an orchestra by name and description."""
    conn = sqlite3.connect("orchestra.db")
    cursor = conn.cursor()

    cursor.execute("SELECT json_data FROM orchestras WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        build_json = json.loads(row[0])
        build_json_file = os.path.join(os.getcwd(), f"{name.replace(' ', '_')}_config.json")

        # Write JSON to a file
        with open(build_json_file, "w") as json_file:
            json.dump(build_json, json_file, indent=2)

        print(f"Chatbot: JSON configuration for '{name}' saved to '{build_json_file}'.")

        # Call auto_build and run_orchestra_auto
        run_orchestra_auto(name, description, llm_config, config_list, config_file_or_env, build_json_file)
    else:
        print(f"No orchestra found with the name '{name}'.")

    conn.close()

def describe_orchestra(name):
    """Describes an orchestra by name."""
    conn = sqlite3.connect("orchestra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, date, json_data FROM orchestras WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        print(f"Details for Orchestra: {row[0]}")
        print(f"Description: {row[1]}")
        print(f"Date: {row[2]}")
        print(f"Additional Data: {json.dumps(json.loads(row[3]), indent=2)}")
    else:
        print(f"No orchestra found with the name '{name}'.")

    conn.close()

def list_orchestras():
    """Lists all available orchestras."""
    orchestra_db = get_orchestra_list()
    if orchestra_db:
        print("Available Orchestras:")
        for orchestra in orchestra_db:
            print(f"- {orchestra['name']}")
    else:
        print("No orchestras are currently available.")

def build_orchestra(name, description, llm_config, save_json_path):
    """Builds an orchestra and generates a configuration JSON file."""
    # Example JSON file creation
    build_json = {
        "name": name,
        "description": description,
        "type": "custom",
        "theme": "dynamic"
    }
    build_json_file = os.path.join(save_json_path, f"save_config_{name.replace(' ', '_')}.json")

    try:
        auto_build(name, description, llm_config, save_json_path)
        os.makedirs(save_json_path, exist_ok=True)
        with open(build_json_file, "w") as json_file:
            json.dump(build_json, json_file, indent=2)
        print(f"Chatbot: Configuration file for '{name}' saved at '{build_json_file}'.")
        return build_json_file
    except Exception as e:
        print(f"Chatbot: Failed to create configuration file. Error: {e}")
        return None

def main():
    """Main function to run the chatbot."""
    print("Welcome to CLI Chat! Type 'exit' to quit.")
    print("You can either list orchestras with 'list', describe one with 'describe <name>', run one by asking 'run <name>', or build a new one.")

    OAI_CONFIG_LIST = [
        {
            'model': 'gpt-4o',
            'api_key': 'api_key',
        },
    ]
    os.environ['OAI_CONFIG_LIST'] = json.dumps(OAI_CONFIG_LIST)

    config_list = [
        {
            'model': 'gpt-4o-mini',
            'api_key': 'api_key',
        },
        {
            'model': 'gpt-3.5-turbo',
            'api_key': 'api_key',
        },
        {
            'model': 'gpt-3.5-turbo-16k',
            'api_key': 'api_key',
        },
    ]
    llm_config = {"temperature": 0, "config_list": config_list}

    initialize_database()

    while True:
        # Get user input
        user_input = input("You: ").strip()

        # Exit condition
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye! Take care.")
            break

        # Handle list requests
        if user_input.lower() == "list":
            list_orchestras()
            continue

        # Handle describe requests
        if user_input.lower().startswith("describe "):
            _, name_to_describe = user_input.split("describe ", 1)
            name_to_describe = name_to_describe.strip()
            describe_orchestra(name_to_describe)
            continue

        # Handle run requests
        if user_input.lower().startswith("run "):
            _, name_to_run = user_input.split("run ", 1)
            name_to_run = name_to_run.strip()

            conn = sqlite3.connect("orchestra.db")
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM orchestras WHERE name = ?", (name_to_run,))
            row = cursor.fetchone()

            if row:
                description = row[0]
                run_orchestra(name_to_run, description, llm_config, config_list, "OAI_CONFIG_LIST")
            else:
                print(f"No orchestra found with the name '{name_to_run}'.")

            conn.close()
            continue

        # Handle build requests
        if user_input.lower() == "build":
            name_to_build = input("Enter the name of the orchestra to build: ").strip()
            description = input("Enter a description for the orchestra: ").strip()
            save_json_path = './log'

            build_json_file = build_orchestra(name_to_build, description, llm_config, save_json_path)

            if build_json_file and os.path.exists(build_json_file):
                # Save to database
                conn = sqlite3.connect("orchestra.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orchestras (name, description, date, json_data) VALUES (?, ?, DATE('now'), ?)",
                               (name_to_build, description, json.dumps({"file": build_json_file})))
                conn.commit()
                conn.close()
                print(f"Chatbot: Orchestra '{name_to_build}' built successfully and saved to the database.")
            else:
                print("Chatbot: Configuration file was not created successfully.")
            continue

        # Generate and display chatbot response
        response = chatbot_response(user_input)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    main()

