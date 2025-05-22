from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Literal


class AnatomicalLocalisation(BaseModel):
    name: str = Field(..., description="The name of the anatomical localisation")
    confidence: float = Field(...,
                              description="The score of clinical confidence (from 0 to 1) in this anatomical hypothesis")
    reason: str = Field(..., description="Rationale based on clinical history, physical findings, or prior data")


class Pathophysiology(BaseModel):
    name: str = Field(...,
                      description="Name of the suspected pathophysiological condition (e.g., genetic epilepsy, FS+)")
    confidence: float = Field(...,
                              description="The estimated likelihood (between 0 and 1) of the condition being the underlying cause")
    reason: str = Field(..., description="Justification for the diagnosis based on the patient's clinical features.")


class NeurologyQuestion(BaseModel):
    question: str = Field(..., description="Exact question to be asked during neurological review.")
    topic: str = Field(..., description="The topic of the question.")
    target_sympthom: str = Field(..., description="The symptom or risk factor the question is designed to assess.")
    question_type: Literal["ROUTINE", "SPECIFIC"] = Field(...,description="Whether the question is routine or more specific.")


class DiagnosticTest(BaseModel):
    test: str = Field(..., description="Name of the investigation (e.g., EEG, MRI)")
    reason: str = Field(..., description="Why this investigation is considered relevant for the case")
    mandatory_or_optional: Literal["Mandatory", "Optional"] = Field(...,
                                                                    description="Whether the test must be performed or is recommended as supplementary")
    urgency: str = Field(..., description="How urgently the test should be carried out (e.g., 'within 2 weeks')")


class TreatmentRecommendation(BaseModel):
    diagnosis: str = Field(..., description="Diagnosis associated with the recommended treatment")
    treatment: str = Field(..., description="Proposed treatment including drug name, dose, and form if applicable")
    timing: str = Field(..., description="Recommended time frame for initiating or evaluating the treatment")


class NeurologyReport(BaseModel):
    compressed_summary: str = Field(..., description="P1: A brief summary of the clinical case, highlighting key facts")
    anatomical_localisations: List[AnatomicalLocalisation] = Field(...,
                                                                   description="List of possible anatomical origins of seizures with confidence levels")
    pathophysiologies: List[Pathophysiology] = Field(...,
                                                     description="Possible underlying disease mechanisms and justifications")
    questions: List[NeurologyQuestion] = Field(...,
                                               description="Structured neurological history and examination questions")
    investigations: List[DiagnosticTest] = Field(...,
                                                 description="Diagnostic investigations including urgency and priority")
    treatments: List[TreatmentRecommendation] = Field(...,
                                                      description="Initial treatment plan for each hypothesized diagnosis")

