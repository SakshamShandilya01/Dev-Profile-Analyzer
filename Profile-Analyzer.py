# Developer Profile Analyzer
# my first python project - v2, fixed the bugs I found (input crashes, empty
# skill entries counting as "proven", file not closing properly on error)

import json


# ---------- safe input helpers ----------
# these just keep asking until the user gives something valid,
# instead of crashing the whole program on one bad keystroke

def safe_int_input(prompt, min_value=0):
    while True:
        raw = input(prompt)
        try:
            value = int(raw)
            if value < min_value:
                print("please enter a number >=", min_value)
                continue
            return value
        except ValueError:
            print("that's not a valid whole number, try again")


def safe_float_input(prompt, min_value=0.0, max_value=10.0):
    while True:
        raw = input(prompt)
        try:
            value = float(raw)
            if value < min_value or value > max_value:
                print("please enter a number between", min_value, "and", max_value)
                continue
            return value
        except ValueError:
            print("that's not a valid number, try again")


def split_and_clean(raw_text):
    # splits on comma, strips whitespace, and drops empty entries
    # (this fixes the bug where "Python, C++, " left a '' in the list,
    # and '' matches inside every string so it looked "proven")
    parts = raw_text.split(",")
    cleaned = []
    for p in parts:
        p = p.strip()
        if p != "":
            cleaned.append(p)
    return cleaned


def yes_no(prompt):
    ch = input(prompt).strip().lower()
    return ch in ("yes", "y")


# ---------- core logic (same as before, untouched) ----------

def find_unproven_skills(skills, projects):
    unproven = []
    for skill in skills:
        used = False
        for p in projects:
            desc = p['description'].lower()
            tech = ""
            for t in p['tech_used']:
                tech = tech + t.lower() + " "
            if skill.lower() in desc or skill.lower() in tech:
                used = True
        if used == False:
            unproven.append(skill)
    return unproven


def find_undeployed(projects):
    undeployed = []
    for p in projects:
        if p['deployed'] == False:
            undeployed.append(p['name'])
    return undeployed


def calculate_score(skills, projects, leetcode, cgpa, github_repos):
    score = 0
    unproven = find_unproven_skills(skills, projects)
    proven_count = len(skills) - len(unproven)

    skill_points = proven_count * 10
    if skill_points > 30:
        skill_points = 30
    score = score + skill_points

    project_points = len(projects) * 12
    if project_points > 36:
        project_points = 36
    score = score + project_points

    deployed_count = 0
    for p in projects:
        if p['deployed'] == True:
            deployed_count = deployed_count + 1
    deploy_points = deployed_count * 3
    if deploy_points > 9:
        deploy_points = 9
    score = score + deploy_points

    if leetcode >= 200:
        score = score + 15
    elif leetcode >= 100:
        score = score + 10
    elif leetcode >= 50:
        score = score + 6
    elif leetcode >= 20:
        score = score + 3

    if cgpa >= 8.5:
        score = score + 5
    elif cgpa >= 7.5:
        score = score + 3
    elif cgpa >= 6.5:
        score = score + 1

    if github_repos >= 5:
        score = score + 5
    elif github_repos >= 3:
        score = score + 3
    elif github_repos >= 1:
        score = score + 1

    if score > 100:
        score = 100
    return score


def get_label(score):
    if score >= 80:
        return "STRONG - you can apply now"
    elif score >= 60:
        return "DECENT - apply to startups"
    elif score >= 40:
        return "WEAK - fix the gaps first"
    else:
        return "CRITICAL - dont apply yet, build more stuff"


