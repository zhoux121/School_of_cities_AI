import tiktoken

# Check how many tokens
def num_tokens_from_string(string: str, encoding_name: str):
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def read_string_from_txt(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()
file_name = r'C:\Users\zxx91\Desktop\School of Cities AI\hamilton\hamilton_PDF_extracted_content.txt'
text_content = read_string_from_txt(file_name)

print(num_tokens_from_string(text_content, "cl100k_base"))

