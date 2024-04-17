#FUNCTION TO DEAL WITH AI (SEND REQUEST / GET RESPONSE):D 
import ollama

def send_to_ai(text):
    requested= f"""
    Generate a concise , one paragraph summary of the text below.
    Text: {text}
    
    Add a title to the summary.

    Make sure your summary has useful and true information about the main points of the topic.
    Begin with a short introduction explaining the topic. If you can, use bullet points to list important details,
    and finish your summary with a concluding sentence
    """
    resp = ollama.generate(model='llama2',prompt=requested)
    summary=resp['response']
    return summary