def generate_roast(skills, projects, leetcode, headline):
    issues = []
    unproven = find_unproven_skills(skills, projects)

    if len(unproven) > 0:
        s = ""
        for sk in unproven:
            s = s + sk + ", "
        issues.append("You wrote these skills but no project uses them: " + s + "remove them or make a project with them")

    if leetcode == 0:
        issues.append("You have 0 leetcode solved. Every interview has a coding round, start practicing")
    elif leetcode < 30:
        issues.append("Only " + str(leetcode) + " leetcode done, try to do atleast 50 easy before applying")
    elif leetcode < 100:
        issues.append(str(leetcode) + " leetcode is okay but not enough, try to reach 100")

    if len(projects) == 0:
        issues.append("You have no projects. build atleast one project this week")
    elif len(projects) == 1:
        issues.append("only 1 project, try to make 2 more so recruiter sees more range")

    undeployed = find_undeployed(projects)
    if len(undeployed) > 0:
        names = ""
        for n in undeployed:
            names = names + n + ", "
        issues.append("These projects are not deployed: " + names + "deploy on vercel its free and fast")

    weak_words = ['interested in', 'passionate about', 'learning', 'student of']
    headline_lower = headline.lower()
    found_weak = False
    for w in weak_words:
        if w in headline_lower:
            found_weak = True
    if found_weak:
        issues.append("Your headline sounds generic, say what you build not what you like")

    if len(issues) == 0:
        issues.append("no major issues found, keep improving")

    return issues


def suggest_fixes(skills, projects, leetcode):
    fixes = []
    unproven = find_unproven_skills(skills, projects)
    for sk in unproven:
        fixes.append("For skill " + sk + " : build a small project with it or remove from resume")

    if leetcode < 50:
        fixes.append("Do 2 easy leetcode everyday, start with Two Sum and Valid Palindrome")

    if len(projects) < 2:
        fixes.append("Build one more project, maybe a cli tool or a small tracker app")

    undeployed = find_undeployed(projects)
    if len(undeployed) > 0:
        fixes.append("Deploy your projects on vercel, it only takes like 10 min")

    return fixes


def rewrite_headline(skills, projects):
    if len(skills) > 0:
        top = skills[0]
        if len(skills) > 1:
            top = top + " , " + skills[1]
        if len(skills) > 2:
            top = top + " , " + skills[2]
    else:
        top = "Python, Web Dev"

    if len(projects) > 0:
        building = "Building " + projects[0]['name']
    else:
        building = "Building real projects"

    new_headline = "2nd Year CSE student | " + top + " | " + building + " | Open to internships"
    return new_headline


def make_plan(skills, projects, leetcode):
    plan = {}
    unproven = find_unproven_skills(skills, projects)

    week1 = []
    if leetcode < 20:
        week1.append("solve 2 easy leetcode everyday")
    if len(projects) < 1:
        week1.append("start a project today, anything is fine")
    if len(unproven) > 0:
        week1.append("remove " + unproven[0] + " from resume or build something with it")
    if len(week1) == 0:
        week1.append("polish your existing projects, add screenshots to readme")
    plan["Week 1"] = week1

    week2 = []
    if leetcode < 50:
        week2.append("keep doing 2 leetcode a day, focus on arrays and strings")
    week2.append("deploy your best project if not deployed already")
    week2.append("update your linkedin headline")
    plan["Week 2"] = week2

    week3 = []
    week3.append("learn one new skill that companies actually use")
    week3.append("push code to github everyday")
    plan["Week 3"] = week3

    week4 = []
    week4.append("connect with 10 people on linkedin")
    week4.append("apply to 5 internships on internshala")
    plan["Week 4"] = week4

    return plan


