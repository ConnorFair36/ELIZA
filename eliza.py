import re
from queue import PriorityQueue

# stores the keywords along with their rank level, patterns and responce transformations
keywords = {
    "tired": ([[r"(\w+ )*tired", "Why are you tired?"]], 1)
}

# A priority queue that keeps track of all identified and unused keywords with words of higher rank going first
found_kw = PriorityQueue()

def clean_input(user_input: str) -> str:
    """Cleans the user input text for easier processing."""
    return user_input.lower()

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
            if re.match(pattern, user_input) != None:
                return transform_input(user_input, transformation)
        # if there were no matches, try again with the next keyword
        return generate_response(user_input)
    else:
        return default_response()

# TODO Add transform logic
def transform_input(user_input: str, transformation: str) -> str:
    return transformation

def clear_queue() -> None:
    """Clears the entire priority queue."""
    # Loops throught the entire priority queue to remove everything
    while not found_kw.empty():
        found_kw.get()

def main():
    print("Hello from eliza!")
    # main ELIZA loop
    while True:
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
        print(generate_response(user_input))
        #print(found_kw.queue)
        # clear the queue for the next input
        clear_queue()


if __name__ == "__main__":
    main()
