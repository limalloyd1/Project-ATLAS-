import os 
import hashlib 

def checkHash(filename:str, algo='sha256'):
    try:
        with open(filename, 'rb') as infile:
            hasher = hashlib.new(algo)
    
            # generate sha256 hash file contents
            while chunk := infile.read(8192):
                hasher.update(chunk)
        
            result_hash = hasher.hexdigest()

        with open('hashes.txt', 'r') as infile:
            if result_hash in infile:
                print("MATCH FOUND - FILE IS POTENTIALLY MALWARE")
            else:
                print("File seems clean")
        return result_hash

    except Exception as e:
        print(f"An error occured: {e}")
        return 


def checkFolder(root):
    try:
        with open(root) as infile:
            if os.path.isdir(root):
                for item in os.listdir(root):
                    item = os.path.join(root, item)
                    if os.path.isdir(item):
                        checkfolder(item)
                    h = checkHash(item,'sha256')
            
            elif os.path.isfile:
                checkHash(item)


    except Exception as e:
        pass


filePath = "/home/limalima/Downloads/soul_eater_smoke.mp4"
h = checkHash(filePath)
print(h)

