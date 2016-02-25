#!/bin/sh

# TODO: Create a python pipe out of this

here="`dirname \"$0\"`"
cd "$here" || exit 1
wait
cd scripts
mkdir "$here"/scripts/staging

wait
# TODO: recursive search with python
cp "$here"/sources/**/*.png /"$here"/scripts/staging
cp "$here"/sources/**/**/*.png /"$here"/scripts/staging
cp "$here"/sources/**/*.eps /"$here"/scripts/staging
cp "$here"/sources/**/**/*.eps /"$here"/scripts/staging
cp "$here"/sources/*/*.tex /"$here"/scripts/staging
cp "$here"/sources/**/*.gif /"$here"/scripts/staging
cp "$here"/sources/**/**/*.jpg /"$here"/scripts/staging
cp "$here"/sources/**/*.jpg /"$here"/scripts/staging
cp "$here"/sources/*/*.bst /"$here"/scripts/staging
cp "$here"/sources/**/**/*.bib /"$here"/scripts/staging
cp "$here"/sources/*/*.bib /"$here"/scripts/staging
cp "$here"/sources/*/*.csl /"$here"/scripts/staging
wait

clear
echo "Choose output format: pdf (p), docx (d), tex (t), md (m) or gdrive update (g)"
read input_variable
echo "\n"
date +"%T"

case $input_variable in
    p ) python assembler.py "$here" "$input_variable"
        wait
        cd "$here"/scripts/staging;
		mv output.pdf "$here";
		rm -r "$here"/scripts/staging;
        ;;
    d ) echo "Converting images..."
        find "$here"/scripts/staging -iname '*.eps' -exec mogrify -format png -transparent white -density 200 {} +;
        python assembler.py "$here" "$input_variable"
        wait
        cd "$here"/scripts/staging;
		mv output.docx "$here";
		rm -r "$here"/scripts/staging;
        ;;
    g ) echo "Converting images..."
        find "$here"/scripts/staging -iname '*.eps' -exec mogrify -format png -transparent white -density 200 {} +;
        python assembler.py "$here" "$input_variable"
        wait
        cd "$here"/scripts/staging;
        mv output.docx "$here";
        rm -r "$here"/scripts/staging;
        cd "$here"/scripts
        python "$here"/scripts/gdoc_uploader.py "$here" 
        ;;
    m ) python assembler.py "$here" "$input_variable"
        wait
        cd "$here"/scripts/staging;
		mv output.md "$here";
		wait;
		rm -r "$here"/scripts/staging;
        ;;
    t ) python assembler.py "$here" "$input_variable"
        wait
        cd "$here"/scripts/staging;
		mv output.tex "$here";
		wait;
		rm -r "$here"/scripts/staging;
		;;
    esac
exit