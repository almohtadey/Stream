import streamlit as st
import pandas as pd
import openai
import requests
from io import BytesIO

# Set your API key and base URL for DeepSeek
openai.api_key = "sk-514baa52c5b74ec4a17730a962cee049"  # Replace with your actual API key
openai.api_base = "https://api.deepseek.com"  # Set the DeepSeek API base URL

# Load the Excel file from GitHub URL
def load_data_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        file_data = BytesIO(response.content)
        data = pd.read_excel(file_data)

        # Create a simpler summary
        summary = pd.DataFrame({
            "Feature": data.columns,
            "Non-Null Count": data.notnull().sum().values,
            "Missing Count": data.isnull().sum().values,
            "Unique Count": data.nunique().values,
            "Data Type": data.dtypes.values
        })
        total_rows = data.shape[0]
        total_columns = data.shape[1]
        summary_text = f"Total Rows: {total_rows}\nTotal Columns: {total_columns}"
        return data, summary, summary_text
    except Exception as e:
        return None, None, f"Error loading file: {str(e)}"

# Streamlit interface
st.title("Interactive Chat with Your Data")
st.subheader("Created by: Almohtadey")

# GitHub URL to the Excel file
github_excel_url = "https://raw.githubusercontent.com/almohtadey/Stream/main/Final%20Supplier%20Data%20with%20Trust.xlsx"

# Load data
data, summary, summary_text = load_data_from_github(github_excel_url)

if data is not None:
    st.write("### Data Summary:")
    st.text(summary_text)
    st.dataframe(summary)  # Display the summary as a table

    # Chat interface
    st.write("### Ask Questions About Your Data")
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Here is the summary of the data:\n{summary.to_string()}"},
        ]

    # User input
    user_input = st.text_input("Your Question:", "")

    if st.button("Send") and user_input.strip():
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get response from the model
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",  # Use the DeepSeek model name
                messages=st.session_state.messages,
            )
            assistant_message = response['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})

            # Display the latest question and answer
            st.write(f"**You:** {user_input}")
            st.write(f"**Assistant:** {assistant_message}")
        except Exception as e:
            st.error(f"Error communicating with the model: {str(e)}")
else:
    st.error(summary_text or "Failed to load data. Please check the file URL or format.")
