import streamlit as st
import requests
import urllib.parse
import pandas as pd
import json

st.title("🛰 OlaParty Fucked BY Malone !")

# --- Input fields
vid = st.text_input("Enter VID (User ID):")
auth_token ='PWAi4owfZn5m5tDhifoYEQ%2BCyzEYZKPCAwdB8QtELq4lU6eWjT6gGTuJ%2F6SCNqrJ%2CnNM9ovMxw6%2FHgsKdoqKhs8f%2FPJarf6tVP4i14x%2BpyKvK7yXUMTWLLER7qLfHdiv%2Fjgrm3OFlH7uVekRSeEcdQFP7IFcrOJTh9x6%2B7Ck2jbBQ3a6B645L7zNkL57XGX9exl%2FAOQ16Nk0MZz65AgkGDS8AIug4pU2ey%2BPn03E3fk8CHiQqINYbczZ4%2BtLA6dIObEHfMKPWmFm2Ey8gfbl7sXWxd8ReEOPKWBsn5KPHLM98GOnUVmQmb3agmhFQ2BAWBQFGD4gkzN%2FlmLhYgV2S67Oyoa9Bo0APBiH9hZG7yWZ9ruib0relKA6l7aJhD9GewNO723BzgQ%2B37d%2BijRfbDlcMa8q9vwr3y8f80DxWduwFxG0xEN1qzllKbnqR%2B%2Br7Tmv8ZhIkGG0cxjNu2es0bNSU%2BoZe4pQ%2BcGE9ApvCthgkpPVAX8KbDQDNGWXHOkbP%2F2QuCxyYXIh1IOGptwNtjAof5APHrZABqkF8R3Qj%2FmLcxFMkSN7%2FO%2BHbjyibRh%2FX'

# --- Button
if st.button("Fetch Full Info"):
    if not vid or not auth_token:
        st.error("⚠️ Please enter both VID and Auth Token.")
    else:
        try:
            # -------------------------------
            # Step 1: Get UID from VID
            # -------------------------------
            query = {"nick": vid, "from": 0, "size": 10}
            encoded_data = urllib.parse.quote(json.dumps(query))
            search_url = f"https://i-875.olaparty.com/ikxd_search/friend_list?data={encoded_data}"

            headers = {
                "Host": "i-875.olaparty.com",
                "X-Cpuarch": "arm_32",
                "X-Devicetype": "OnePlus ONEPLUS A3010",
                "X-Sdk-Ver": "25",
                "X-Simciso": "in",
                "X-Client-Net": "1",
                "X-App-Lastver": "",
                "X-Lang": "en_in",
                "X-App-Ver": "32400",
                "X-Os-Ver": "7.1.1",
                "X-Auth-Token": auth_token,
                "X-Ostype": "android",
                "X-Deviceid": "79c05e3af59c7d66d62bc2e95deb5086",
                "User-Agent": "okhttp/3.12.1",
                "Accept-Encoding": "gzip, deflate, br",
            }

            resp1 = requests.get(search_url, headers=headers)
            data1 = resp1.json()

            if "data" not in data1 or "user_info" not in data1["data"]:
                st.warning("⚠️ No user found for this VID.")
            else:
                user_basic = data1["data"]["user_info"][0]
                uid = user_basic.get("uid")

                st.success(f"✅ UID Found: {uid}")

                # -------------------------------
                # Step 2: Get Full Info using UID
                # -------------------------------
                post_url = "https://i-875.olaparty.com/uinfo/get_uinfo_byver"
                payload = {"data": json.dumps({"uids": [{"uid": uid, "ver": 0}]})}

                headers_post = headers.copy()
                headers_post["Content-Type"] = "application/x-www-form-urlencoded"

                resp2 = requests.post(post_url, headers=headers_post, data=payload)
                data2 = resp2.json()

                # Debug info (optional)
                # st.json(data2)

                # Handle both possible response structures
                uinfo = None
                if "data" in data2:
                    if "uinfo" in data2["data"]:
                        uinfo = data2["data"]["uinfo"]
                    elif "user_info" in data2["data"]:
                        uinfo = data2["data"]["user_info"]

                # -------------------------------
                # Step 3: Display results
                # -------------------------------
                if uinfo:
                    user_full = uinfo[0]

                    if "avatar" in user_full:
                        st.image(user_full["avatar"], caption="User Avatar", width=150)

                    st.subheader("📋 Full User Information")
                    df = pd.DataFrame(user_full.items(), columns=["Field", "Value"])
                    st.dataframe(df, use_container_width=True)

                    # --- Download CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="💾 Download as CSV",
                        data=csv,
                        file_name=f"user_{uid}_info.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("⚠️ Full user info not available (check auth token or permissions).")

        except Exception as e:
            st.error(f"❌ Error: {e}")
