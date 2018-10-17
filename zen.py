import re
import json
import argparse
from requests import get

parser = argparse.ArgumentParser()
parser.add_argument('target', help='target')
parser.add_argument('-o', help='output file', dest='output')
parser.add_argument('--org', help='organization', dest='org', action='store_true')
args = parser.parse_args()

inp = args.target
output = args.output
organization = args.org

end = '\033[1;m'
green = '\033[1;32m'
bad = '\033[1;31m[-]\033[1;m'
info = '\033[1;33m[!]\033[1;m'

print ('''%s
	Z E N v1.0
%s''' % (green, end))

if inp.endswith('/'):
	inp = inp[:-1]

targetOrganization = targetRepo = targetUser = False

if inp.count('/') < 4:
	if '/' in inp:
		username = inp.split('/')[-1]
	else:
		username = inp
	if organization:
		targetOrganization = True
	else:
		targetUser = True
elif inp.count('/') == 4:
	targetRepo = inp.split('/')
	username = targetRepo[-2]
	repo = targetRepo[-1]
	targetRepo = True
else:
	print ('%s Invalid input' % bad)
	quit()

def findContributorsFromRepo(username, repo):
	response = get('https://api.github.com/repos/%s/%s/contributors?per_page=100' % (username, repo)).text
	contributors = re.findall(r'https://github\.com/(.*?)"', response)
	return contributors

def findReposFromUsername(username):
	response = get('https://api.github.com/users/%s/repos?per_page=100&sort=pushed' % username).text
	repos = re.findall(r'"full_name":"%s/(.*?)",.*?"fork":(.*?),' % username, response)
	nonForkedRepos = []
	for repo in repos:
		if repo[1] == 'false':
			nonForkedRepos.append(repo[0])
	return nonForkedRepos

def findEmailFromContributor(username, repo, contributor):
	response = get('https://github.com/%s/%s/commits?author=%s' % (username, repo, contributor)).text
	latestCommit = re.search(r'href="/%s/%s/commit/(.*?)"' % (username, repo), response).group(1)
	commitDetails = get('https://github.com/%s/%s/commit/%s.patch' % (username, repo, latestCommit)).text
	email = re.search(r'<(.*)>', commitDetails).group(1)
	return email

def findEmailFromUsername(username):
	repos = findReposFromUsername(username)
	for repo in repos:
		email = findEmailFromContributor(username, repo, username)
		if email:
			print (username + ' : ' + email)	
			break

def findEmailsFromRepo(username, repo):
	contributors = findContributorsFromRepo(username, repo)
	jsonOutput = {}
	print ('%s Total contributors: %s%i%s' % (info, green, len(contributors), end))
	for contributor in contributors:
		email = (findEmailFromContributor(username, repo, contributor))
		print (contributor + ' : ' + email)
		haveIBeenPawned(email)
		jsonOutput[contributor] = email
	if output:
		json_string = json.dumps(jsonOutput, indent=4)
		savefile = open(output, 'w+')
		savefile.write(json_string)
		savefile.close()

def findUsersFromOrganization(username):
	response = get('https://api.github.com/orgs/%s/members?per_page=100' % username).text
	members = re.findall(r'"login":"(.*?)"', response)
	return members

def haveIBeenPawned(email):
	url = 'https://haveibeenpwned.com/api/v2/breachedaccount/'+ email
	response = get(url)
	if response.status_code==200:
		Data=json.loads(response.content)
		print("%sThis email has been appeared in data breach for the first time on  %s\n%sFor more info %s" %(bad,Data[0]['BreachDate'],info,url))

if targetOrganization:
	usernames = findUsersFromOrganization(username)
	for username in usernames:
		findEmailFromUsername(username)
elif targetUser:
	findEmailFromUsername(username)
elif targetRepo:
	findEmailsFromRepo(username, repo)
