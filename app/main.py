from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.executor import execute_python, execute_cpp, execute_java

app = FastAPI()

class CodeRequest(BaseModel):
    code: str
    language: str  # 'python', 'cpp', 'java'

@app.post("/execute")
def run_code(req: CodeRequest):
    lang = req.language.lower()
    if lang == 'python':
        return execute_python(req.code)
    if lang == 'cpp':
        return execute_cpp(req.code)
    if lang == 'java':
        return execute_java(req.code)
    raise HTTPException(status_code=400, detail="Unsupported language")
