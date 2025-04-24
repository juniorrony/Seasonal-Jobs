import json

# Load JSON data
with open("case.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract employer emails
employer_emails = []
for item in data:
    employer_emails.append({"name": item["empBusinessName"], "email": item["emppocEmail"]})
    
print(employer_emails)