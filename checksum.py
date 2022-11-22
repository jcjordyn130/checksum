import hashlib
import pathlib
import os
import time
import sys
import concurrent.futures
import argparse
import json

class UnsupportedChecksumException(Exception):
    pass

def walk(path: pathlib.Path | str):
	for path in pathlib.Path(path).iterdir():
		if path.is_dir():
		    yield from walk(path)
		    continue

		yield path.resolve()


def get_checksum(file: pathlib.Path, algo: str):
    def get_checksum_sha256(file):
        m = hashlib.sha256()
        with file.open("rb") as file:
            while True:
                chunk = file.read(16 * 1024 * 1024)
                if not chunk: break
                m.update(chunk)
        return m.hexdigest()

    def get_checksum_sha512(file):
        m = hashlib.sha512()
        with file.open("rb") as file:
            while True:
                chunk = file.read(16 * 1024 * 1024)
                if not chunk: break
                m.update(chunk)
        return m.hexdigest()
            
    if algo == "sha256":
        return get_checksum_sha256(file)
    elif algo == "sha512":
        return get_checksum_sha512(file)
    else:
        raise UnsupportedChecksumException("sha256 and sha512 are the only supported algos as of now.")

def verify_file(file1 : pathlib.Path, file2: pathlib.Path):
    with file1.open("rb") as file1_obj, file2.open("rb") as file2_obj:
        while True:
            file1_data  = file1_obj.read(16 * 1024 * 1024)
            file2_data = file2_obj.read(16 * 1024 * 1024)

            if (not file1_data and file2_data) or (not file2_data and file1_data):
                return False
            
            if not file1_data or not file2_data:
                break
            
            if file1_data != file2_data:
                print(f"!!!! {file1} and {file2} are NOT the same with verify_file! !!!!")
                return False


        return True
    
# list containing old path, new path, old csum, new csum
difffiles = []

# Integer that's incremented as a file is processed.
# This is incremented at the end, just in case an error occurs or something.
filecount = 0

# files that cause exceptions when processing
# contains the old file, new file, and the exception tuple from sys.exc_info
# This isn't the most efficient way to handle it, but whatever.
errors = {}

# Skipped files
skippedcount = 0

# Time of script execution, as seconds since the UNIX epoch.
timestarted = int(time.time())

def file_stat_print():
    with open("/tmp/csum_stats", "w") as file:
        print(f"Total Files Processed: {filecount}", file = file)
        print(f"Number of Sucessful Processed Files: {filecount - len(errors)}", file = file)
        print(f"Number of Differing Files: {len(difffiles)}", file = file)
        print(f"Number of Skipped files: {skippedcount}", file = file)
        print(f"Number of Errors: {len(errors)}", file = file)
        print(errors, file = file)


    # because both pathlib paths and python classes aren't JSON encodable
    # we have to convert the errors here.
    formatted_es = {str(key): [value[0].__name__, str(value[1])] for (key, value) in errors.items()}

    with open("/tmp/output.json", "w") as file:        
        json.dump({"timestarted": timestarted, "filecount": filecount, "errorcount": len(errors), "diffcount": len(difffiles), "skippedcount": skippedcount, "errors": formatted_es, "oldroot": str(args.oldroot), "newroot": str(args.newroot), "checksum": args.checksum}, file, indent = 2)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checksum", default = "sha256", help = "Checksum algorithm to use (currently supported: sha256)")
    parser.add_argument("--verify", action = "store_true", help = "Verifies file content byte by byte in addition to the checksum.", default = False)
    parser.add_argument("oldroot", help = "First directory to compare files from (this one is where the file list is obtained from)", type = pathlib.Path)
    parser.add_argument("newroot", help = "Second directory to compare files from", type = pathlib.Path)
    args = parser.parse_args()
    
    executor = concurrent.futures.ThreadPoolExecutor()
    
    for file in walk(args.oldroot):
        try:
            # Process file statistics every 10 files or so
            if not filecount % 10 and filecount > 1:
                file_stat_print()
                
            print(f"Testing {file}!")

            relfile = file.relative_to(args.oldroot)
            newfile = args.newroot / file.relative_to(args.oldroot)

            if not file.is_file() or not newfile.is_file():
                print(f"Skipping {file} because either {file} or {newfile} is not a regular file!")
                skippedcount+=1
                continue
 
            # The two roots may be on different disks, so concurrent.futures is used here
            # to allow both files to be read at the same time for increased speed.
            csum_obj = executor.submit(get_checksum, file, args.checksum)
            newcsum_obj = executor.submit(get_checksum, newfile, args.checksum)

            csum = csum_obj.result()
            newcsum = newcsum_obj.result()

            if csum != newcsum:
                print(f"{file} and {newfile} are NOT the same!")
                difffiles.append((file, newfile, csum, newcsum))

            if args.verify:
                if not verify_file(file, newfile):
                    difffiles.append((file, newfile, "verify", "verify"))
                    
            filecount+=1
        except KeyboardInterrupt as e:
            # For some reason KeyboardInterrupt is caught by a catch-all except,
            # so handle it here as to not cause erratic behavior.
            raise SystemExit(0)
        except UnsupportedChecksumException as e:
            raise
        except:
            exc = sys.exc_info()
            errors.update({relfile: exc})
            
    file_stat_print()
