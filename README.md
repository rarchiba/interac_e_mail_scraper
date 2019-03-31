Interac E-mail Scraper for G-mail
---------------------------------
This will search your G-mail account for e-mails from the
INTERAC e-mail payment system and return a pandas DataFrame
of the resulting data in the format:
ID  Payer Amount Date

Based on the GMAIL api python quickstart.

Usage
-----
1. Enable the Gmail API:
 * Go here: https://developers.google.com/gmail/api/quickstart/python
 * Follow Step 1 on the page.
 * Move the credentials.json to this directory.

2. pip install -r requirements.txt

3. Run the program. Bu default, it outputs a csv of the results
