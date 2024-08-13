from huggingface_hub import InferenceClient
from api_keys import ai_key

client = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token=ai_key,
)


def get_course_recommendations(QA_res, available_courses):
    global client

    recommended_courses = ""

    for message in client.chat_completion(
            messages=[{"role": "user", "content": f"""You only answer in the format ["courses to learn1", "course to learn2"... ]
                Based off the answers for the below questions,
                which of these topics should the user learn {available_courses}.
                This is in the perspective of the user for your context\n"""+QA_res}],
            max_tokens=500,
            stream=True,
    ):
        recommended_courses += (message.choices[0].delta.content)

    print(recommended_courses)
    print(eval(recommended_courses))

    return eval(recommended_courses)


def generate_description(course_name):
    global client
    for message in client.chat_completion(
            messages=[{"role": "user", "content": f"""Generate a description for a video whose title is {
                course_name}"""}],
            max_tokens=500,
            stream=True,
    ):
        description += (message.choices[0].delta.content)

    return description

# print(output)


def generate_course_overview(question):
    # Generate a brief overview for the question using the LLM
    prompt = f"Provide a brief overview of the topic (your entire response should be In about 15 words)[!DONT SAY ANYTHING ELSE!]: {question}"
    overview = ""
    for message in client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        stream=True,
    ):
        overview += message.choices[0].delta.content
    return overview


def fetch_relevant_video(question):
    # Simulate fetching a relevant video for the course
    prompt = f"Find a YouTube video link that best explains, The video link should be of the format https://www.youtube.com/watch?v=[video_code]: {question}"
    video_link = ""
    for message in client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        stream=True,
    ):
        video_link += message.choices[0].delta.content
    return video_link


def create_custom_course(question, user_id, db):
    # Generate the overview
    overview = generate_course_overview(question)
    # Fetch a relevant video
    video_link = fetch_relevant_video(question)

    # Create a course dictionary
    course_title = question.title()  # Use the question as the title
    new_course = {
        "title": course_title,
        "description": overview,
        "type": "video",
        "link": video_link
    }

    # Update user's enrolled courses in the database
    user_data = db.child("users").child(user_id).get().val()
    enrolled_courses = user_data.get('enrolled_courses', [])
    enrolled_courses.append(new_course)
    db.child("users").child(user_id).update({
        'enrolled_courses': enrolled_courses
    })

    return new_course

def is_finance_related(topic):
    global client
    
    # Use the AI model to assess if the topic is finance-related
    prompt = f"Is the following topic related to finance? Answer with 'Yes' or 'No': {topic}"
    response = ""

    for message in client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        stream=True,
    ):
        response += message.choices[0].delta.content.strip()

    # Assuming the AI will respond with "Yes" or "No"
    return response.lower() == "yes"

def is_asking_to_create_course(user_input):
    global client
    
    # Use the AI model to assess if the user is asking to create a course
    prompt = f"Is the user asking to create a course in the following statement? Answer with 'Yes' or 'No': {user_input}"
    response = ""

    for message in client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        stream=True,
    ):
        response += message.choices[0].delta.content.strip()

    # Assuming the AI will respond with "Yes" or "No"
    return response.lower() == "yes"

def generate_teaching_response(question):
    global client
    response = ""
    
    prompt = f"Answer the following question in detail as if you are teaching finance to a beginner: {question}"
    
    for message in client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        stream=True,
    ):
        response += message.choices[0].delta.content
    
    return response
