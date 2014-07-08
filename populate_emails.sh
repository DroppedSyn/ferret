#!/bin/bash
# Grep the corp dir for email addresses and created a CSV file

#The corp dir in CSV format
CORPDIR="corpdir.txt"
#Intermediate file that contains all email addresses
OUT="emails_clean.txt"
#The file used to populate the "verified" table
CSVDATA="dbout.txt"
# Hack to pull out email addresses, ignoring the name
grep -Eio '\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b' $CORPDIR > $OUT
rm -f $CSVDATA 
for line in `cat $OUT`;
do
        echo $line | sed -e "s/@.*$//" -e "s/$/,twitter_not_provided,DEFAULT,FALSE,0/" >> dbout.txt
done

ABPATH=`pwd -P`/$CSVDATA
# Update the DB with new entries, this will not add emails that aren't already there
psql -1 << EOF
\x
CREATE TEMP TABLE tmp_table 
ON COMMIT DROP
AS
SELECT * 
FROM verified;

COPY tmp_table FROM '$ABPATH' DELIMITERS ',';

INSERT INTO verified
SELECT DISTINCT ON (email) *
FROM tmp_table
WHERE email NOT IN (SELECT email FROM verified);
EOF
rm $OUT
