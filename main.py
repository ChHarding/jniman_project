import zipfile

###Extraction block
def extract_imscc(imscc_path, extract_dir):
    """Unzip the .imscc package into a temporary folder."""
    with zipfile.ZipFile(imscc_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extraction complete!\n")

#TEST
if __name__ == "__main__":
    IMSCC_FILE = "Canvas_Commons_Example.imscc"
    TMP_DIR = "temp"
    
    extract_imscc(IMSCC_FILE, TMP_DIR)