on run argv
	set the_file to (item 1 of argv)
	try
		tell application "iTunes" to add POSIX file the_file 
	end try
	return the_file
end run