def print_report(name, skills, projects, headline, leetcode, cgpa, github_repos):
    score = calculate_score(skills, projects, leetcode, cgpa, github_repos)
    label = get_label(score)
    issues = generate_roast(skills, projects, leetcode, headline)
    fixes = suggest_fixes(skills, projects, leetcode)
    new_headline = rewrite_headline(skills, projects)
    plan = make_plan(skills, projects, leetcode)

    report = ""
    report = report + "====================================\n"
    report = report + "  PROFILE ANALYSIS REPORT\n"
    report = report + "====================================\n\n"

    report = report + "Name: " + name + "\n"
    report = report + "CGPA: " + str(cgpa) + "\n"
    report = report + "Leetcode: " + str(leetcode) + "\n"
    report = report + "Github repos: " + str(github_repos) + "\n"
    report = report + "Projects: " + str(len(projects)) + "\n\n"

    report = report + "SCORE: " + str(score) + "/100\n"
    report = report + "VERDICT: " + label + "\n\n"

    report = report + "ISSUES FOUND:\n"
    i = 1
    for issue in issues:
        report = report + str(i) + ". " + issue + "\n"
        i = i + 1
    report = report + "\n"

    report = report + "FIXES:\n"
    i = 1
    for fix in fixes:
        report = report + str(i) + ". " + fix + "\n"
        i = i + 1
    report = report + "\n"

    report = report + "NEW HEADLINE SUGGESTION:\n"
    report = report + "Old: " + headline + "\n"
    report = report + "New: " + new_headline + "\n\n"

    report = report + "30 DAY PLAN:\n"
    for week in plan:
        report = report + week + ":\n"
        for task in plan[week]:
            report = report + "  - " + task + "\n"
        report = report + "\n"

    print(report)

    # using "with" now instead of manual open/close - this guarantees the
    # file gets closed even if something errors out mid-write
    try:
        with open("profile_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("report saved in profile_report.txt")
    except OSError as e:
        print("something went wrong while saving the file:", e)


def save_profile(data):
    try:
        with open("profile.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
        print("profile saved")
    except OSError as e:
        print("could not save profile file:", e)


def load_profile():
    try:
        with open("profile.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # basic check that this file actually has what we need
        # (fixes crash if profile.json is old/corrupted/missing keys)
        required_keys = ['name', 'skills', 'projects', 'headline', 'leetcode', 'cgpa', 'github_repos']
        for key in required_keys:
            if key not in data:
                print("saved profile is missing '" + key + "', ignoring it")
                return None
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("profile.json is corrupted, ignoring it")
        return None


def collect_projects():
    projects = []
    n = safe_int_input("how many projects do you have: ")
    for i in range(n):
        print("Project", i + 1)
        name = input("project name: ").strip()
        desc = input("what does it do (one line): ").strip()
        tech = input("tech used, comma separated: ")
        tech_list = split_and_clean(tech)
        deployed = yes_no("is it deployed? yes/no: ")

        p = {}
        p['name'] = name
        p['description'] = desc
        p['tech_used'] = tech_list
        p['deployed'] = deployed
        projects.append(p)
    return projects


def collect_profile():
    name = input("your name: ").strip()
    skills_input = input("your skills, comma separated: ")
    skills = split_and_clean(skills_input)

    projects = collect_projects()

    headline = input("your linkedin headline: ").strip()
    leetcode = safe_int_input("leetcode problems solved: ")
    cgpa = safe_float_input("your cgpa: ", min_value=0.0, max_value=10.0)
    github_repos = safe_int_input("number of github repos: ")

    data = {}
    data['name'] = name
    data['skills'] = skills
    data['projects'] = projects
    data['headline'] = headline
    data['leetcode'] = leetcode
    data['cgpa'] = cgpa
    data['github_repos'] = github_repos
    return data


def main():
    print("====================================")
    print(" DEVELOPER PROFILE ANALYZER")
    print(" (my first python project lol)")
    print("====================================")

    saved = load_profile()

    if saved != None:
        print("found a saved profile for", saved['name'])
        if yes_no("use saved profile? yes/no: "):
            data = saved
        else:
            data = collect_profile()
            save_profile(data)
    else:
        print("no saved profile found, lets make one")
        data = collect_profile()
        save_profile(data)

    name = data['name']
    skills = data['skills']
    projects = data['projects']
    headline = data['headline']
    leetcode = data['leetcode']
    cgpa = data['cgpa']
    github_repos = data['github_repos']

    print("\nanalyzing your profile...\n")
    print_report(name, skills, projects, headline, leetcode, cgpa, github_repos)


if __name__ == "__main__":
    main()