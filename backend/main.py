from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
import uvicorn
from database import get_db
from jd_parser import analyze_job_description
from ml.model import process_single_resume
from ml.ranking import rank_candidates
from resume_parser import parse_resume
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
from bson import ObjectId

app = FastAPI(title="AI Resume Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_mongo_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

class JobRequest(BaseModel):
    job_description: str

class UserCreate(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Resume Finder API"}

# Auth Endpoints
@app.post("/api/auth/register")
def register(user: UserCreate):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    if db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user = {"username": user.username, "hashed_password": hashed_password}
    db.users.insert_one(new_user)
    
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"status": "success", "message": "User registered successfully", "access_token": access_token}

@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Login request for username: {form_data.username}")
    db = get_db()
    if db is None:
        print("Database not connected")
        raise HTTPException(status_code=500, detail="Database not connected")
        
    print("Database connected, finding user...")
    user = db.users.find_one({"username": form_data.username})
    print(f"User found: {user is not None}")
    
    if not user:
        print("User not found")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    print("Verifying password...")
    try:
        is_valid = verify_password(form_data.password, user["hashed_password"])
        print(f"Password valid: {is_valid}")
    except Exception as e:
        print(f"Password verification error: {e}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    if not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    print("Creating token...")
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    print("Token created")
    return {"access_token": access_token, "token_type": "bearer"}
        
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 1. Upload Resume
@app.post("/api/resumes/upload")
async def upload_resumes(files: List[UploadFile] = File(...), current_user: str = Depends(get_current_user)):
    if not files:
        raise HTTPException(status_code=400, detail="No resumes uploaded")
    
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    candidates = []
    db = get_db()
    
    for idx, file in enumerate(files):
        if file.content_type not in allowed_types and not file.filename.endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail=f"Invalid file type for {file.filename}.")
            
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} is too large.")
            
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
            
        parsed_data = parse_resume(temp_path)
        os.remove(temp_path)
        
        doc = {
            "name": parsed_data.get("name", "Unknown"),
            "email": parsed_data.get("email", "Unknown"),
            "phone": parsed_data.get("phone", "Unknown"),
            "original_filename": file.filename,
            "extracted_text": parsed_data.get("text", ""),
            "education": parsed_data.get("education", "Not explicitly found"),
            "experience": parsed_data.get("experience", "Not explicitly found"),
            "skills": parsed_data.get("skills", []),
            "upload_date": datetime.utcnow().isoformat(),
            "uploaded_by": current_user
        }
        
        if db is not None:
            try:
                res = db.resumes.insert_one(doc)
                doc["_id"] = str(res.inserted_id)
            except: pass
        candidates.append(format_mongo_doc(doc))
        
    return {"status": "success", "message": f"Successfully uploaded and parsed {len(candidates)} resumes.", "data": candidates}

# 2. Get Resumes
@app.get("/api/resumes")
def get_resumes(current_user: str = Depends(get_current_user)):
    db = get_db()
    if db is None: return {"status": "error", "message": "Database not connected"}
    resumes = [format_mongo_doc(r) for r in db.resumes.find({"uploaded_by": current_user})]
    return {"status": "success", "data": resumes}

# 3. Create Job Description
@app.post("/api/jobs/analyze")
async def analyze_jd(req: JobRequest, current_user: str = Depends(get_current_user)):
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
        
    jd_data = analyze_job_description(req.job_description)
    jd_data["created_at"] = datetime.utcnow().isoformat()
    jd_data["created_by"] = current_user
    
    db = get_db()
    if db is not None:
        try:
            res = db.job_descriptions.insert_one(jd_data)
            jd_data["_id"] = str(res.inserted_id)
        except: pass
    
    return {"status": "success", "data": format_mongo_doc(jd_data)}

