from jira import JIRA

jira = JIRA(server='https://jira.atlassian.com')
auth_jira = JIRA(basic_auth=('email', 'API token'))

