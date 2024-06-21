import os
import random
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore
import subprocess
import black

load_dotenv()

client = OpenAI(organization=os.environ.get("OPENAI_ORGANIZATION"), api_key=os.environ.get("OPENAI_API_KEY"))

PROGRAMS_LIST = [
'''Given two strings str1 and str2, prints all interleavings of the given
two strings. You may assume that all characters in both strings are
different.Input: str1 = "AB", str2 = "CD"
Output:
ABCD
ACBD
ACDB
CABD
CADB
CDAB
Input: str1 = "AB", str2 = "C"
Output:
ABC
ACB
CAB "''',
"A program that checks if a number is a palindrome",
"A program that finds the kth smallest element in a given binary search tree",
"A program that gets number and check if it is prime",
"A program that calculate the GCD of two numbers"]

def code_from_openai(request):
    chat_completion = client.chat.completions.create(
        messages=
        [
            {
              "role": "system",
              "content": "You are a python developer, You can create any python program without unnecessary text."
                         "DO THE UNIT TESTS WITH ASSERTS!!"
                         "DO NOT write any explanations and NOT add any text."
                         "START AND END THE CODE WITH @@D"
                         "DO THE UNIT TESTS WITH ASSERTS!!"
                         "SHOW THE CODE ITSELF."
                         "Again, START and END the CODE with @@D."
                         "Again, DO THE UNIT TESTS WITH ASSERTS!!"
            },
            {
                "role": "user",
                "content": "Hi, can you create a python program?"
                           "DO THE UNIT TESTS WITH ASSERTS!!"
                           "any code without any addition."
                           "START AND END THE CODE WITH @@D"
                           "DO THE UNIT TESTS WITH ASSERTS!!"
                           "include unit tests that check the logic of the program using 5 different inputs and expected outputs."
                           "START AND END THE CODE WITH @@D"
                           "DO THE UNIT TESTS WITH ASSERTS!!"
            },
            {
                "role": "user",
                "content": request
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content.split("@@D")[1]

def get_program():
    user_input = input("Tell me, which program would you like me to code for you? If you don't have "
                       "an idea,just press enter and I will choose a random program to code:").strip()
    if not user_input:
        user_request = random.choice(PROGRAMS_LIST)
    else:
        user_request = user_input

    return user_request

program = get_program()
errors = []
run_code = ""
checker = False
for i in range(5):
    if errors:
        request = f"{Fore.CYAN}DO THE UNIT TESTS with ASSERTS!!!\n{Fore.RESET}" \
                  f"{Fore.YELLOW}I have an error, this is the error: {errors[-1]}\n\n This is the code that i ran: {run_code}\n\nPlease show me the whole code fixed as I have these errors.\n{Fore.RESET}" \
                  f"{Fore.CYAN}START and END the code with @@D, DO THE UNIT TESTS WITH ASSERTS!!!{Fore.RESET}"
    else:
        request = f"{Fore.CYAN}DO THE UNIT TESTS with ASSERTS!!!\n{Fore.RESET}" \
                  f"{Fore.YELLOW}write {program}.\n{Fore.RESET}" \
                  f"{Fore.CYAN}START and END the code with @@D, DO THE UNIT TESTS with ASSERTS!!!.{Fore.RESET}"

    print(request)
    run_code = code_from_openai(request)
    print(f"{Fore.BLUE}The Code from OpenAI:\n{run_code}{Fore.RESET}")
    file_name = "code_generate.py"
    with open(file_name, "w") as file:
        file.write(run_code)
    result = subprocess.run(["python", "code_generate.py"], capture_output=True)
    if result.returncode == 0:
        print(f"{Fore.GREEN}Code creation completed successfully !{Fore.RESET}")
        formatted_code = black.format_file_contents(run_code, fast=False, mode=black.FileMode())
        with open(file_name, "w") as file:
            file.write(formatted_code)
        checker = True
        os.startfile("code_generate.py")
        break
    else:
        errors.append(result.stderr)
        print(f"{Fore.RED}Error running generated code! Error: {errors[-1]}{Fore.RESET}")
        os.remove(file_name)

if not checker:
    print(f"{Fore.RED}Code generation FAILED{Fore.RESET}")
