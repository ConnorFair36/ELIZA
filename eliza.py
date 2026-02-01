import re
from queue import PriorityQueue

username = ""

# stores the keywords in the following format:
#   "keyword" : ([["pattern 1", "transformation or response 1"],
#                  "patten 2",  "transformation or response 2"], rank)
# things to note about adding keywords:
# - lower rank means higher priority
# - patterns are choosen by the order they are put in, not by best-fit
keywords = {
    # A
    "are": ([[r"the ((?:\w+\s)*)are ((?:\w+\s)*\w+)", "Why do you think the @0are @1?"]], 2),
    # B
    "boss": ([[r"((?:\w+\s)*)(thinking|talking) about my boss ((?:\w+\s)*\w+)", "Tell me about your boss"]], 0),
    # E
    "everyone": ([[r"((?:\w+\s)*)everyone ((?:\w+\s)*)", "When you say that, who are you thinking of in particular?"]], 1),
    "everything": ([[r"((?:\w+\s)*)everything ((?:\w+\s)*)", "When you say that, what are you thinking of in particular?"]], 1),
    # F
    "feeling": ([[r"((?:\w+\s)*)feeling ((?:\w+\s)*\w+)", "Why are you feeling @1?"]], 1),
    "family": ([[r"((?:\w+\s)*)family ((?:\w+\s)*\w+)", "Tell me about your family"]], 0),
    "falling": ([[r"((?:\w+\s)*)you are falling short ((?:\w+\s)*\w+)", "How are you falling short?"]], 0),
    # I
    "i": ([[r"i think i am ((?:\w+\s)*\w+)", "Why do you think I'm @0?"]], 1),
    # L
    "like": ([[r"((?:\w+\s)*)not like ((?:\w+\s*)*)", "Why don't you like @1?"],
              [r"((?:\w+\s)*)like ((?:\w+\s*)*)", "Why do you like @1?"]], 2),
    "zebra": ([[r"((?:\w+\s)*)zebra", "ZEBRAS?!?! I LOVE ZEBRAS!!!! HAHAHAHAHA\n\n\nSorry about that...\nPlease continue"]], -1),
    # N
    "nothing": ([[r"((?:\w+\s)*)nothing ((?:\w+\s)*)", "When you say that, what are you thinking of in particular?"]], 1),
    # O
    "one": ([[r"((?:\w+\s)*)no one ((?:\w+\s)*)", "When you say that, who are you thinking of in particular?"]], 1),
    # S
    "stop": ([[r"stop", "If you are looking to end the program, type end"]], 1),
    # T
    "thanks": ([[r"no thanks", "Why not?"],
                r"((?:\w+\s)*)thanks", "Of course!"], 1),
    # Y
    "you": ([[r"((?:\w+\s)*)you are ((?:\w+\s)*\w+)", "Why do you think you are @1?"]], 1),
    
}

# A priority queue that keeps track of all identified and unused keywords with words of higher rank going first
found_kw = PriorityQueue()

def get_username() -> str:
    """Gets and saves the username."""
    print("Hey there, this is Eliza, your local chatbot therapist!\nWhat is your name?")
    while True:
        # get the username from the user
        user_input = input()
        user_input = re.sub("[Hh]ey |[Hh]i |[Hh]ello |[Hh]ey, |[Hh]i, |[Hh]ello, ", "", user_input)
        user_input = re.sub("[Mm]y name is ", "", user_input)
        if re.match("[A-Z][a-z]*", user_input):
            username = re.match(r"(?:\w+)", user_input).group(0)
            break
        print("Please enter your name using only alphabetical characters")
    # if the user gave an immediate response, extract it and send it off to the main loop.
    user_input = re.sub(username, "", user_input)
    user_input =  re.sub(r"[,.?!]", "", user_input)
    if user_input == "":
        print(f"Thanks {username}!\nHow are you today?")
    return user_input.strip()

    

