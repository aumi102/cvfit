from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from typing import Literal, List, Optional

class ScoreOptions(BaseModel):
    target_role: Optional[str] = None
    language: Literal["vi","en"] = "vi"
    strictness: Literal["lenient","balanced","strict"] = "balanced"
    output_formats: List[Literal["json","docx"]] = ["json","docx"]

class ScoreCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cv_file_id: str = Field(validation_alias=AliasChoices("cv_file_id", "cv_id"))
    jd_text: str = Field(min_length=30, validation_alias=AliasChoices("jd_text", "job_description"))
    options: ScoreOptions = ScoreOptions()
