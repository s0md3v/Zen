<h1 align="center">
  <br>
  <a href="https://github.com/s0md3v/Zen"><img src="https://image.ibb.co/eNj5Qf/zenlogo.png" alt="Zen"></a>
</h1>

<h4 align="center">Find email addresses of Github users</h4>

<p align="center">
  <a href="https://github.com/s0md3v/Zen/releases">
    <img src="https://img.shields.io/github/release/s0md3v/Zen.svg">
  </a>
  <a href="https://travis-ci.com/s0md3v/Zen">
    <img src="https://img.shields.io/travis/com/s0md3v/Zen.svg">
  </a>
  <a href="https://github.com/s0md3v/Zen/issues?q=is%3Aissue+is%3Aclosed">
      <img src="https://img.shields.io/github/issues-closed-raw/s0md3v/Zen.svg">
  </a>
</p>

![demo](https://image.ibb.co/nenkff/Screenshot-2018-10-17-21-41-53.png)

#### Find email address of a user
`python zen.py username`

or

`python zen.py https://github.com/username`

#### Find email addressess of contributors of a repository
`python zen.py https://github.com/username/repository`


#### Find email addresses of members of an organization
`python zen.py organization --org`

or

`python zen.py https://github.com/orgs/organzation`

#### Save JSON output to a file
`python zen.py https://github.com/username/repository -o /path/to/file`

#### Rate limiting
Github allows 60 unauthenticated requests per hour but limit for authenticated requests is 6000 per hour.
You don't need to generate any kind of authenticated token, just supply your username via `-u` option as follows:

`python zen.py username -u yourUsername`

#### Threading
Zen supports multi-threading for faster data retrieval.

`python zen.py IBM --org -t 20`

#### Check if email has appeared in a breach
Zen uses haveibeenpwned.com API to check if an email has been breached or not. This feature is turned off by default and can be used with `--breach` option as follows

`python zen.py s0md3v --breach`
