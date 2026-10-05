import zipfile
import xml.etree.ElementTree as ET
import os
import re
import shutil

##Extraction block
def extract_imscc(imscc_path, extract_dir):
    """Unzip the .imscc package into a temporary folder."""
    with zipfile.ZipFile(imscc_path, 'r') as zip_ref: #open imscc in read mode ('r') 
        zip_ref.extractall(extract_dir) #creates temp folder if missing, for extraction
    print("Extraction complete!\n")

##Prep for parsing
#Strip the XML's namespace prefix in {}s for clean matching
def local_name(tag):
    return tag.rsplit('}', 1)[-1]

#Build resource dictionary for pass 1
def build_resource_dict(root):
    """Scans the XML for resource tags"""
    resource_dict = {}
    for elem in root.iter():
        if local_name(elem.tag) == 'resource':
            res_id = elem.get('identifier')  #Canvas identifers
            href = elem.get('href')          #file path for elements

            #store in dict only if both ID and path exist
            if res_id and href:
                resource_dict[res_id] = href

    return resource_dict

#Read module structure to organize items for pass 2
def extract_modules(root):
    """Navigates <organizations> to extract modules and child items."""
    modules = []

    #Locate <organization> container node in XML to read items and references
    org_node = None
    for elem in root.iter():
        if local_name(elem.tag) == 'organization':
            org_node = elem
            break

    if org_node is not None:
        #get child <item> elements under <organization>
        direct_items = [
            child for child in org_node if local_name(child.tag) == 'item'
        ]

        if len(direct_items) == 1 and any(
            local_name(c.tag) == 'item' for c in direct_items[0]
        ):
            module_elements = [
                c for c in direct_items[0] if local_name(c.tag) == 'item'
            ]
        else:
            module_elements = direct_items

        #loop through each module
        for mod_elem in module_elements:
            module_title = 'Untitled Module'
            for child in mod_elem:
                if local_name(child.tag) == 'title' and child.text:
                    module_title = child.text
                    break

            module_items = []

        #extract items inside module (docs, assignments, pages, etc.)
            for child in mod_elem:
                if local_name(child.tag) == 'item':
                    item_title = 'Untitled Item'
                    for sub in child:
                        if local_name(sub.tag) == 'title' and sub.text:
                            item_title = sub.text
                            break

                    ref = child.get('identifierref')  #Links resource dict's identifers/IDs to the XML's ID refs

                    module_items.append({'title': item_title, 'ref': ref})

            modules.append({'title': module_title, 'items': module_items})

    return modules

##Parsing block
#TODO: may need a try-except for atypical situations, need to test with other courses
def parse_manifest(manifest_path):
    """"Two pass parsing of imsmanifest.xml, returns resource_dict and modules."""
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    resource_dict = build_resource_dict(root) #pass 1
    modules = extract_modules(root) #pass 2

    return resource_dict, modules

##Output block
def clean_filename(name):
    """Removes characters not allowed in file/folder names"""
    clean_name = re.sub(r'[\\/*?:"<>|]', "", name)
    return clean_name.strip()

#Build module folders and copy files
def build_module_folders(resource_dict, modules, extract_dir, output_dir):
    """Creates physical module folders and copies over the matching files."""
    os.makedirs(output_dir, exist_ok=True) #check for top output folder

    copied_count = 0

    #Loop through each extracted module
    for mod_index, module in enumerate(modules, start=1):
        #Clean up title name
        clean_mod_title = clean_filename(module["title"])
        folder_name = f"{mod_index:02d}_{clean_mod_title}"
        mod_folder_path = os.path.join(output_dir, folder_name)

        os.makedirs(mod_folder_path, exist_ok=True)  #create physical folder

        #Process each item in this module
        for item in module["items"]:
            ref_id = item["ref"]

            #Check if ref_id exists in resource dict
            if ref_id and ref_id in resource_dict:
                rel_file_path = resource_dict[ref_id]
                src_file_path = os.path.join(extract_dir, rel_file_path)

                #Copy file if it exists
                if os.path.exists(src_file_path):
                    shutil.copy2(src_file_path, mod_folder_path)
                    copied_count += 1

    return copied_count

#TODO: delete temp files once copying is complete.

##TEST block
#TODO: replace hardcoded paths with Tkinter interaction so user can upload file
if __name__ == "__main__": 
    IMSCC_FILE = "Canvas_Commons_Example.imscc"
    TMP_DIR = "temp"
    OUTPUT_DIR = "course_backup"
    
    #Extract IMSCC course export package
    extract_imscc(IMSCC_FILE, TMP_DIR) #based on extract_imscc's positional arguments (imscc_path, extract_dir)
    
    #Parse xml manifest
    manifest_file = f"{TMP_DIR}/imsmanifest.xml"
    resource_dict, modules = parse_manifest(manifest_file)

    #Build folders and copy files
    copied = build_module_folders(resource_dict, modules, TMP_DIR, OUTPUT_DIR)

    #print summary results
    print(f"Pass 1 complete: indexed {len(resource_dict)} file resources.\n")
    print(f"Pass 2 complete: extracted {len(modules)} course modules.\n")
    print(f"{len(modules)} module folders created in '{OUTPUT_DIR}' with {copied} files copied.\n")

#TODO: with Tkinter, display status and success/error messages

    print("Sample resource mapping:")
    for res_id, href in list(resource_dict.items())[:5]:
        print(f" {res_id} -> {href}")
    if modules:
        first_mod = modules[0]
        print(f"Module 1 title: '{first_mod['title']}'")
        print(f"total items in M1: {len(first_mod['items'])}\n")
        print("Sample module items:")
        for item in first_mod['items'][:5]:
            print(f" - title: {item['title']} | Ref key: {item['ref']}")

#TODO: offer user a summary log file for copied and skipped items (may not be able to handle quizzes and discussions)