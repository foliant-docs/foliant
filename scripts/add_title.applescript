set x to 0

set doc1 to "atitle.docx"
set doc2 to "output.docx"

tell application "Finder"
	set current_path to container of (path to me) as alias
end tell

set theItems to {(current_path & doc1), (current_path & doc2)}
set theItems to only_doc(theItems) -- check files type
set theItems to ASCII_Sort(theItems)

tell application "Microsoft Word"
	activate
	make new document
	repeat with aFile in theItems
		tell application "Finder"
			set fileRef to ((a reference to file aFile) as string)
		end tell
		insert file at text object of selection file name fileRef
		if x < ((count of theItems) - 1) then
			insert break at text object of selection
		end if
		set x to x + 1
	end repeat
end tell

on only_doc(my_list)
	set cleanList to {}
	repeat with i from 1 to count my_list
		if (kind of (info for file ((item i of my_list) as string))) = "Alias" then
			tell application "Finder" to set filetype to type identifier of (info for file (original item of alias ((item i of my_list) as string) as text))
		else
			set filetype to type identifier of (info for file ((item i of my_list) as string))
		end if
		if filetype = "org.openxmlformats.wordprocessingml.document" then
			set cleanList's end to my_list's item i
		end if
	end repeat
	return the cleanList
end only_doc


on ASCII_Sort(my_list)
	set the index_list to {}
	set the sorted_list to {}
	repeat (the number of items in my_list) times
		set the low_item to ""
		repeat with i from 1 to (number of items in my_list)
			if i is not in the index_list then
				set this_item to item i of my_list as text
				if the low_item is "" then
					set the low_item to this_item
					set the low_item_index to i
				else if this_item comes before the low_item then
					set the low_item to this_item
					set the low_item_index to i
				end if
			end if
		end repeat
		set the end of sorted_list to the low_item
		set the end of the index_list to the low_item_index
	end repeat
	return the sorted_list
end ASCII_Sort

set docName to (current_path & "output.docx")

tell application "Microsoft Word"
	save as active document file name docName
	close active document
end tell

say "Done"