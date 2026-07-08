
allowVals = ("Getting-started", "Lighting","Advanced-OpenGL","Advanced-Lighting","PBR","Guest-Articles")


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

        if "learnopengl.com" not in line:
            continue

        if not any (val in line for val in allowVals):
            continue

        links.add(line)

    # write to output file:
    try:
        outfile = open("/home/limalima/AtlasProj/Argus/data/filtered/filteredLinks.txt", 'w')
        for item in links:
            outfile.write(f"{item}\n")

        print(f"Successfully wrote to outfile")
        outfile.close()
    except Exception as e:
        print(e)

# filterURLs("/home/limalima/AtlasProj/Argus/data/input/learnOpenGLSources.txt")
#  filterURLs("/home/limalima/AtlasProj/Argus/data/input/stackOverflowOpenGL.txt")




