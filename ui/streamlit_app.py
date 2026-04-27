"""Small Streamlit UI for the AI Request Monitor API."""

import httpx
import streamlit as st


st.set_page_config(page_title="AI Request Monitor", page_icon=":shield:", layout="centered")

st.title("AI Request Monitor")
st.write("Submit a prompt to the FastAPI `/analyze` endpoint.")

backend_url = st.sidebar.text_input(
    "Backend URL",
    value="http://127.0.0.1:8000",
)

prompt = st.text_area("Prompt", height=180, placeholder="Enter a prompt to analyze...")

if st.button("Analyze", type="primary"):
    if not prompt.strip():
        st.warning("Enter a prompt before submitting.")
    else:
        api_url = f"{backend_url.rstrip('/')}/analyze"

        try:
            response = httpx.post(api_url, json={"prompt": prompt}, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        except httpx.RequestError:
            st.error("Could not reach the backend. Make sure the FastAPI server is running.")
        except httpx.HTTPStatusError as exc:
            st.error(f"Backend returned an error: {exc.response.status_code}")
        else:
            st.subheader("Result")
            st.write(f"**Risk Score:** {data['risk_score']}")
            st.write(f"**Is Malicious:** {data['is_malicious']}")
            st.write(f"**Timestamp:** {data['timestamp']}")

            st.write("**Reasons:**")
            if data["reasons"]:
                for reason in data["reasons"]:
                    st.write(f"- {reason}")
            else:
                st.write("No suspicious patterns detected.")
