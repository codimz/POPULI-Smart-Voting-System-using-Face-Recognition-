with open('backend/app/schemas/admin.py', 'a') as f:
    f.write("""

class ElectionResultResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: dict = {}

class ResultData(BaseModel):
    candidate_name: str = ""
    vote_count: int = 0
    percentage: float = 0.0
""")
