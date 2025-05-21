import os
from typing import List

import pandas as pd
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field, BaseModel

from models import AnatomicalLocalisation, Pathophysiology, DiagnosticTest, TreatmentRecommendation

df = pd.read_csv("../data/extracted_data.csv")
df.head()

anatomical_localisations: List[AnatomicalLocalisation] = Field(...,
                                                               description="List of possible anatomical origins of seizures with confidence levels")

llm = init_chat_model("openai:gpt-4.1")

class AnatomicalLocalisations(BaseModel):
    anatomical_localisations: List[AnatomicalLocalisation] = Field(...,
                                                                   description="List of anatomical localisations identified by the doctors in the given text.")

class Pathophysiologies(BaseModel):
    pathophysiologies: List[Pathophysiology] = Field(...,
                                                         description="List of possible diagnosis prognozed by the doctor in the text.")

class NextClinicalExaminations(BaseModel):
    investigations: List[DiagnosticTest] = Field(...,
                                                 description="List of next clinical tests identified by the doctor in the text.")

class Treatments(BaseModel):
    treatments: List[TreatmentRecommendation] = Field(...,
                                                      description="List of the treatments given by the doctor to the patients in the text.")

def generate_analytical_localizations(text:str):
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a neurology doctor and you should identify all analytical localizations provided by the doctor in the text.
             Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
            """
        ),
        ("human", "{query}"),
    ]).partial(schema=AnatomicalLocalisations.model_json_schema())
    parser = PydanticOutputParser(pydantic_object=AnatomicalLocalisations )
    query = text
    chain = prompt | llm | parser
    report: AnatomicalLocalisations = chain.invoke({"query": query})
    return report


def generate_pathophysiologies(text:str):
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a neurology doctor and you should identify all pathophysiologies given by the doctor in the text.
             Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
            """
        ),
        ("human", "{query}"),
    ]).partial(schema=Pathophysiologies.model_json_schema())
    parser = PydanticOutputParser(pydantic_object=Pathophysiologies )
    query = text
    chain = prompt | llm | parser
    report: Pathophysiologies = chain.invoke({"query": query})
    return report


def generate_next_clinical_examinations(text:str):
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a neurology doctor and you should identify all next clinical examinations given by the doctor in the text.
             Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
            """
        ),
        ("human", "{query}"),
    ]).partial(schema=NextClinicalExaminations.model_json_schema())
    parser = PydanticOutputParser(pydantic_object=NextClinicalExaminations )
    query = text
    chain = prompt | llm | parser
    report: NextClinicalExaminations = chain.invoke({"query": query})
    return report


def generate_next_treatments(text:str):
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a neurology doctor and you should identify all treatments given by the doctor in the text.
             Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
            """
        ),
        ("human", "{query}"),
    ]).partial(schema=Treatments.model_json_schema())
    parser = PydanticOutputParser(pydantic_object=Treatments )
    query = text
    chain = prompt | llm | parser
    report: Treatments = chain.invoke({"query": query})
    return report

test = """
The clinical presentation of progressive paraesthesia and only minimal sensory deficits with associated hyperreflexia in the upper and lower limbs (but with normal motor functions, cranial nerves, and fundoscopy) can be suggestive of cervical myelopathy. Notably, the patientâ€™s intact and increased reflexes make peripheral neuropathy less likely, and her lack of risk factors (only borderline B12 deficiency, no history of diabetes) further supports this. The presence of sensory symptoms in the hands also raises the possibility of carpal tunnel syndrome (CTS) (sensory symptoms are known to  dominate the clinical picture in early stages of CTS). The absence of prior neurological symptoms is not suggestive of a relapsing-remitting course. Importantly, the patient reports symptom exacerbation upon neck flexion, indicative of Lâ€™hermitte phenomenon, which is often associated with pro - cesses affecting the cervical spinal cord such as compressive cervical myelopathy or inflammation (including multiple sclerosis or transverse myelitis). The patientâ€™s hyperreflexia as an upper motor neuron feature further suggests spinal cord involvement. Sphincter signs which would be expected in spinal lesion were absent here. Given these clinical find - ings, the patient warrants further investigation, including MRI of the cervical spine, to confirm the diagnosis and guide subsequent management. MRI of the thoracic and lumbar spine was also performed (Figs.  1.1, 1.2, 1.3, and 1.4). F/i.sc/g.sc/u.sc/r.sc/e.sc /one.taboldstyle./one.taboldstyle  MRI T2WI, sagittal scanThoughts 4 F/i.sc/g.sc/u.sc/r.sc/e.sc /one.taboldstyle.(  MRI T2WI, sagittal scan F/i.sc/g.sc/u.sc/r.sc/e.sc /one.taboldstyle.)  MRI T2WI, axial scan F/i.sc/g.sc/u.sc/r.sc/e.sc /one.taboldstyle./four.taboldstyle  MRI FLAIR image, sagittal scan
"""

thought = """
We evaluated a female presenting acutely with heralding
symptoms of drowsiness and blurred vision. Clinically, she
exhibited right-sided third nerve palsy (incomplete but there
is a history of a squint) and left-sided hemiparesis, which was
already showing signs of improvement. These findings may
suggest lesion at the level of the brainstem, specifically the
third nerve motor nucleus, and also the Edinger-Westphal
nucleus responsible for the pupillary light reflex (midbrain
involvement). However, the presence of cognitive impairment
indicates possible cortical involvement.
The improvement of hemiparesis raises the possibility of
Todd’s paralysis following an epileptic seizure, with the confusion
being post-ictal in nature. However no seizure activity
was reported and CK and lactate levels were normal. The
lack of diplopia despite visible EOM impairment can be
explained by pre-existing amblyopia.
Infectious encephalitis or meningitis should be considered
as an obvious possibility on the differential diagnoses list.
Other pathological processes in the brainstem or supratentorial
region, such as neoplasms, should also be suspected. A CT
scan of the head was unremarkable, making stroke less likely
given the presence of prodromal symptoms and the patient’s
lack of risk factors. As a result, we have requested an MRI of
the brain and a lumbar puncture (LP) for further evaluation
(Figs.!18.2 and 18.3).

"""
analytical_examinations = generate_analytical_localizations()
pathophysiology = generate_pathophysiologies()
print(generate_next_treatments(test))
