import os
import pandas as pd
import requests
import time
import redis
from gpt4all import GPT4All
from dotenv import load_dotenv
from colorama import Fore

load_dotenv()
wolfram_app_key = os.environ.get("WOLFRAM_ALPHA_API_KEY")

mini_orca_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

# The Model for checking the Correctness.
instruct_model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")

print(f"{Fore.YELLOW}Welcome to compare answers of ai models{Fore.RESET}")

# Function that compute the correctness of the answer according to instruct model
def check_correctness(model_answer, wolframalpha_answer):
    if wolframalpha_answer == "Wolfram|Alpha did not understand the question" or wolframalpha_answer.decode() == "Wolfram|Alpha did not understand the question":
        return 0

    prompt = f"""You are a answer similarity machine. DON'T ANSWER THE QUESTION. Rate the similarity between the two following phrases on a scale from 0.0 (not similer) to 1.0 (identical).
                    phrase1: {model_answer} 
                    phrase2: {wolframalpha_answer}
                    The similarity between the two phrases are: """

    output = instruct_model.generate(prompt, max_tokens=15)
    try:
        correctness_grade = float(output.split()[0])
        return min(max(correctness_grade, 0.0), 1.0)
    except ValueError:
        # If the model output is not a valid number
        return 0.0

# Read the Questions
df = pd.read_csv('General_Knowledge_Questions.csv')

r = redis.Redis()
wolframalpha_answers = []

for question in df['Question']:
    answer = r.get(question)
    if answer is None:
      response = requests.get(f'https://api.wolframalpha.com/v1/result?i={question.replace(" ", "+")}&appid={wolfram_app_key}')
      answer = response.text

      r.set(question, answer)
      r.expire(question, 14400)

    wolframalpha_answers.append(answer)

df['WolframAlpha_Answer'] = wolframalpha_answers
mini_orca_answers = []
instruct_answers = []
counter = 0

for question in df['Question']:
    counter += 1
    print(f"{Fore.GREEN}" + str(counter) + ". " + question + f"{Fore.RESET}")

    # Mini Orca Model Answer
    time_start = time.time()
    mini_orca_answer = mini_orca_model.generate(f"###User:Just Answer that question- {question} \n###Assistant", max_tokens=25)
    time_end = time.time()
    mini_orca_answer = mini_orca_answer.strip(":").replace("\n", "")
    print(f"{Fore.MAGENTA}Mini Orca Model Answer: {mini_orca_answer}{Fore.RESET}")
    corectness_model_mini_orca = check_correctness(mini_orca_answer, df.loc[df['Question'] == question, 'WolframAlpha_Answer'].iloc[0])
    mini_orca_answers.append({'Question': question,
                              'Model': 'orca-mini-3b-gguf2-q4_0.gguf',
                              'Answer': mini_orca_answer,
                              'TimeInMillisecondsToGetAnswer': time_end - time_start,
                              'Correctness': corectness_model_mini_orca})

    # Instruct Model Answer
    time_start = time.time()
    instruct_answer = instruct_model.generate(f"{question}", max_tokens=25)
    time_end = time.time()
    instruct_answer = instruct_answer.strip(":").replace("\n", "")
    print(f"{Fore.BLUE}Instruct Model Answer: {instruct_answer}{Fore.RESET}")
    corectness_model_instruct = check_correctness(instruct_answer, df.loc[df['Question'] == question, 'WolframAlpha_Answer'].iloc[0])
    instruct_answers.append({'Question': question,
                           'Model': 'mistral-7b-instruct-v0.1.Q4_0.gguf',
                           'Answer': instruct_answer,
                           'TimeInMillisecondsToGetAnswer': time_end - time_start,
                           'Correctness': corectness_model_instruct})
    if counter % 5 == 0:
        # print(f"Processed {counter} questions")
        break


# Compute the number of Answers from WolframAlpha
try:
    wolframalpha_answered_count = df['WolframAlpha_Answer'].apply(lambda x: 'Wolfram|Alpha' not in x).sum()
except:
    wolframalpha_answered_count = df['WolframAlpha_Answer'].apply(lambda x: 'Wolfram|Alpha' not in x.decode()).sum()

# Compute average answer ratings for each model
sum_mini_orca = pd.DataFrame(mini_orca_answers)['Correctness'].sum()
sum_instruct = pd.DataFrame(instruct_answers)['Correctness'].sum()

# Finding the lowest rated question and answer for each model
lowest_rated_mini_orca = min(mini_orca_answers, key=lambda x: x['Correctness'])
lowest_rated_instruct = min(instruct_answers, key=lambda x: x['Correctness'])

# Print the results
print(f"\n{Fore.YELLOW}Number of questions that WolframAlpha answered: {wolframalpha_answered_count}{Fore.RESET}")
print(f"{Fore.MAGENTA}Average answer rating of 'orca-mini-3b-gguf2-q4_0': {(sum_mini_orca/wolframalpha_answered_count):.5f}{Fore.RESET}")
print(f"{Fore.BLUE}Average answer rating of 'mistral-7b-instruct-v0.1.Q4_0.gguf': {(sum_instruct/wolframalpha_answered_count):.5f}{Fore.RESET}")
print(f"{Fore.MAGENTA}Lowest rating question of 'mini_orca': {lowest_rated_mini_orca['Question']}")
print(f"{Fore.MAGENTA}The answer for it is: " + lowest_rated_mini_orca['Answer'] + f"{Fore.RESET}")
print(f"{Fore.BLUE}Lowest rating question of 'instruct': {lowest_rated_instruct['Question']}{Fore.RESET}")
print(f"{Fore.BLUE}The answer for it is: " + lowest_rated_instruct['Answer'] + f"{Fore.RESET}")





