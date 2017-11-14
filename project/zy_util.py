import os.path


def get_filepart_path(file_uri, part_id):
	idd = part_id.decode("utf-8", "ignore")
	filename = file_uri.decode("utf-8", "ignore") 
	filepath = os.path.join(self.drive_path, filename, idd + ".zylo")
	return filepath
