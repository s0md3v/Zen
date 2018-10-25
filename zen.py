import re
import json
import argparse
import threading
try:
	import urllib.request as urlib_alias 
	from urllib.error import HTTPError 
except ImportError:
	import urllib2 as urlib_alias
	from urllib2 import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument('target', help='target')
parser.add_argument('-o', help='output file', dest='output')
parser.add_argument('-u', help='your username', dest='uname')
parser.add_argument('-t', help='number of threads', dest='threads', type=int)
parser.add_argument('--org', help='organization', dest='org', action='store_true')
parser.add_argument('--breach', help='check emails for breach', dest='breach', action='store_true')
args = parser.parse_args()

inp = args.target
breach = args.target
output = args.output
organization = args.org
uname = args.uname or ''
thread_count = args.threads or 2

end = '\033[1;m'
green = '\033[1;32m'
bad = '\033[1;31m[-]\033[1;m'
info = '\033[1;33m[!]\033[1;m'

print ('''%s
 _____ _____ _____          ___     ___                                             
|__   |   __|   | |     _ _|_  |   |_  |  
|   __|   __| | | |    | | |_| |_ _ _| |_ 
|_____|_____|_|___|     \_/|_____|_|_____|                                                       
%s''' % (green, end))

inp = inp.strip(" /")

targetOrganization = targetRepo = targetUser = False

jsonOutput = {}

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

password_mgr = urlib_alias.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, "https://api.github.com", username, '')
handler = urlib_alias.HTTPBasicAuthHandler(password_mgr)
opener = urlib_alias.build_opener(handler)
urlib_alias.install_opener(opener) 

def get(url):
	try:
		f = urlib_alias.urlopen(url)
		try:
			body = f.read().decode("utf-8")
		finally:
			f.close()
	except HTTPError:
		body =""
	return body


def findContributorsFromRepo(username, repo):
	response = get('https://api.github.com/repos/%s/%s/contributors?per_page=100' % (username, repo))
	contributors = re.findall(r'https://github\.com/(.*?)"', response)
	return contributors

def findReposFromUsername(username):
	response = get('https://api.github.com/users/%s/repos?per_page=100&sort=pushed' % username)
	repos = re.findall(r'"full_name":"%s/(.*?)",.*?"fork":(.*?),' % username, response)
	nonForkedRepos = []
	for repo in repos:
		if repo[1] == 'false':
			nonForkedRepos.append(repo[0])
	return nonForkedRepos

def findEmailFromContributor(username, repo, contributor):
	response = get('https://github.com/%s/%s/commits?author=%s' % (username, repo, contributor))
	latestCommit = re.search(r'href="/%s/%s/commit/(.*?)"' % (username, repo), response)
	if latestCommit:
		latestCommit = latestCommit.group(1)
	else:
		latestCommit = 'dummy'
	commitDetails = get('https://github.com/%s/%s/commit/%s.patch' % (username, repo, latestCommit))
	email = re.search(r'<(.*)>\nDate', commitDetails)
	if email:
		email = email.group(1)
		if breach:
			jsonOutput[contributor] = {}
			jsonOutput[contributor]['email'] = email
			if get('https://haveibeenpwned.com/api/v2/breachedaccount/' + email):
				email = email + ' \033[1;31m[\033[0mpwned\033[1;31m]\033[0m'
				jsonOutput[contributor]['pwned'] = True
			else:
				jsonOutput[contributor]['pwned'] = False
		else:
			jsonOutput[contributor] = email
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
	print ('%s Total contributors: %s%i%s' % (info, green, len(contributors), end))
	for contributor in contributors:
		email = (findEmailFromContributor(username, repo, contributor))
		if email:
			print (contributor + ' : ' + email)

def findUsersFromOrganization(username):
	response = get('https://api.github.com/orgs/%s/members?per_page=100' % username)
	members = re.findall(r'"login":"(.*?)"', response)
	return members

def threader(function, arg):
    threads = []
    for i in arg:
        task = threading.Thread(target=function, args=(i,))
        threads.append(task)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    del threads[:]

def flash(function, arg):
    for begin in range(0, len(arg), thread_count):
        end = begin + thread_count
        splitted = arg[begin:end]
        threader(function, splitted)
def main():
	if targetOrganization:
		usernames = findUsersFromOrganization(username)
		flash(findEmailFromUsername, usernames)
	elif targetUser:
		findEmailFromUsername(username)
	elif targetRepo:
		findEmailsFromRepo(username, repo)

	if output:
		json_string = json.dumps(jsonOutput, indent=4)
		with open(output, 'w+') as f:
			f.write(json_string)

if __name__ == "__main__":
	main()
