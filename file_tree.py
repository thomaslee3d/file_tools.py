#!/usr/bin/env python3
import os
import sys

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "build",
    "dist",
    "__pycache__"
}

IGNORE_FILES = {
    ".DS_Store",
    "package-lock.json",
    "yarn.lock"
}

def print_welcome():
    print("=========================================")
    print("  Welcome to the Folder Mapping Script   ")
    print("=========================================")
    print("\nThis script will:")
    print("1. Ask for a folder (or use '.') to scan.")
    print("2. Print the folder tree, skipping 'node_modules' and some common files.")
    print("3. List files with numeric indices.")
    print("4. Let you choose files by number or '.' for all.")
    print("5. Optionally search for files containing specific word combinations.")
    print("Type 'q' or 'quit' at any prompt to exit.\n")

def get_folder_path():
    """
    Prompt user for a folder path. 
    If the user inputs '.' or an empty string, use current directory.
    If the user types 'q' or 'quit', exit the script.
    """
    while True:
        folder = input("Enter the folder path (or '.' for current folder): ").strip()
        if folder.lower() in ['q', 'quit']:
            sys.exit("Quitting...")
        if folder == "" or folder == ".":
            folder = os.getcwd()
        if os.path.isdir(folder):
            return folder
        else:
            print(f"Error: '{folder}' is not a valid directory. Please try again.")

def scan_directory(base_path):
    """
    Recursively walk through the directory and:
    - Skip ignored directories (e.g., node_modules)
    - Skip ignored files
    Return a list of (file_index, file_full_path) that are discovered.
    """
    file_list = []
    index = 1

    for root, dirs, files in os.walk(base_path, topdown=True):
        # Modify 'dirs' in place to skip IGNORE_DIRS
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        
        # We also skip files that appear in IGNORE_FILES or start with '.'
        for f in files:
            if f in IGNORE_FILES or f.startswith('.'):
                continue
            full_path = os.path.join(root, f)
            file_list.append((index, full_path))
            index += 1

    return file_list

def print_folder_tree(base_path, prefix=""):
    """
    Print the folder structure in a tree-like format while skipping IGNORE_DIRS.
    """
    # Gather directories and files at this level
    try:
        entries = os.listdir(base_path)
    except PermissionError:
        # If permission denied, skip
        return
    except FileNotFoundError:
        # If somehow the directory doesn't exist, skip
        return

    # Filter out ignored directories and hidden directories/files
    dirs = []
    local_files = []
    for e in entries:
        full_e = os.path.join(base_path, e)
        if os.path.isdir(full_e):
            if e in IGNORE_DIRS or e.startswith('.'):
                continue
            dirs.append(e)
        else:
            if e in IGNORE_FILES or e.startswith('.'):
                continue
            local_files.append(e)

    # Sort them for consistent printing
    dirs.sort()
    local_files.sort()

    # Print the current folder name
    print(prefix + os.path.basename(base_path) + "/")

    # Increase prefix for children
    child_prefix = prefix + "  "
    # Print directories
    for d in dirs:
        print_folder_tree(os.path.join(base_path, d), prefix=child_prefix)

    # Print files
    for f in local_files:
        print(child_prefix + f)

def prompt_file_selection(file_list):
    """
    Print the list of files with numeric indices.
    Prompt the user to select files by their indices, or '.' to select all.
    Return the list of selected file paths.
    """
    if not file_list:
        print("No files found.")
        return []

    print("\nList of discovered files:")
    for idx, path in file_list:
        print(f"{idx}. {path}")

    print("\nEnter the file indices separated by spaces (e.g., '1 3 5'), ")
    print("or '.' to select all, or 'none' to select none.")
    print("Type 'q' or 'quit' to exit.")

    while True:
        selection = input("Your selection: ").strip()
        if selection.lower() in ['q', 'quit']:
            sys.exit("Quitting...")
        if selection == '.':
            # select all
            return [p for _, p in file_list]
        if selection.lower() == 'none':
            return []
        # parse indices
        try:
            indices = list(map(int, selection.split()))
            selected_files = []
            valid_indices = {idx for idx, _ in file_list}
            for i in indices:
                if i not in valid_indices:
                    print(f"Index {i} is not in the list of files.")
                    break
            else:
                # If we didn't break
                for i in indices:
                    # find the corresponding path
                    for idx, path in file_list:
                        if idx == i:
                            selected_files.append(path)
                            break
                return selected_files
        except ValueError:
            print("Invalid input. Please enter indices like '1 2 3' or '.' or 'none'.")

def search_in_files(files, search_terms):
    """
    Search each file in 'files' for lines that contain ALL search terms.
    If all search terms appear in a line, print that line (and file).
    """
    terms = [t.lower() for t in search_terms]  # Lowercase for basic matching

    for f in files:
        try:
            with open(f, 'r', encoding="utf-8") as file_reader:
                lines = file_reader.readlines()
            matched_lines = []
            for line_num, line in enumerate(lines, 1):
                lower_line = line.lower()
                if all(term in lower_line for term in terms):
                    matched_lines.append((line_num, line.strip()))
            if matched_lines:
                print(f"\nFile: {f}")
                for ln, text in matched_lines:
                    print(f"  Line {ln}: {text}")
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            # Skip files that can't be read or do not exist
            pass

def main():
    print_welcome()

    # Ask user if they want to map the folder
    while True:
        map_choice = input("Do you want to map a folder? (y/n): ").strip().lower()
        if map_choice in ['q', 'quit']:
            sys.exit("Quitting...")
        if map_choice not in ['y', 'n']:
            print("Invalid input. Please answer 'y' or 'n'.")
            continue
        break

    if map_choice == 'n':
        print("No folder mapping selected. Exiting...")
        sys.exit(0)

    # Get folder path
    folder_path = get_folder_path()

    # Print folder tree
    print("\nFolder Tree:\n")
    print_folder_tree(folder_path)

    # Scan directory and list files
    file_list = scan_directory(folder_path)

    # Let the user select files
    selected_files = prompt_file_selection(file_list)
    if not selected_files:
        print("No files selected.")
    else:
        print(f"\nYou have selected {len(selected_files)} file(s).")

    # Optionally search for word combinations
    while True:
        search_choice = input("Do you want to search for specific word combinations in the selected files? (y/n): ").strip().lower()
        if search_choice in ['q', 'quit']:
            sys.exit("Quitting...")
        if search_choice not in ['y', 'n']:
            print("Invalid input. Please answer 'y' or 'n'.")
            continue
        if search_choice == 'n':
            break
        # If yes, gather search terms
        search_input = input("Enter the words you want to search for (separated by spaces), or '.' for no search: ").strip()
        if search_input == '.':
            break
        search_terms = search_input.split()
        if search_terms:
            search_in_files(selected_files, search_terms)
        else:
            print("No search terms entered.")
        # After search, ask if they want to do another search or quit
        another = input("Another search? (y/n): ").strip().lower()
        if another not in ['y']:
            break

    print("\nDone. Exiting...")

if __name__ == "__main__":
    main()
