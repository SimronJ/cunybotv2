from playwright.sync_api import Playwright, sync_playwright, expect
import csv
import datetime
import os


def make_abbreviation(name):
    return "".join(word[0].upper() for word in name.split())


def select_from_options(prompt_message, options):
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option[0]}")
    selected_index = int(input(prompt_message)) - 1
    return options[selected_index][1]


def extract_options(select_element):
    return [
        (option.text_content().strip(), option.get_attribute("value"))
        for option in select_element.query_selector_all("option")
        if option.get_attribute("value")
    ]


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp")

    # Select College
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

    # Select Term
    term_select = page.query_selector("select[name='term_value']")
    terms = extract_options(term_select)
    selected_term = select_from_options("Select a term by entering its number: ", terms)
    term_select.select_option(selected_term)

    page.get_by_role("button", name="Next").click()

    # Select Subject
    subject_select = page.query_selector("#subject_ld")
    subjects = extract_options(subject_select)
    if not subjects:
        print("There are no subjects available yet.")
        return
    selected_subject = select_from_options(
        "Select a subject by entering its number: ", subjects
    )
    subject_select.select_option(selected_subject)

    # Select Course Career
    course_career_select = page.query_selector("#courseCareerId")
    course_careers = extract_options(course_career_select)
    if not course_careers:
        print("There are no course careers available yet.")
        return
    selected_career = select_from_options(
        "Select a course career by entering its number: ", course_careers
    )
    course_career_select.select_option(selected_career)

    page.get_by_role("button", name="Search").click()

    # Extract course data
    courses = extract_course_data(page)
    save_course_data_to_csv(courses, school_name, selected_subject)

    context.close()
    browser.close()


def extract_course_data(page):
    course_name_elements = page.query_selector_all(".testing_msg")
    courses_table = page.query_selector_all(".classinfo")
    combined_courses = []

    for course_name_element, table in zip(course_name_elements, courses_table):
        course_name = course_name_element.query_selector("span").text_content().strip()
        classes = extract_classes(table)
        combined_courses.append({"course_name": course_name, "classes": classes})
    return combined_courses


def extract_classes(table):
    classes = []
    for tbody in table.query_selector_all("tbody"):
        class_row = tbody.query_selector("tr")
        if class_row:
            cells = class_row.query_selector_all("td")
            status_img = cells[7].query_selector("img")
            status = status_img.get_attribute("title") if status_img else "Unknown"
            classes.append(
                {
                    cell.get_attribute("data-label"): cell.text_content().strip()
                    for cell in cells
                }
            )
            classes[-1]["status"] = status
    return classes


def save_course_data_to_csv(courses, school_name, subject):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    folder_path = "collegeCourseData"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_name = f"{folder_path}/{school_name}_{subject}-{current_date}.csv"

    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
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
        for course in courses:
            for class_info in course["classes"]:
                writer.writerow(
                    [course["course_name"]]
                    + [
                        class_info.get(column, "")
                        for column in [
                            "Class",
                            "Section",
                            "Days & Times",
                            "Room",
                            "Instructor",
                            "Instruction Mode",
                            "Meeting Dates",
                            "Status",
                        ]
                    ]
                )


with sync_playwright() as playwright:
    run(playwright)
