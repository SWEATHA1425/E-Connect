from datetime import datetime
import pytz
import re
from pydantic import BaseModel, validator, ValidationError,Field
from typing import Any, Optional, List, Dict, Union
from datetime import date,datetime

class Item(BaseModel):
    email: str
    # password: str
    name: str

class Item2(BaseModel):
    email: str
    # password: str
    name:str

class Item(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    position: str
    date_of_joining: str

    # @validator("email")
    # def validate_email(cls, value):
    #     if not value:
    #         raise ValueError("Email must be provided.")
    #     # if (("@rbg" not in value) and ('.ai' not in value)):
    #     #     raise ValueError("Invalid email.")
    
    #@validator("password")
    #def validate_password(cls, value):
     #   if not value:
      #      raise ValueError("Password must be provided.")
       # if len(value) < 8:
        #    raise ValueError("Password must be at least 8 characters long.")
        #if not re.search(r"[0-9]", value):
         #   raise ValueError("Password must contain at least one number.")
        #if not re.search(r"[@#$%&]", value):
         #   raise ValueError("Password must contain at least one special character (@#$%&).")
        #return value*/
    
    @validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name must be provided.")
        return value

class Item2(BaseModel):
    email: str
    password: str

class Item3(BaseModel):
    id: str
    
class Item4(BaseModel):
    data: str 
    id:str
    filename:str
    
class Item5(BaseModel):
    client_name: str 
    email:str

class Item9(BaseModel):
    client_name: str 
    email:str
    userid:str
    password:str
    
class Csvadd(BaseModel):
    data :str
    name:str
    fileid:str

class Csvedit(BaseModel):
    data:str
    name:str
    id:int
    fileid:str

class Csvdel(BaseModel):
    id:int
    fileid:str

class CT(BaseModel):
    name:str
    userid:str

    @property
    def current_time(self) -> str:
        now  = datetime.now(pytz.timezone("Asia/Kolkata"))
        return now.strftime("%I:%M:%S %p")
    
class UserId(BaseModel):
    user_id: str

class Item6(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    reason: str
    selectedDate: date
    requestDate: date 

class Item7(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    reason: str
    selectedDate: date
    ToDate : date
    requestDate: date
    
class Item8(BaseModel):
    userid: str
    employeeName: str
    time: str
    leaveType: str
    selectedDate: date
    requestDate: date
    timeSlot :str 
    reason: str   

class Item9(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    selectedDate: date
    reason: str
    requestDate: date

class SubTask(BaseModel):
    title: str
    done: bool = False

class Comment(BaseModel):
    id: Union[int, str]
    user: str
    text: str
    timestamp: str

class FileRef(BaseModel):
    id: str             # string id (uuid or stringified ObjectId)
    name: str
    size: int
    type: str
    uploadedAt: str
    uploadedBy: Optional[str] = "Employee"
    path: Optional[str] = None

class Tasklist(BaseModel):
    task: List[str]
    userid: str
    date:str
    due_date: str
    assigned_by: str = "self" 
    priority: str = "Medium" 
    subtasks: List[SubTask] = []
    comments: List[Comment] = []      
    files: List[FileRef] = []

class SingleTaskAssign(BaseModel):
    task: List
    userid: str
    due_date: str
    date:str
    TL: str
    assigned_by: str  
    priority: str = "Medium" 
    subtasks: List[SubTask] = []
    comments: List[Comment] = []      
    files: List[FileRef] = [] 

class Taskedit(BaseModel):
    userid: str
    taskid: Union[str, int]
    updated_task: Optional[Union[str, List[str]]] = None 
    status: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None 
    subtasks: Optional[List[Any]] = [] 
    comments: Optional[List[Any]] = [] 
    files: Optional[List[Any]] = [] 

class Gettasks(BaseModel):
    userid: str
    date: str

class Deletetask(BaseModel):
    taskid: str

class RemoteWorkRequest(BaseModel):
    userid: str
    employeeName: str
    fromDate: date
    toDate: date
    requestDate: date
    reason: str
    ip: str

class DeleteLeave(BaseModel):
    userid: str
    fromDate: str
    requestDate: str
    leavetype: str

class AddEmployee(BaseModel):
    name: str
    email: str
    phone: str
    position: str
    department: str
    address: str
    date_of_joining: str
    education: List[Dict[str, Union[str,int]]] 
    skills: List[Dict[str, Union[str, int]]] 
    TL: str
    personal_email: str
    resume_link: str
    status: str
    ip: str
    


class EditEmployee(BaseModel):
    userid: str
    name: str
    email: str
    phone: str
    position: str
    department: str
    address: str 
    date_of_joining: str 
    education: List[Dict[str, Union[str, int]]]
    skills: List[Dict[str, Union[str, int]]]
    TL: str
    personal_email: str
    resume_link: str
    status: str
    ip: str
    
    @validator('skills')
    def validate_skills(cls, v):
        """Ensure skill levels are integers"""
        for skill in v:
            if 'level' in skill:
                try:
                    skill['level'] = int(skill['level'])
                except (ValueError, TypeError):
                    skill['level'] = 0
        return v
# class EditEmployee(BaseModel):
#  userid: str
#  name: str
#  email: str
#  phone: str
#  position: str
#  department: str
#  address: str 
#  education: List[Dict[str, Union[str,int]]] # A list of educational qualifications
#  skills: List[Dict[str, Union[str, int]]] # A list of skills with 'name' and 'level'
#  TL: str
#  personal_email: str
#  resume_link:str
#  status: str
#  ip:str


# class Taskassign(BaseModel):
#     Task_details: List[Dict[str, Union[str, int, List[str]]]]
class Taskassign(BaseModel):
    Task_details: List[Dict[str, Any]]
    
class Settings(BaseModel):
    authjwt_secret_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhZG1pbl9pZCIsInJvbGUiOiJhZG1pbiIsImV4cGlyZXMiOjE3MDk3MTM2NjEuMjc5ODk4NH0.DwYyZBkO20Kicz5vvqxpCrxZ7279uHRlLttNDBVO-_E"
    authjwt_algorithm: str = "HS256"

class NotificationModel(BaseModel):
    userid: str
    title: str
    message: str
    type: str
    priority: Optional[str] = "medium"
    action_url: Optional[str] = None

class NotificationUpdate(BaseModel):
    is_read: bool

class NotificationFilter(BaseModel):
    userid: Optional[str] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None

class Holiday(BaseModel):
    date: str   # YYYY-MM-DD
    name: str

class HolidayYear(BaseModel):
    year: int
    holidays: List[Holiday]

class AssignPayload(BaseModel):
    task_id: str
    assigned_to: str
    tl: str
    title: str


# Message schema aligned with Chat.jsx
class Message(BaseModel):
    id: Optional[str] = None          # unique ID (MongoDB _id or frontend tempId)
    tempId: Optional[str] = None      # temporary ID from frontend
    type: str = "message"             # "message", "reaction", "thread"
    from_user: str                    # sender userId
    to_user: str                      # recipient userId
    text: Optional[str] = None        # text message
    file: Optional[str] = None        # file name if uploaded
    chatId: str                       # deterministic chat id (userA_userB)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Thread message schema (replies inside a thread)
class ThreadMessage(BaseModel):
    id: Optional[str] = None
    tempId: Optional[str] = None
    type: str = "thread"
    rootId: str                       # parent message ID
    from_user: str
    to_user: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Reaction schema
class Reaction(BaseModel):
    type: str = "reaction"
    messageId: str                    # message being reacted to
    emoji: str
    user: str                         # who reacted
    delta: Optional[int] = 1          # +1 or -1 for toggling


# Chat history response
class ChatHistoryResponse(BaseModel):
    chatId: str
    messages: List[Message]


#  Online presence payload
class PresencePayload(BaseModel):
    type: str = "presence"
    users: List[str]
    
class Settings(BaseModel):
    authjwt_secret_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhZG1pbl9pZCIsInJvbGUiOiJhZG1pbiIsImV4cGlyZXMiOjE3MDk3MTM2NjEuMjc5ODk4NH0.DwYyZBkO20Kicz5vvqxpCrxZ7279uHRlLttNDBVO-_E"
    authjwt_algorithm: str = "HS256"


# Assign Docs
class AssignPayload(BaseModel):
    docName: str
    userIds: List[str]

class ReviewPayload(BaseModel):
    userId: str
    docName: str
    status: str  # "verified"
    remarks: str = ""

class ReviewDocument(BaseModel):
    file_id: str
    status: str
    remarks: str = None

class GroupCreate(BaseModel):
    name: str
    members: List[str]

class GroupUpdate(BaseModel):
    name: Optional[str]
    members: Optional[List[str]]

class UpdateGroupPayload(BaseModel):
    name: str
    members: list[str]