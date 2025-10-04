import re
import csv
import sys
from pandas import DataFrame
from typing import Optional, Pattern, List

def extract_from_message(msg: str, rx: Pattern) -> Optional[str]:
    # extract all text that matches the supplied regex pattern
    if not msg:
        return None
    
    m = rx.search(msg)
    if m:
        seg = m.group(1) or ''
        # replace newlines with spaces and collapse repeated whitespace
        extract = re.sub(r'[\r\n]+', ' ', seg)
        extract = re.sub(r'\s+', ' ', extract).strip()
        if extract != '':
            return extract
        
    return None


def parse_csv_list(s: Optional[str]) -> List[str]:
    """Parse a comma-separated string into a list of trimmed strings.

    Uses the csv module so quoted elements containing commas are handled
    correctly. Empty or all-whitespace items are dropped. If ``s`` is
    None or empty, returns an empty list.
    """
    if not s:
        return []
    try:
        parts = next(csv.reader([s]))
    except Exception:
        # fallback to simple split on comma
        parts = s.split(',')
    # trim whitespace and drop empty entries
    return [p.strip() for p in parts if p and p.strip()]

def parse_file(file_path: str) -> DataFrame:
    # Extract the raw sender text between 'From:' and 'To:'
    sender_re = re.compile(r'(?si)From:\s*(.*?)\s*To:')
    # Extract the raw recipient text between 'To:' and 'Subject:'
    recipient_re = re.compile(r'(?si)To:\s*(.*?)\s*Subject:')
    # Extract the raw date text between 'Date:' and 'From:'
    date_re = re.compile(r'(?si)Date:\s*(.*?)\s*From:')    
    # Extract the raw message text the line after 'X-FileName:'
    msg_text_re = re.compile(r'(?im)^X-FileName:.*\r?\n(?:[ \t]*\r?\n)+([\s\S]*)')

    # Increase csv field size limit to handle very large message fields
    try:
        csv.field_size_limit(sys.maxsize)
    except OverflowError:
        csv.field_size_limit(10**9)

    rows = []  # temporary list to hold file and message data for dataframe

    with open(file_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            fname = row.get('file') or row.get('File')
            msg = row.get('message') or row.get('Message') or ''
            rec_date = extract_from_message(msg, date_re)
            sender = extract_from_message(msg, sender_re)
            recipients_text = extract_from_message(msg, recipient_re)
            recipients = parse_csv_list(recipients_text) if recipients_text else []
            message_text = extract_from_message(msg, msg_text_re)

            rows.append({'file': fname, 'rec_date': rec_date, 'sender': sender, 'recipients': recipients, 'message_text': message_text})

    # Build DataFrame containing only the two columns requested
    return DataFrame(rows, columns=['file', 'rec_date', 'sender', 'recipients', 'message_text'])