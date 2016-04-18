#!/bin/sh

# TODO: Create a python pipe out of this

here="`dirname \"$0\"`"
cd "$here" || exit 1
wait
cd scripts
mkdir "$here"/scripts/staging
mkdir "$here"/sources

python testrail.py "$here"

wait
# TODO: recursive search with python
cp "$here"/sources/*.png /"$here"/scripts/staging
cp "$here"/sources/*.eps /"$here"/scripts/staging
cp "$here"/sources/*.tex /"$here"/scripts/staging
cp "$here"/sources/*.gif /"$here"/scripts/staging
cp "$here"/sources/*.jpg /"$here"/scripts/staging
cp "$here"/sources/*.bst /"$here"/scripts/staging
cp "$here"/sources/*.bib /"$here"/scripts/staging
cp "$here"/sources/*.csl /"$here"/scripts/staging
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
echo "$here"

python assembler.py "$here" "$input_variable"

exit
