from utils.email_generator import EmailGenerator

import streamlit as st

if __name__ == '__main__':
    gen = None
    st.title('H: Drive Management')
    with st.sidebar:
        st.title('Import Data')
        uploaded_file = st.file_uploader(
            'Upload excel spreadsheet',
            ['.xlsx']
        )
        if uploaded_file is not None:
            gen = EmailGenerator(uploaded_file)
            if st.button('Send Emails'):
                emails_to_send = gen.data.to_dict(orient='records')
                progress_bar = st.progress(0, "Emails being sent")
                total = len(emails_to_send)
                i = 1
                for email in emails_to_send:
                    progress_bar.progress(i/total, f"{i}/{total} - Email being sent to {email['Display Name']}")
                    gen.send_idir_email(email)
                    i += 1

    if gen is not None:
        col1, col2, col3 = st.columns(3)
        total_drives = gen.total_drives
        allowed_gb = total_drives * 1.5
        total_gb = round(gen.raw['Used (GB)'].sum())
        total_cost = round((total_gb - (total_drives * 1.5)) * 2.7, 2)
        average_gb = round(gen.raw['Used (GB)'].mean())
        count_over_threshold = gen.raw[gen.raw['Used (GB)'] > 1.5].shape[0]
        percent_over_threshold = round(float(count_over_threshold) / float(total_drives), 4) * 100
        with col1:
            st.metric('Total GB', total_gb, total_gb - allowed_gb, delta_color='inverse')
            st.metric('Average GB', average_gb)

        with col2:
            st.metric('Total Cost', total_cost)
            st.metric('Average Cost', round((average_gb - 1.5) * 2.7, 2) )

        with col3:
            st.metric('Count of Drives Above Threshold', count_over_threshold)
            st.metric('Percent of Drives Above Threshold', percent_over_threshold)


        st.dataframe(
            gen.data.sort_values(by=['Used (GB)'], ascending=False).head(10)
        )

