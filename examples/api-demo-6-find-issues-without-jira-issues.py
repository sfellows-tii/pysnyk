import argparse

from snyk import SnykClient
from utils import get_default_token_path, get_token


def parse_command_line_args():
    parser = argparse.ArgumentParser(description="Snyk API Examples")
    parser.add_argument(
        "--orgId", type=str, help="The Snyk Organisation ID", required=True
    )
    parser.add_argument(
        "--projectId", type=str, help="The Snyk Project ID", required=True
    )
    parser.add_argument(
        "--verbose", type=str, help="Enable verbose output", required=False, default="false"
    )
    return parser.parse_args()


snyk_token_path = get_default_token_path()
snyk_token = get_token(snyk_token_path)
args = parse_command_line_args()
org_id = args.orgId
project_id = args.projectId
verbose = args.verbose.lower() == "true"

client = SnykClient(snyk_token)
org = client.organizations.get(org_id)
project = org.projects.get(project_id)
issues = project.issueset_aggregated.all().issues
jira_issues = project.jira_issues.all()
snyk_issue_with_jira_issues = list(jira_issues.keys())

if not issues:
    print("No issues found in project %s" % project_id)
    exit(0)

# Print the total number of issues
print(f"Total number of issues in project \"{project.name}\" ({project_id}) [{org.name}]: {len(issues)}")

# Prepare CSV output
csv_filename = f"snyk_issues_without_jira_{project_id}.csv"
with open(csv_filename, mode="w", newline="") as csvfile:
    fieldnames = ["issue_id", "issue_url"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for issue in issues:
        if issue.id not in list(jira_issues.keys()):
            issue_url = f"https://app.snyk.io/org/{org.name}/project/{project_id}#{issue.id}"
            if verbose:
                print(f"Found issue without Jira issue: {issue.id}")
                print(f"  {issue_url}")
            writer.writerow({"issue_id": issue.id, "issue_url": issue_url})

print(f"Output written to {csv_filename}")
