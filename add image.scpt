on run argv
	set album_name to item 1 of argv
	set track_name to item 2 of argv
	set pict_art2 to item 3 of argv


	tell application "Music"
		set main_playlist to library playlist "Library"
		repeat with playlist_index from 1 to count tracks of main_playlist
			set current_track to track playlist_index of main_playlist
			set current_track_name to name of current_track
			set current_album_name to album of current_track
			if track_name = current_track_name and album_name = current_album_name then
				set artworks_count to count artworks of current_track
				if artworks_count ≤ 0 then
					set data of artwork 1 of current_track to (read (POSIX file pict_art2) as picture)
				end if
				exit repeat
			end if
		end repeat
	end tell
end run