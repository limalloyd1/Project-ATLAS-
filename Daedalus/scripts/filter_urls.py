
allowValues = (
    "/library/socket",
    "/howto/sockets",
    "/library/select",
    "/library/selectors",
    "/library/socketserver",
    "/library/ssl",
)

allowedDomain = "docs.python.org"

rejectValues = (
    "/genindex",
    "/search",
    "/contents",
    "/bugs",
    "/license",
    "/tutorial",
    "/faq",
    "/glossary",
    "/reference",
    "/using",
    "/install",
    "/extending",
    "/c-api",
    ".pdf",
    "#",
    "?highlight=",
)

def filterURLs(filename: str):
    try:
        infile = open(filename)
        lines = infile.readlines() # store lines in list
        infile.close()
    except Exception as e:
        print(f"An error occured: {e}")
        return False

    links = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if allowedDomain not in line:
            continue

        if not any (val in line for val in allowValues):
            continue
        
        if any(val in line for val in rejectValues):
            continue 

        links.add(line)

    # write to output file:
    try:
        outfile = open("/home/limalima/Atlas/Hermes/data/filtered/socketLibSourcesFiltered.txt", 'w')
        for item in links:
            outfile.write(f"{item}\n")

        print(f"Successfully wrote to outfile")
        outfile.close()
    except Exception as e:
        print(e)

filterURLs("/home/limalima/Atlas/Hermes/data/input/socketLibSources.txt")



