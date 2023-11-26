import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def save_preferences(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    logging.info(f"User preference file has been saved: {file_path}")


def load_preferences(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            preferences = json.load(file)

        # Display current saved preferences
        logging.info("Current saved preferences:")
        for key, value in preferences.items():
            print(f"{key}: {value}")

        # Ask user to continue with these preferences or not
        choice = (
            input("Do you want to continue with these preferences? (Y/n): ")
            .strip()
            .lower()
        )
        if choice != "y":
            return None  # Return None if user chooses not to continue with current preferences

        return preferences

    except FileNotFoundError:
        logging.info("No saved preferences found.")
        return None


def save_data(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def load_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None


# # Save new preferences
# new_preferences = {
#     "college_index": selected_index,
#     "term_index": term_index,
#     "subject_index": subject_index,
#     "career_index": career_index,
# }
# preferencesFileName = f"{"user"}_{selected_collegeCode}_{term_selected}_{subjectName}_{whichCareer}.json"
