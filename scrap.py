from playwright.sync_api import Playwright, sync_playwright, expect
import csv
import datetime
import os


def make_abbreviation(name):
    # Split the name into words
    words = name.split()

    # Take the first letter of each word and combine them
    abbreviation = "".join(word[0].upper() for word in words)

    return abbreviation


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    # -----PAGE 1
    print("page 1")
    page.goto("https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp")
    # ===========================================================================
    # Query all label elements within the ul.checkboxes list
    college_checkboxes = page.query_selector_all("ul.checkboxes input[type='checkbox']")
    # Extract the text content of each associated label to get the college names
    colleges = []
    for checkbox in college_checkboxes:
        # Get the id of the checkbox
        checkbox_id = checkbox.get_attribute("id")
        # Find the label associated with this checkbox
        label = page.query_selector(f"label[for='{checkbox_id}']")
        if label:
            colleges.append(label.text_content().strip())

    # Display the colleges to the user
    for index, college in enumerate(colleges, start=1):
        print(f"{index}. {college}")

    # Ask the user to choose a college
    selected_index = int(input("Select a college by entering its number: ")) - 1
    selected_college = colleges[selected_index]
    school_name = make_abbreviation(selected_college)

    # Find and click the corresponding checkbox
    checkbox = page.get_by_text(selected_college)
    if checkbox:
        checkbox.click()
    else:
        print("Selected college not found.")
    # ===========================================================================
    # Query the select element for terms
    term_select = page.query_selector("select[name='term_value']")

    # Extract the available terms and their values
    terms = []
    for option in term_select.query_selector_all("option"):
        term_value = option.get_attribute("value")
        term_text = option.text_content().strip()
        if term_value:  # Exclude the empty option
            terms.append((term_text, term_value))

    # Display the terms to the user
    for index, (term_text, _) in enumerate(terms, start=1):
        print(f"{index}. {term_text}")

    # Ask the user to choose a term
    selected_index = int(input("Select a term by entering its number: ")) - 1
    selected_term_value = terms[selected_index][1]

    # Select the chosen term
    term_select.select_option(selected_term_value)
    # ===========================================================================
    page.get_by_role("button", name="Next").click()

    # -----PAGE 2
    print("page 2")
    # Locate the select element for subjects
    subject_select = page.query_selector("#subject_ld")

    # Extract the available subjects and their values
    subjects = []
    for option in subject_select.query_selector_all("option"):
        subject_value = option.get_attribute("value")
        subject_text = option.text_content().strip()
        if subject_value:  # Excluding the empty option
            subjects.append((subject_text, subject_value))

    # Check if there are no subjects available
    if not subjects:
        print("There are no subjects available yet.")
        # Exit the Playwright script
        # (Assuming you're using a function or similar structure)
        return

    # Display the subjects to the user
    for index, (subject_text, _) in enumerate(subjects, start=1):
        print(f"{index}. {subject_text}")

    # Ask the user to choose a subject
    selected_index = int(input("Select a subject by entering its number: ")) - 1
    selected_subject_value = subjects[selected_index][1]
    subject = subjects[selected_index][1]

    # Select the chosen subject
    subject_select.select_option(selected_subject_value)

    # Locate the select element for course careers
    course_career_select = page.query_selector("#courseCareerId")

    # Extract the available course careers and their values
    course_careers = []
    for option in course_career_select.query_selector_all("option"):
        career_value = option.get_attribute("value")
        career_text = option.text_content().strip()
        if career_value:  # Excluding the empty option
            course_careers.append((career_text, career_value))

    # Check if there are no course careers available
    if not course_careers:
        print("There are no course careers available yet.")
        # Exit the Playwright script
        # (Assuming you're using a function or similar structure)
        return

    # Display the course careers to the user
    for index, (career_text, _) in enumerate(course_careers, start=1):
        print(f"{index}. {career_text}")

    # Ask the user to choose a course career
    selected_index = int(input("Select a course career by entering its number: ")) - 1
    selected_career_value = course_careers[selected_index][1]

    # Select the chosen course career
    course_career_select.select_option(selected_career_value)

    page.get_by_role("button", name="Search").click()
    # -----PAGE 3
    print("page 3")
    page.get_by_label("Class Section", exact=True).click()
    # page.get_by_text("CSCI 274 - Computer Architecture").click()
    # page.locator("#imageDivLink7").click()

    # Query all the div elements with the class "testing_msg"
    course_name_elements = page.query_selector_all(".testing_msg")
    # Extract course full names
    course_full_names = []
    for element in course_name_elements:
        # Extract the text content from the span element inside the div
        course_full_name = (
            element.query_selector("span")
            .get_property("innerText")
            .json_value()
            .strip()
        )
        # Append the course full name to the list
        course_full_names.append(course_full_name)

    courses_table = page.query_selector_all(".classinfo")
    # Combined data structure
    combined_courses = []

    # Iterate over both course names and tables
    for course_name, table in zip(course_full_names[2:], courses_table):
        # Extract classes for each course
        classes = []
        class_bodies = table.query_selector_all("tbody")
        for tbody in class_bodies:
            class_row = tbody.query_selector("tr")
            if class_row:
                cells = class_row.query_selector_all("td")
                status_img = cells[7].query_selector("img")
                status = status_img.get_attribute("title") if status_img else "Unknown"
                class_info = {
                    "class": cells[0].text_content().strip(),
                    "section": cells[1].text_content().strip(),
                    "days_times": cells[2].text_content().strip(),
                    "room": cells[3].text_content().strip(),
                    "instructor": cells[4].text_content().strip(),
                    "instruction_mode": cells[5].text_content().strip(),
                    "meeting_dates": cells[6].text_content().strip(),
                    "status": status,
                }
                classes.append(class_info)

        # Combine course name with its classes
        course_data = {"course_name": course_name, "classes": classes}
        combined_courses.append(course_data)

    # Get the current date in YYYYMMDD format
    current_date = datetime.datetime.now().strftime("%Y%m%d")

    folder_path = "collegeCourseData"
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Create the file name
    file_name = f"{folder_path}/{school_name}_{subject}-{current_date}.csv"
    # Create a CSV file
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(
            [
                "Course Name",
                "Class",
                "Section",
                "Days & Times",
                "Room",
                "Instructor",
                "Instruction Mode",
                "Meeting Dates",
                "Status",
            ]
        )

        # Write course data
        for course in combined_courses:
            for class_info in course["classes"]:
                writer.writerow(
                    [
                        course["course_name"],
                        class_info["class"],
                        class_info["section"],
                        class_info["days_times"],
                        class_info["room"],
                        class_info["instructor"],
                        class_info["instruction_mode"],
                        class_info["meeting_dates"],
                        class_info["status"],
                    ]
                )

    # # Query all the div elements with the class "testing_msg"
    # course_name_elements = page.query_selector_all(".testing_msg")
    # # Extract course full names
    # course_full_names = []
    # for element in course_name_elements:
    #     # Extract the text content from the span element inside the div
    #     course_full_name = (
    #         element.query_selector("span")
    #         .get_property("innerText")
    #         .json_value()
    #         .strip()
    #     )
    #     # Append the course full name to the list
    #     course_full_names.append(course_full_name)

    # # Print the list of course names
    # for name in course_full_names[2:]:
    #     print(name)

    # # Select the table containing the course information
    # # Replace .classinfo with the actual class or ID of your table
    # courses_table = page.query_selector_all(".classinfo")

    # # Extract course information
    # courses = []
    # for table in courses_table:  # Skipping the header row
    #     # Now, for each table, select all tbody elements, each representing a class
    #     class_bodies = table.query_selector_all("tbody")

    #     for tbody in class_bodies:
    #         # Extract each class information from tbody
    #         class_row = tbody.query_selector(
    #             "tr"
    #         )  # each tbody has one tr for class details
    #         if class_row:
    #             cells = class_row.query_selector_all("td")

    #             # Extract the title attribute from the img tag in the Status cell
    #             status_img = cells[7].query_selector("img")
    #             status = status_img.get_attribute("title") if status_img else "Unknown"

    #             course_info = {
    #                 "course_topic": cells[8].text_content().strip(),
    #                 "class": cells[0].text_content().strip(),
    #                 "section": cells[1].text_content().strip(),
    #                 "days_times": cells[2].text_content().strip(),
    #                 "room": cells[3].text_content().strip(),
    #                 "instructor": cells[4].text_content().strip(),
    #                 "instruction_mode": cells[5].text_content().strip(),
    #                 "meeting_dates": cells[6].text_content().strip(),
    #                 "status": status,
    #             }
    #         courses.append(course_info)

    # with open("JJ_MajorCourseInfo.txt", "w") as file:
    #     # Do something with the extracted data
    #     for course in courses:
    #         courseinfo = (
    #             course["course_topic"]
    #             + "|"
    #             + course["class"]
    #             + "|"
    #             + course["status"]
    #             + "\n"
    #         )
    #         print(courseinfo)
    #         file.write(courseinfo)

    # page.wait_for_timeout(10000)

    # pageContent = page.content()
    # with open("JJ_HTMLMajor.txt", "w") as file:
    #     file.write(pageContent)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