# 4. Analyze Candidates
@app.post("/api/match")
async def match_candidates(req: JobRequest, current_user: str = Depends(get_current_user)):
    job_description = req.job_description
    
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    resumes = list(db.resumes.find({"uploaded_by": current_user}))
    if not resumes:
        raise HTTPException(status_code=400, detail="No resumes found. Please upload resumes first.")
        
    results = []
    analysis_date = datetime.utcnow().isoformat()
    
    for idx, cand in enumerate(resumes):
        raw_text = cand.get('extracted_text', '')
        
        # Run ML Pipeline
        candidate_result = process_single_resume(
            raw_resume_text=raw_text,
            raw_jd_text=job_description,
            candidate_name=cand.get('name', 'Unknown'),
            candidate_email=cand.get('email', 'Unknown')
        )
        
        # Format the analysis document
        analysis_doc = {
            "resume_id": str(cand['_id']),
            "job_description_snippet": job_description[:200] + "...",
            "candidate_info": {
                "name": cand.get('name'),
                "email": cand.get('email'),
                "phone": cand.get('phone'),
                "education": cand.get('education'),
                "experience": cand.get('experience')
            },
            "match_score": candidate_result["match_score"],
            "matching_skills": candidate_result["matching_skills"],
            "missing_skills": candidate_result["missing_skills"],
            "recommendation": candidate_result["recommendation"],
            "score_breakdown": candidate_result.get("score_breakdown", {}),
            "analysis_date": analysis_date,
            "analyzed_by": current_user
        }
        
        try:
            db.candidate_analysis.insert_one(analysis_doc)
            analysis_doc['_id'] = str(analysis_doc['_id'])
        except: pass
        
        analysis_doc['id'] = str(analysis_doc.get('_id', idx+1))
        analysis_doc['name'] = analysis_doc['candidate_info']['name']
        analysis_doc['email'] = analysis_doc['candidate_info']['email']
        analysis_doc['experience'] = analysis_doc['candidate_info']['experience']
        analysis_doc['education'] = analysis_doc['candidate_info']['education']
        
        results.append(analysis_doc)
        
    ranked = rank_candidates(results)
    return {"status": "success", "data": ranked}

# 5. Get Rankings
@app.get("/api/rankings")
def get_rankings(current_user: str = Depends(get_current_user)):
    db = get_db()
    if db is None: return {"status": "error", "message": "Database not connected"}
    analysis = [format_mongo_doc(a) for a in db.candidate_analysis.find({"analyzed_by": current_user}).sort("match_score", -1)]
    return {"status": "success", "data": analysis}

# 6. Get Candidate Details
@app.get("/api/candidates/{id}")
def get_candidate_details(id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    if db is None: return {"status": "error"}
    try:
        cand = db.resumes.find_one({"_id": ObjectId(id), "uploaded_by": current_user})
        if not cand: raise HTTPException(status_code=404, detail="Candidate not found")
        
        analysis = list(db.candidate_analysis.find({"resume_id": id, "analyzed_by": current_user}).sort("analysis_date", -1))
        
        cand = format_mongo_doc(cand)
        cand["analysis_history"] = [format_mongo_doc(a) for a in analysis]
        return {"status": "success", "data": cand}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# 7. Delete Resume
@app.delete("/api/resumes/{id}")
def delete_resume(id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    if db is None: return {"status": "error"}
    try:
        cand = db.resumes.find_one({"_id": ObjectId(id)})
        if not cand or cand.get("uploaded_by") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        db.resumes.delete_one({"_id": ObjectId(id)})
        db.candidate_analysis.delete_many({"resume_id": id})
        return {"status": "success", "message": "Resume and associated analysis deleted"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=400, detail="Error deleting resume")

# 8. ML Evaluation Storage (model_results)
@app.get("/api/ml/evaluation")
async def get_ml_evaluation(current_user: str = Depends(get_current_user)):
    db = get_db()
    if db is not None:
        try:
            latest = db.model_results.find_one(sort=[("created_at", -1)])
            if latest:
                return {"status": "success", "data": format_mongo_doc(latest)}
        except: pass
        
    metrics_path = os.path.join(os.path.dirname(__file__), 'ml', 'evaluation_metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                import json
                data = json.load(f)
                if db is not None:
                    data["created_at"] = datetime.utcnow().isoformat()
                    try: db.model_results.insert_one(data.copy())
                    except: pass
                return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    return {"status": "error", "message": "Evaluation metrics not found."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

