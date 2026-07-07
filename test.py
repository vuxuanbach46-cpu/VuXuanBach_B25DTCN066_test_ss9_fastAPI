from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional, Literal , Any

app = FastAPI()

courses_db = [
    {
        "id": 1,
        "course_name": "FastAPI Masterclass",
        "duration_hours": 32,
        "price": 1500000,
        "status": "active",
        "created_at": "2026-07-01T02:00:00Z",
    },
    {
        "id": 2,
        "course_name": "NextJS Next-Level",
        "duration_hours": 45,
        "price": 1800000,
        "status": "active",
        "created_at": "2026-07-01T03:15:00Z",
    },
]

class BaseRequest(BaseModel):
    status_code : int 
    message : str 
    data : Optional[Any]  
    error : Optional[Any]
    timestamp : str
    path : str
    
class CreateCourse(BaseModel):
    course_name : str = Field(... , min_length=5)
    duration_hours : int = Field(... , gt=0)
    price : int = Field(... , ge=0)
    
    
def api_repoint(req: Request , status_code : int , message : str , data = None , error = None):
    return BaseRequest(
        status_code=status_code ,
        message=message , 
        data=data , 
        error=error , 
        timestamp=datetime.now().isoformat() , 
        path=req.url.path
    )
    

@app.exception_handler(RequestValidationError)
def validate_exc_handler(req : Request , exc : RequestValidationError):
    repoint = api_repoint(req , status.HTTP_404_NOT_FOUND , "Sai kiểu dữ liệu" , error=exc.errors())
    return JSONResponse(
        status_code=repoint.status_code , 
        content=repoint.model_dump()
    )
    
@app.exception_handler(HTTPException)
def validate_exc(
    req : Request , 
    exc : HTTPException
):
    repoint = api_repoint(req , exc.status_code , "Lỗi" , error=exc.detail)
    return JSONResponse (
        status_code=repoint.status_code , 
        content=repoint.model_dump()
    )



@app.get("/courses")
def get_all_courses(req : Request):
    if not courses_db : 
        return api_repoint(req , status.HTTP_200_OK , "Dữ liệu rỗng" , data=[] )
    
    return api_repoint(req , status.HTTP_200_OK , "Lấy danh sách thành công" , courses_db )

@app.post("/courses")
def create_course(req : Request , course_in : CreateCourse):
    
    duplicate_name = next((v for v in courses_db if v['course_name'].lower() == course_in.course_name.lower()) , None)
    
    if duplicate_name is not None : 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="ERR-EDU-01: Course name duplicates an existing record in memory array.")
    
    new_course = {
        "id": max(v["id"] for v in courses_db) + 1 if courses_db else 1,
        **course_in.model_dump(),
    }
    
    courses_db.append(new_course)
    
    return api_repoint(req , status.HTTP_201_CREATED , "Tạo mới khóa học thành công!" , new_course)


@app.delete("/courses/{course_id}")
def delete_course(course_id : int, req: Request):
    task = next((v for v in courses_db if v["id"] == course_id), None)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lỗi: Không tìm thấy mã khóa học yêu cầu để xóa!",
        )

    courses_db.remove(task)

    return api_repoint( req, status.HTTP_200_OK, "Xóa khóa học thành công")
