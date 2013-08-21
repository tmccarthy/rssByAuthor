# Main method, invokes the getRssForAuthor method for the given feed url and 
# author, and writes the returned element to the given file.
def main():
    import sys
    import xml.etree.ElementTree

    getRssForAuthor(sys.argv[1], sys.argv[2]).write(sys.argv[3])


# Searches the rss feed at the given url for items whose author matches the
# given author.
def getRssForAuthor(author, rssFeedUrl):
    import lxml.etree as etree

    rssXml = etree.fromstring(getHttpResourceBody(rssFeedUrl))

    for item in rssXml.find('channel').findall('item'):
        itemAuthor = None
        
        currentItemAuthorElement = item.find('author')

        # If the current item's author element is None (ie it doesn't exist)
        # then we attempt to retrieve the item's author from the item link.
        if currentItemAuthorElement is None:
            itemAuthor = getAuthorFromWebpage(item.find('link').text)
        else:
            itemAuthor = currentItemAuthorElement.text

        # If we are still unable to identify the author of the item, or the
        # author field does not contain the name of the author we are searching
        # for, we remove this item from the dom.
        if (itemAuthor is None) or (author.lower() not in itemAuthor.lower()):
            rssXml.find('channel').remove(item)

    return etree.ElementTree(rssXml)


# Attemps to parse a webpage looking for the author of that page.
def getAuthorFromWebpage(url):
    
    import lxml.html as html

    dom = html.fromstring(getHttpResourceBody(url))

    authorClassElements = dom.find_class('author')

    return None if authorClassElements is None else authorClassElements[0].text


# Retrieve the resource from the given url. Any http status that isn't 2xx will
# lead to an exception being thrown.
def getHttpResourceBody(url):
    import http.client
    import urllib.parse

    server = urllib.parse.urlparse(url)[1]
    resource = urllib.parse.urlparse(url)[2]

    try:
        httpConnection = http.client.HTTPConnection(server);
        httpConnection.request("GET", resource)
        
        httpResponse = httpConnection.getresponse()

        body = httpResponse.read().lstrip()
        if httpResponse.status < 200 and httpResponse.status >= 300:
            raise http.client.HTTPException(str(httpResponse.status) 
                                            + ": " + str(httpResponse.reason))
        httpConnection.close()

        return body
    except:
        raise
    finally:
        httpConnection.close()


if __name__ == '__main__':main()

