import openai
import os

def grade_answers(user_answers, reference_answers, evidences, locations):
    client = openai.OpenAI()
    results = []
    for user_ans, ref_ans, evidence, location in zip(user_answers, reference_answers, evidences, locations):
        prompt = f"Reference answer: {ref_ans}\nUser answer: {user_ans}\n\nGrade the user answer as 'correct', 'partially correct', or 'incorrect'. Justify your grading with reference to the evidence.\nEvidence: {evidence}\nLocation: {location}\n\nFormat:\nGrade: ...\nFeedback: ..."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strict but fair grader. Only use the provided evidence."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2
        )
        content = response.choices[0].message.content
        # Parse grade and feedback
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        grade = 'incorrect'
        feedback = ''
        for line in lines:
            if line.lower().startswith('grade:'):
                grade = line.split(':', 1)[-1].strip().lower()
            elif line.lower().startswith('feedback:'):
                feedback = line.split(':', 1)[-1].strip()
        results.append({
            'grade': grade,
            'feedback': feedback,
            'evidence': evidence,
            'location': location
        })
    return results
