import re

def clean_output(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#+\s', '', text)
    text = re.sub(r'`+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\n---\n', ' ', text)
    
    return text.strip()

def extract_actions_with_tools(input_text: str) -> str:
    pattern = r"Action:\s*(.*?)\s*- Reasoning:.*?Tool Used:\s*(.*?)\s*- Output:"
    matches = re.findall(pattern, input_text, re.DOTALL)

    result_lines = []
    for idx, (action, tool) in enumerate(matches, start=1):
        action_clean = ' '.join(action.split())
        tool_clean = ' '.join(tool.split())
        result_lines.append(f"{idx}. {action_clean} using {tool_clean}")
    result = ''.join(result_lines)
    return result