def clean_input(user_input: str) -> str:
    """Cleans the user input text for easier processing."""
    user_input = user_input.lower()
    # clean up punctuation
    # remove punctuation
    user_input = re.sub(r"[.,?!-]", "", user_input)
    user_input = user_input.replace("’", "'")

    # expand all contracted words
    # add some space padding to help make substituting easier (every individual word should always have a space before and afer it)
    user_input = " " + user_input + " "
    user_input = user_input.replace("i'm", "i am")
    user_input = user_input.replace("'re", " are")
    user_input = user_input.replace("let's", "let us")
    user_input = user_input.replace("'s", " is")
    user_input = user_input.replace("'ve", " have")
    user_input = user_input.replace("'d", " did")
    user_input = user_input.replace("'ll", " will")
    user_input = user_input.replace("n't", " not")
    user_input = user_input.replace("gonna", "going to")
    user_input = user_input.replace("wanna", "want to")
    user_input = user_input.replace("'bout", "about")
    user_input = user_input.replace("'cause", "because")
    # swap  i and you for easier processing later
    user_input = user_input.replace(" you ", " _i ")         # placeholders for i and i am
    user_input = user_input.replace(" you are ", " _i _am ")
    user_input = user_input.replace(" i am ", " you are ") # replace i and i am with you and you are
    user_input = user_input.replace(" i ", " you ")
    user_input = user_input.replace(" _i ", " i ")          # bring back i and i am

    # other important word transformations
    user_input = user_input.replace("'zebras", "zebra")
    return user_input.strip()

def extract_keywords(user_input: str) -> list[str]:
    """Check user input for keywords and return them in the order the are found in."""
    found_kw = []
    for word in user_input.split(" "):
        if keywords.get(word, False):
            found_kw.append(word)
    return found_kw

def update_pq(user_kw: list[str]) -> None:
    """Adds all keywords to the priority queue and clears all previously stored ones."""
    for kw in user_kw:
        # get the rank associated with the keyword and put (rank, keword into the priority queue)
        rank = keywords[kw][1]
        found_kw.put((rank, kw))

def default_response() -> str:
    """Returns a default response not based on keywords"""
    return "Tell me more"

def generate_response(user_input: str) -> str:
    """Generates a response based on what is in the priority queue and the user's response."""
    if not found_kw.empty():
        # generate response if there is a keyword to work with
        kw = found_kw.get()[1]
        # get the pattern, transformation pairs for each keyword
        rules = keywords[kw][0]
        for pattern, transformation in rules:
            # check every pattern associated with the keyword
            pattern_match = re.match(pattern, user_input)
            if pattern_match != None:
                return transform_input(pattern_match.groups(), transformation)
        # if there were no matches, try again with the next keyword
        return generate_response(user_input)
    else:
        return default_response()

def transform_input(pattern_match: tuple, transformation: str) -> str:
    """Transforms the input message returned by the user"""
    response = transformation
    # modifies the response if the transformation requires it 
    if "@" in response:
        for i, phrase in enumerate(pattern_match):
            response = response.replace(f"@{i}", phrase)
    return response

def clear_queue() -> None:
    """Clears the entire priority queue."""
    # Loops throught the entire priority queue to remove everything
    while not found_kw.empty():
        found_kw.get()

def main():
    quickstart_input = get_username()
    # main ELIZA loop
    while True:
        if quickstart_input != "":
            user_input = quickstart_input
            quickstart_input = ""
        else: 
            user_input = input()
        user_input = clean_input(user_input)
        # end the program if user gives "end" as input
        if user_input == "end":
            break
        # identify all keywords
        user_kw = extract_keywords(user_input)
        # place keywords into priority queue
        update_pq(user_kw)
        # generate a response to the user's input
        print(found_kw.queue)
        print(generate_response(user_input))
        # clear the queue for the next input
        clear_queue()


if __name__ == "__main__":
    main()
