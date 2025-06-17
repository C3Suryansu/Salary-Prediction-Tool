from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class SalaryInput(BaseModel):
    working: bool
    relevant_degree: Optional[bool] = None
    ds_projects: Optional[bool] = None
    skills_rating: int = 0
    college_tier: str
    certifications: bool
    location: str
    domain: str
    current_company: Optional[str] = None
    data_related: Optional[bool] = None
    yo_experience: int = 0
    interested_in_ds: Optional[bool] = None


def calculate_salary(data: SalaryInput):
    def modifiers():
        percent = 0
        percent += 15 if data.college_tier=='tier1' else (-10 if data.college_tier=='tier3' else 0)
        percent += 5 if data.certifications else 0
        percent += 10 if data.location=='metro' else 0
        percent += 10 if data.domain in ['tech','bfsi'] else 0
        if data.working:
            percent += 20 if data.current_company=='top_mnc' else (-10 if data.current_company=='service_small' else 0)
        return percent

    mod = modifiers()

    if not data.working:
        if not data.relevant_degree:
            base = (2.5,4)
        elif not data.ds_projects:
            base = (3,5)
        elif data.skills_rating>=3:
            base = (4,8)
        else:
            base = (3,6)

        final = (round(base[0]*(1+mod/100),2),round(base[1]*(1+mod/100),2))
        return {'base_range':base,'final_range':final,'modifiers_percent':mod}

    else:
        if not data.data_related:
            if not data.interested_in_ds:
                base = (3,6)
            elif data.skills_rating>=3:
                base = (4,9)
            else:
                base = (3,6)

            final = (round(base[0]*(1+mod/100),2),round(base[1]*(1+mod/100),2))
            return {'base_range':base,'final_range':final,'modifiers_percent':mod}

        else:
            if data.yo_experience>2 and data.skills_rating>=4:
                return {'hike':'30-35% DS','modifiers_percent':mod}
            elif (data.yo_experience>2 and data.skills_rating<4) or (data.yo_experience<=2 and data.skills_rating>=4):
                return {'hike':'20-25% BA','modifiers_percent':mod}
            else:
                base = (3,6)
                final = (round(base[0]*(1+mod/100),2),round(base[1]*(1+mod/100),2))
                return {'base_range':base,'final_range':final,'modifiers_percent':mod}

@app.post("/predict")
def predict_salary(data: SalaryInput):
    res = calculate_salary(data)
    if 'final_range' in res:
        return res['final_range']
    else:
        return res['hike']
