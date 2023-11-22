import csv


def read_course_data(file_path):
    """
    Reads course data from a CSV file and returns it as a list of dictionaries.
    """
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def filter_classes_by_course_number(course_data, course_number):
    """
    Filters classes based on the course number and returns open and closed classes.
    """
    open_classes = []
    closed_classes = []
    for row in course_data:
        course_name = row["Course Name"]
        extracted_course_number = course_name.split()[
            1
        ]  # Assuming format "CSCI 101 - Course Title"

        if extracted_course_number == course_number:
            if row["Status"].strip().lower() == "open":
                open_classes.append(row)
            elif row["Status"].strip().lower() == "closed":
                closed_classes.append(row)
    return open_classes, closed_classes


def main():
    course_number_input = input("Enter the CSCI course number to check: ")
    csv_file_path = "JJ_CS-Courses.csv"

    try:
        course_data = read_course_data(csv_file_path)
        open_classes, closed_classes = filter_classes_by_course_number(
            course_data, course_number_input
        )

        print(f"Open classes for CSCI {course_number_input}:")
        for cls in open_classes:
            print(f"  Class: {cls['Class']}, Section: {cls['Section']}")

        print(f"\nClosed classes for CSCI {course_number_input}:")
        for cls in closed_classes:
            print(f"  Class: {cls['Class']}, Section: {cls['Section']}")
    except FileNotFoundError:
        print("Error: The specified CSV file could not be found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
