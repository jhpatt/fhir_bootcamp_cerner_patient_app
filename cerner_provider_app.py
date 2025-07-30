import streamlit as st
import requests
import secrets
from urllib.parse import urlencode

# --- Configuration ---
CLIENT_ID = "11c867a3-5c5a-4857-9835-ca22859e7882"
REDIRECT_URI = "http://localhost:8501/"
SCOPES = "launch openid fhirUser profile user/Patient.read user/Patient.write user/Observation.read user/Observation.write"

# --- Functions ---
def get_smart_configuration(iss_url: str) -> dict | None:
    """Fetches the SMART configuration from the server."""
    if not iss_url:
        st.error("Error: ISS URL is empty.")
        return None
    well_known_url = f"{iss_url.rstrip('/')}/.well-known/smart-configuration"
    try:
        response = requests.get(well_known_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching SMART configuration: {e}")
        return None

# --- Main App Logic ---
st.set_page_config(page_title="SMART on FHIR Launch App")
st.title("SMART App Launch Helper")

params = st.query_params

# Step 3: Handle the callback from the authorization server
if "code" in params and "state" in params:
    st.header("Authorization Callback Received")
    
    if st.session_state.get("state") != params.get("state"):
        st.error("State mismatch! This could be a security risk. Please try launching the app again.")
        st.write("Expected state:", st.session_state.get("state"))
        st.write("Received state:", params.get("state"))
    else:
        st.success("State verified successfully! ✅")
        st.write("Received Authorization Code:")
        st.code(params.get("code"), language=None)
        st.info("The next step is to exchange this code for an access token.")

# Step 1: Handle the initial launch from the EHR (Corrected Condition)
elif "iss" in params and "launch" in params and "iss" not in st.session_state:
    st.session_state.clear() 
    st.session_state.iss = params["iss"]
    st.session_state.launch = params["launch"]
    st.rerun()

# Step 2: Fetch config and show the login button
elif "iss" in st.session_state:
    st.success("Launch parameters received!")
    smart_config = get_smart_configuration(st.session_state.iss)
    
    if smart_config and "authorization_endpoint" in smart_config:
        auth_endpoint = smart_config["authorization_endpoint"]
        
        if "state" not in st.session_state:
            st.session_state.state = secrets.token_urlsafe(32)

        auth_params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "launch": st.session_state.launch,
            "state": st.session_state.state,
            "aud": st.session_state.iss,
        }
        full_auth_url = f"{auth_endpoint}?{urlencode(auth_params)}"

        st.info("Click the button below to authorize the application.")
        st.link_button("Login to EHR and Authorize App", url=full_auth_url)
    else:
        st.error("Could not fetch server configuration. Halting.")

# Default case: Waiting for launch
else:
    st.warning("Waiting for EHR launch.")




# ### --- setting the config parameters --- ###
# config = {
#     'app_id': '111c867a3-5c5a-4857-9835-ca22859e7882',
#     'api_base': 'https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d',
#     'redirect_uri': 'http://localhost:8501',
#     'scope': 'openid fhirUser launch user/Patient.crus user/Observation.crus user/Observation.write'
# }

# ### --- defining function for authentication --- ###

# def cerner_auth():
#     auth_url_base = 'https://authorization.cerner.com/tenants/ec2458f2-1e24-41c8-b71b-0e701af7583d/protocols/oauth2/profiles/smart-v1/personas/provider/authorize'
#     aud_url = 'https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d'
#     launch_id = 'launch=97c39702-180e-436e-bb82-8657c1faa6e4'

#     full_auth_url = f'{auth_url_base}?{aud_url}{launch_id}'

#     params = {
#         'response_type': 'code',
#         'client_id': config['app_id'],
#         'redirect_uri': config['redirect_uri'],
#         'scope': config['scope'],
#         'state': '12345',  # Should be a unique, unguessable value in a real app
#     }
#     # URL encode the parameters
#     auth_url = requests.Request('GET', full_auth_url, params=params).prepare().url
#     return auth_url

# ### --- defining a function for token exchange --- ###
# def token_exchange(authorization_code):
#     token_url = "https://authorization.cerner.com/tenants/ec2458f2-1e24-41c8-b71b-0e701af7583d/hosts/fhir-ehr-code.cerner.com/protocols/oauth2/profiles/smart-v1/token"
#     payload = {
#         'grant_type': 'authorization_code',
#         'code': authorization_code,
#         'redirect_uri': config['redirect_uri'],
#         'client_id': config['app_id'],
#     }

#     try:
#         response = requests.post(token_url, data=payload)
#         response.raise_for_status()  
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error exchanging authorization code for access token: {e}")
#         st.error(f"Response content: {response.text}")
#         return None
