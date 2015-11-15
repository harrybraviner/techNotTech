#! /usr/bin/python2.7

# BloombergScraper.py
# The purpose of this script is to take the url of a Bloomberg article and
# download the article, seperating out the title and subtitles from the
# body of the article.

import argparse, urllib2, sys, os, re, unicodedata
from bs4 import BeautifulSoup

# Read commandline arguments
parser = argparse.ArgumentParser(description="Get a Bloomberg article and convert to my data format.")
parser.add_argument('url', metavar='url', type=str)
args = parser.parse_args()

articlePage = urllib2.urlopen(args.url)
articleHTML = articlePage.read()
soup = BeautifulSoup(articleHTML, 'html.parser')

try:
    headline = soup.findAll('span', { 'class' : "lede-headline__highlighted"})[0].string

    subheaders = [element.string for element in soup.findAll('div', { 'class' : "article-abstract__item-text"})]

    bodyParas = [para.get_text() for para in soup.find('div', { 'class' : 'article-body__content' }).findAll('p')]

    body = reduce(lambda x, y: x + "\n\n" + y, bodyParas)

    # Normalise to ASCII
    headline = unicodedata.normalize('NFKD', headline).encode('ascii', 'ignore')
    subheaders = [unicodedata.normalize('NFKD', sub).encode('ascii', 'ignore') for sub in subheaders]
    body     = unicodedata.normalize('NFKD', body    ).encode('ascii', 'ignore')

    print "Got headline: " + headline

    if (subheaders == []):
        print "Found no subheaders"
        sys.exit()

    for sub in subheaders:
        print "Got subheader: " + sub

    if (body.strip() == ""):
        print "Found no body text"
        sys.exit()

    print "Got body text:\n" + body

except Exception as exception:
    print "Page did not conform to expected format!"
    print exception
    sys.exit()

try:
    dataFilenames = os.listdir("./data")
    numExtractRegex = re.compile(r'^(?P<num>\d+)[.]txt$')
    fileNums =      [int(numString) for numString in
                        [m.group('num') for m in
                            filter(lambda x : x, [numExtractRegex.match(filename) for filename in dataFilenames])
                        ]
                    ]
    fileNums.append(0)  # Need to do this in case the data directory is empty
    newFileNum = max(fileNums) + 1
    newFilename = "{0}.txt".format(newFileNum)

    outputFile = open("./data/{0}".format(newFilename), "w")
    
    outputFile.write("Headline: {0}\n".format(headline).encode('utf8'))
    for sub in subheaders:
        outputFile.write("Subheader: {0}\n".format(sub).encode('utf8'))
    outputFile.write("Body: {0}".format(body).encode('utf8'))
    
    outputFile.close()
    print "Succesfully wrote output to {0}".format(newFilename)

except Exception as exception:
    print 'Couldn\'t save to the data directory - are you sure it exists?'
    raise exception
    sys.exit()
