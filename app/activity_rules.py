PROCESS_CATEGORY_RULES: dict[str, str] = {
    "code.exe": "Development",
    "pycharm64.exe": "Development",
    "cursor.exe": "Development",
    "outlook.exe": "Email",
    "explorer.exe": "File Management",
}

PROCESS_CONTAINS_RULES: dict[str, str] = {
    "teams": "Meeting",
}

WINDOW_TITLE_RULES: dict[str, str] = {
    "jira": "Issue Tracking",
    "azure devops": "Issue Tracking",
    "github": "Source Control",
}

BROWSER_PROCESSES: set[str] = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
}
