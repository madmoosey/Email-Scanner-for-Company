import csv
import re
from pathlib import Path

UNREACHABLES_FILE = "clean_unreachables.csv"
EXTRA_EMAILS = [
    "sean.mbogo@####.com",
    "c####.p####@####.com",
]

EMAIL_RE = re.compile(
    r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)+$",
    re.IGNORECASE,
)

BAD_CHARS_RE = re.compile(r"[\xc2\xc3\xa3\xbe\x8e\xae\x83\xa8\xe6\xc4\xca\n]")


def normalize_email(value):
    if value is None:
        return ""

    email = value.strip().replace(" ", "").lower()
    if EMAIL_RE.match(email):
        return email

    cleaned = BAD_CHARS_RE.sub("", email)
    if EMAIL_RE.match(cleaned):
        return cleaned

    return ""


def load_unreachables(path):
    unreachable = set()

    with open(path, "r", newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            email = row[0].strip().replace(" ", "").lower()
            if email and email != "email":
                unreachable.add(email)

    return unreachable


def process_file(filename, unreachables_file=UNREACHABLES_FILE):
    source = Path(filename)
    cleaned_output = source.with_name(f"customer_zaius_{source.name}")
    unreachable_output = source.with_name(f"UNREACHABLES_{source.name}")
    send_output = source.with_name(f"SENT_EMAILS_{source.name}")

    unreachables = load_unreachables(unreachables_file)
    invalid_rows = []
    valid_emails = []

    with open(source, "r", newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)

        try:
            next(reader)
        except StopIteration:
            pass

        for row in reader:
            if not row:
                continue

            raw_email = row[0]
            email = normalize_email(raw_email)

            if email:
                valid_emails.append(email)
            else:
                invalid_rows.append(raw_email)

    valid_emails.extend(EXTRA_EMAILS)

    with open(cleaned_output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email"])

        for email in valid_emails:
            writer.writerow([email])

        for bad in invalid_rows:
            if "'" in bad.lower():
                writer.writerow([bad])
            else:
                writer.writerow([f"FIX THIS EMAIL: {bad!r}"])

    with open(unreachable_output, "w", newline="", encoding="utf-8") as f_unr, \
         open(send_output, "w", newline="", encoding="utf-8") as f_send:
        unr_writer = csv.writer(f_unr)
        send_writer = csv.writer(f_send)

        for email in valid_emails:
            if email in unreachables:
                unr_writer.writerow([email])
            else:
                send_writer.writerow([email])

    print("Processing complete!")
    print(f"Valid/cleaned output: {cleaned_output}")
    print(f"Unreachables output:  {unreachable_output}")
    print(f"Send list output:     {send_output}")


def main():
    filename = input("What is the filename: ").strip()
    process_file(filename)


if __name__ == "__main__":
    main()
