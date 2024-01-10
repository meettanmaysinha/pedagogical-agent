import streamlit as st
import tempfile
import os 
import batchuploader

def get_file_path(uploaded_file):
    '''Saves uploaded file to temporary directory and returns path for analysis'''
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    with open(path, "wb") as f:
            f.write(uploaded_file.getvalue())
    return path

# Title of page
st.title("Emotions Video Analyser")

# File upload
uploaded_file = st.file_uploader("Choose a file...", type=["wav","mp3","m4a","mp4","avi"])



# Check if a file has been uploaded
if uploaded_file is not None:

    # Display playback
    st.sidebar.success("File Uploaded Successfully")
    st.sidebar.header("Play Uploaded File")
    st.sidebar.video(uploaded_file)

    # Display loading message
    st.toast("Analysing File...")


    # Example usage
    # FILE_PATH = ["/Users/chengyao/Downloads/Hume_Test_Video_Football.mp3"]
    # FILE_PATH = ["/Users/chengyao/Downloads/Test_Hume_Comedian.mp4"]
    file_path = get_file_path(uploaded_file)
    print(file_path)
    processor = batchuploader.FileProcessor(file_path=file_path)

    predictions = processor.process_file()
    analyser = batchuploader.EmotionsAnalyser()
    st.toast("Transcription Complete")
    analyser.display_file_details(predictions)
    face_df, prosody_df = analyser.to_dataframe(predictions)
    analyser.export_results(face_df,"face_results.csv")
    analyser.export_results(prosody_df,"prosody_results.csv")
    # print("The most common facial occurence of emotion is: ", (analyser.most_common_occurence(dataframe=face_df)))
    # print("The most common prosody occurence of emotion is: ", (analyser.most_common_occurence(dataframe=prosody_df)))
    
    face_col1, face_col2, face_col3 = st.columns(3)
    face_col1.metric("Most common facial emotion", (analyser.most_common_occurence(dataframe=face_df))[0])
    face_col2.metric("Occurences", (analyser.most_common_occurence(dataframe=face_df))[1])
    face_col3.metric("Total Predictions", face_df.shape[0])

    prosody_col1, prosody_col2, prosody_col3 = st.columns(3)
    prosody_col1.metric("Most common prosody emotion", (analyser.most_common_occurence(dataframe=prosody_df))[0])
    prosody_col2.metric("Occurences", (analyser.most_common_occurence(dataframe=prosody_df))[1])
    prosody_col3.metric("Total Predictions", prosody_df.shape[0])

    # Create CSV data for the DataFrames
    st.dataframe(face_df)
    st.download_button(
        label="Download Facial Results",
        data=face_df.to_csv(index=False).encode('utf-8'),
        file_name='face_results.csv',
        mime='text/csv',
    )
    st.dataframe(prosody_df)
    st.download_button(
        label="Download Prosody Results",
        data=prosody_df.to_csv(index=False).encode('utf-8'),
        file_name='prosody_results.csv',
        mime='text/csv',
    )

else:
    st.error("Please upload a file")