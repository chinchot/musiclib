on run argv
	tell application "iTunes"
		launch
		try
			set the_file to (item 1 of argv)
			add the_file
		end try
	end tell
end run
