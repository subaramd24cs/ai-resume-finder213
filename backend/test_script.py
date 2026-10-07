import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"

def run_tests():
    print("Starting tests...")
    
    # Wait a sec for the server to be fully ready
    time.sleep(2)
    
    # 1. Register
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "password123"
    print(f"Registering {username}...")
    res = requests.post(f"{BASE_URL}/api/auth/register", json={"username": username, "password": password})
    assert res.status_code == 200, f"Register failed: {res.text}"
    
    # 2. Login
    print("Logging in...")
    res = requests.post(f"{BASE_URL}/api/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create Job Description
    print("Creating Job Description...")
    jd = "We need a Python developer with FastAPI, MongoDB, and Machine Learning experience. Strong communication skills required."
    res = requests.post(f"{BASE_URL}/api/jobs/analyze", headers=headers, json={"job_description": jd})
    assert res.status_code == 200, f"JD Analyze failed: {res.text}"
    
    # 4. Upload Resumes
    print("Uploading Resumes...")
    # create fake pdf or docx content (using plain text with .pdf extension might fail validation, let's use a real-ish one or create a text file)
    # The server accepts docx and pdf.
    with open("dummy_resume.docx", "wb") as f:
        f.write(b"Dummy resume content")
        
    with open("dummy_resume.docx", "rb") as f:
        files = [('files', ('dummy_resume.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))]
        res = requests.post(f"{BASE_URL}/api/resumes/upload", headers=headers, files=files)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    
    # 5. Match Candidates
    print("Matching candidates...")
    res = requests.post(f"{BASE_URL}/api/match", headers=headers, json={"job_description": jd})
    assert res.status_code == 200, f"Match failed: {res.text}"
    
    # 6. Rankings
    print("Getting rankings...")
    res = requests.get(f"{BASE_URL}/api/rankings", headers=headers)
    assert res.status_code == 200, f"Rankings failed: {res.text}"
    rankings = res.json().get("data", [])
    assert len(rankings) > 0, "No rankings found"
    
    # 7. Candidate Details
    cand_id = rankings[0]['resume_id']
    print(f"Getting candidate details for {cand_id}...")
    res = requests.get(f"{BASE_URL}/api/candidates/{cand_id}", headers=headers)
    assert res.status_code == 200, f"Candidate details failed: {res.text}"
    
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
