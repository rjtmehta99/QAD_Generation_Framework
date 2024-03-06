import pandas as pd

def merge_by_subject(subject_files: list) -> pd.DataFrame:
    df_subject = []
    for file in subject_files:
        df_temp = pd.read_csv('data/'+file)
        # Bright storm
        if list(df_temp.columns) == ['title', 'summary', 'subject', 'url']:
            df_temp = df_temp[['summary']]

        #Openstax
        elif list(df_temp.columns) == ['summary_heading', 'summary_text', 'subject']:
            df_temp = df_temp[['summary_text']]

        # CK12
        elif list(df_temp.columns) == ['title','url','subject','content']:
            df_temp = df_temp[['content']]

        df_temp.columns = ['content']
        df_subject.append(df_temp)

    df_subject = pd.concat(df_subject, ignore_index=True)
    df_subject = df_subject.fillna('No data')
    return df_subject
