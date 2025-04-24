import requests
import zipfile
import os
import datetime
import json
import time
from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Generate dynamic URLs based on job type and date
def generate_url(date, job_type):
    return f"https://api.seasonaljobs.dol.gov/datahub-search/sjCaseData/zip/{job_type}/{date}"

# Get absolute file paths to avoid file not found errors
def get_json_file_path(destination_folder, date, job_type):
    return os.path.abspath(os.path.join(destination_folder, f"{job_type}_{date}.json"))

# Check if today's JSON file already exists
def json_already_downloaded(destination_folder, date, job_type):
    file_path = get_json_file_path(destination_folder, date, job_type)
    return os.path.exists(file_path)

# Retry downloading ZIP files to handle incomplete reads
def download_file_with_retry(url, destination_folder, filename, retries=3, wait_time=5):
    file_path = os.path.join(destination_folder, filename)
    
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    
            return file_path  # Return file path if successful
        
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(wait_time)  # Wait before retrying
            else:
                print("Download failed after multiple attempts.")
                return None

    return None  # If all retries fail, return None

# Download and extract ZIP files with validation
def download_and_extract_zip(url, destination_folder, date, job_type):
    zip_filename = f"{job_type}_{date}.zip"
    json_filename = f"{job_type}_{date}.json"
    json_file_path = get_json_file_path(destination_folder, date, job_type)
    
    if json_already_downloaded(destination_folder, date, job_type):
        print(f"{job_type.upper()} JSON for {date} already downloaded.")
        return [json_file_path]
    
    zip_path = download_file_with_retry(url, destination_folder, zip_filename)
    
    if zip_path and os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(destination_folder)

            os.remove(zip_path)  # Remove ZIP after extraction

            extracted_json_files = [os.path.join(destination_folder, file) for file in os.listdir(destination_folder) if file.endswith(".json")]
            
            # Rename the extracted JSON file correctly
            if extracted_json_files:
                os.rename(extracted_json_files[0], json_file_path)

            return [json_file_path]
        except zipfile.BadZipFile:
            print(f"Corrupt ZIP file encountered: {zip_path}")
            os.remove(zip_path)  # Remove corrupt file
            return []
    else:
        print(f"Download failed or file not found: {zip_filename}")
        return []

# Fetch data based on job type (H2A/H2B)
def fetch_data(job_type):
    current_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)  # Convert to EST
    formatted_date = current_date.strftime("%Y-%m-%d")

    destination_folder = "data"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    url = generate_url(formatted_date, job_type)
    json_files = download_and_extract_zip(url, destination_folder, formatted_date, job_type)

    return json_files

@app.route("/", methods=["GET", "POST"])
def landing_page():
    if request.method == "POST":
        job_type = request.form.get("jobType")  # Get selected job type
        return redirect(url_for("show_jobs", job_type=job_type))
    return render_template("landing.html")

# Validate JSON before loading
def is_valid_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json.load(file)
        return True
    except json.JSONDecodeError:
        return False

@app.route("/jobs/<job_type>")
def show_jobs(job_type):
    json_files = fetch_data(job_type)
    data = []

    for json_file in json_files:
        if is_valid_json(json_file):
            with open(json_file, "r", encoding="utf-8") as file:
                json_data = json.load(file)

                for job in json_data:
                    if job_type == "h2b":
                        data.append({
                            "empBusinessName": job.get("empBusinessName"),
                            "jobTitle": job.get("tempneedJobtitle"),
                            "locationCity": job.get("empCity"),
                            "locationState": job.get("empState"),
                            "startDate": job.get("tempneedStart"),
                            "endDate": job.get("tempneedEnd"),
                            "minExperience": job.get("jobMinexpmonths"),
                            "jobDuties": job.get("jobDuties"),
                            "contactEmail": job.get("emppocEmail")
                        })
                    elif job_type == "h2a":
                        clearance_order = job.get("clearanceOrder", {})
                        data.append({
                            "empBusinessName": job.get("empBusinessName"),
                            "jobTitle": clearance_order.get("jobTitle"),
                            "locationCity": clearance_order.get("jobCity"),
                            "locationState": clearance_order.get("jobState"),
                            "startDate": clearance_order.get("jobBeginDate"),
                            "endDate": clearance_order.get("jobEndDate"),
                            "minExperience": clearance_order.get("jobMinexpmonths"),
                            "jobDuties": clearance_order.get("jobDuties"),
                            "contactEmail": job.get("emppocEmail")
                        })
        else:
            print(f"Invalid JSON file skipped: {json_file}")

    return render_template("index.html", jobs=data, job_type=job_type)

# Scheduled function to update both H2A and H2B data daily
def scheduled_job():
    print("Running scheduled job to update H2A and H2B data...")
    fetch_data("h2a")
    fetch_data("h2b")
    print("Data update completed.")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, "cron", hour=0, minute=0)  # Daily update at midnight EST
scheduler.start()

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()