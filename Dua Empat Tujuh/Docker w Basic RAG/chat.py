from qdrant import qdrant_retrieve
from google.genai import Client, types

input = "What is 2+2?"

def rag_chat(input):

    retrieved_points = qdrant_retrieve(input)

    retrieved_text = retrieved_points.points[0].payload['text']

    google_client = Client(api_key='AIzaSyAguG6uHe228b1GmdGWL5cbJ0QRcCaZY_E')

    response = google_client.models.generate_content(
        model='gemini-2.5-flash',
        contents={'text': f'{input} If it is relevant, use the information here to answer: {retrieved_text}'},
        config={
            'temperature': 0,
            'top_p': 0.95,
            'top_k': 20,
        },
    )

    return response.candidates[0].content.parts[0].text