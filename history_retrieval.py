import json
import re
from typing import List, Literal, Optional

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

import os
from langchain.chat_models import init_chat_model

from models import NeurologyReport

llm = init_chat_model("openai:gpt-4.1")

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a neurology doctor and you should help the doctor to identify the required questions in the report.
            ake into consideration that the routine direct questions are as follows: 
            1.Have you noticed any change in your mood, memory or powers of concentration? 
            2.Have you ever lost consciousness or had a fit or seizure? 
            3.Do you suffer unduly from headaches? 
            4. Have you noticed any change in your senses: (i) smell; (ii) taste; (iii) sight; (iv) hearing? 
            5. Do you have any difficulty in talking, chewing or swallowing? 
            6. Have you ever experienced any numbness, tightness, pins and needles, tingling or burning sensation in the face, limbs or trunk? 
            7. Have you noticed any weakness, stiffness, heaviness or dragging of arms or legs? 
            8. Do you have any difficulty in using your hands for skilled tasks, such as writing, typing or dressing? 
            9. Do you have any unsteadiness or difficulty in walking? 
            10. Do you ever have any difficulty controlling your bladder or bowels?


             Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
            """
        ),
        ("human", "{query}"),
    ]
).partial(schema=NeurologyReport.model_json_schema())


# Custom parser
def extract_json(message: AIMessage) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between \`\`\`json and \`\`\` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    text = message.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"\`\`\`json(.*?)\`\`\`"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        raise ValueError(f"Failed to parse: {message}")


def generate_neurology_report(anamnesis:str):
    parser = PydanticOutputParser(pydantic_object=NeurologyReport)
    query = anamnesis
    chain = prompt | llm | parser
    report: NeurologyReport = chain.invoke({"query": query})
    return report


# def generate_anatomical_report(anamnesis:str):

# print(response)