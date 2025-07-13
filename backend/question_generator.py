import openai
import os

def generate_questions(doc_chunks, num_questions=3):
    # Use the first N chunks as context for question generation
    context = "\n---\n".join([c['text'] for c in doc_chunks[:5]])
    prompt = f"Read the following document context and generate {num_questions} logic-based, reasoning questions that require inference. For each, provide:\n1. The question\n2. The reference answer\n3. The supporting evidence (snippet)\n4. The location (page/paragraph)\n\nContext:\n{context}\n\nFormat:\nQ: ...\nA: ...\nEvidence: ...\nLocation: ...\n---\n"
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a careful tutor. Only generate questions and answers grounded in the provided context."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.5
    )
    content = response.choices[0].message.content
    # Parse the output into a list of dicts
    questions = []
    for block in content.split('---'):
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) >= 4:
            q = lines[0][2:].strip() if lines[0].startswith('Q:') else lines[0]
            a = lines[1][2:].strip() if lines[1].startswith('A:') else lines[1]
            evidence = lines[2][9:].strip() if lines[2].startswith('Evidence:') else lines[2]
            location = lines[3][9:].strip() if lines[3].startswith('Location:') else lines[3]
            questions.append({
                'question': q,
                'reference_answer': a,
                'evidence': evidence,
                'location': location
            })
    return questions[:num_questions]
