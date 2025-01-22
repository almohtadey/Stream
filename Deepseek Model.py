import streamlit as st
import pandas as pd
import openai

# Set your API key and base URL for DeepSeek
openai.api_key = "sk-514baa52c5b74ec4a17730a962cee049"  # Replace with your actual API key
openai.api_base = "https://api.deepseek.com"  # Set the DeepSeek API base URL

# Load the Excel file and prepare context
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_excel(file_path)
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
        return None, None, f"Error loading file: {e}"

# Streamlit interface
st.title("Interactive Chat with Your Data")
st.subheader("Made by : Almohtadey.")

uploaded_file = st.file_uploader("Upload an Excel File", type=["xlsx", "xls"])

if uploaded_file:
    data, summary, summary_text = load_data(uploaded_file)
    if data is not None:
        st.write("### Data Summary:")
        st.text(summary_text)
        st.dataframe(summary)  # Display the simpler summary as a table

        # Add a collapsible button in the sidebar to view the data table
        with st.sidebar:
            show_table = st.button("View Full Data Table")

        # If the button is clicked, display the data table with an expander
        if show_table:
            with st.expander("Full Data Table (Click to Collapse)", expanded=True):
                st.dataframe(data)

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

                # Only show the latest question and answer
                st.session_state.latest_question = user_input
                st.session_state.latest_response = assistant_message
            except Exception as e:
                assistant_message = f"Error: {e}"
                st.session_state.latest_question = user_input
                st.session_state.latest_response = assistant_message

        # Display only the latest question and response
        if "latest_question" in st.session_state and "latest_response" in st.session_state:
            st.write(f"**You:** {st.session_state.latest_question}")
            st.write(f"**Assistant:** {st.session_state.latest_response}")
    else:
        st.error(summary_text)
else:
    st.info("Please upload an Excel file to start.")
