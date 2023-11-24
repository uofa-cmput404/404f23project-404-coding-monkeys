strip_slash = lambda url: url[:-1] if url[-1] == "/" else url

def get_id_from_url(url):
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")
        return url[-1]
    return ""

def get_part_from_url(url, part):
    # part is one of authors, posts, or comments and will return the id for that part
    if url:
        url = url[:-1] if url[-1] == "/" else url
        url = url.split("/")

        index = 0
        while index < len(url) and url[index] != part:
            index += 1
        
        # return id right after we find the part
        return url[index+1] if index < len(url) - 1 else ""
    return ""

