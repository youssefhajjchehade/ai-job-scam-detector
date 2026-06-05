import re


def detect_warning_signs(job_text: str) -> list[str]:
    text = job_text.lower()
    warning_signs = []

    patterns = {
        "Unrealistic salary or income promise": [
            r"\$\s?\d{4,}",
            r"\d{4,}\s?(usd|dollars|per week|weekly)",
            r"earn\s+\$?\d+",
            r"make\s+\$?\d+",
            r"high income",
            r"unlimited income",
        ],
        "Requests payment or financial information": [
            r"payment information",
            r"bank account",
            r"wire transfer",
            r"western union",
            r"registration fee",
            r"processing fee",
            r"upfront fee",
            r"send money",
            r"deposit",
        ],
        "Asks for sensitive personal information": [
            r"social security",
            r"passport",
            r"id card",
            r"personal details",
            r"driver.?s license",
            r"date of birth",
            r"national id",
        ],
        "Too easy / no experience required": [
            r"no experience",
            r"no skills required",
            r"no degree required",
            r"work from home immediately",
            r"start immediately",
            r"easy job",
            r"simple work",
        ],
        "Urgency or pressure": [
            r"apply now",
            r"limited spots",
            r"urgent hiring",
            r"immediate start",
            r"hiring immediately",
            r"act fast",
        ],
        "Vague job/company description": [
            r"various tasks",
            r"general duties",
            r"flexible role",
            r"online tasks",
            r"work at your own pace",
            r"be your own boss",
        ],
    }

    for category, regex_list in patterns.items():
        for pattern in regex_list:
            if re.search(pattern, text):
                warning_signs.append(category)
                break

    return warning_signs