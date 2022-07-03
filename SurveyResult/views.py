from django.shortcuts import render
from django.views import View
import pandas as pd
import ssaw
from ssaw import InterviewsApi, QuestionnairesApi
import json

# Create your views here.

df = pd.DataFrame()

class Home(View):
    def get(self,request):
        client = ssaw.Client('https://cssapp.dishhome.com.np', 'DH_Datateam', 'Balen12345*#')
        interview_id = []
        answer = []
        for i in InterviewsApi(client).get_list(questionnaire_id="c1a0eb87a5384aacba9b2c3fdf9ea19f", questionnaire_version=2):
            interview_id.append(i.id)
        for i in interview_id:
            answer.append(InterviewsApi(client).get_info(i))
        j=0
        for i in answer:
            globals()[f"df{j}"] = pd.DataFrame.from_dict(pd.json_normalize(i), orient='columns')
            j = j+1
        for i in range(0,j):
            globals()[f"df{i}"] = globals()[f"df{i}"].T.reset_index()
            globals()[f"df{i}"].columns = globals()[f"df{i}"].iloc[0]
            globals()[f"df{i}"] = globals()[f"df{i}"].drop(0).reset_index(drop = True)
            globals()[f"df{i}"].columns.name = None
            globals()[f"df{i}"] = globals()[f"df{i}"].drop(labels=['VariableName'],axis=1)
            globals()[f"df{i}"] = globals()[f"df{i}"].drop([1,2])
        for i in range(1,j):
            global df0
            df0 =pd.merge(df0,globals()[f"df{i}"],how='outer')
        # print(df0)
        present_columns = df0.columns.to_list()
        json_records = df0.reset_index().to_json(orient ='records')
        data = []
        data = json.loads(json_records)
        for q in ssaw.QuestionnairesApi(client).get_list(questionnaire_id='c1a0eb87a5384aacba9b2c3fdf9ea19f'):
            survey_title = q.title
        context = {'data': data,'present_columns':present_columns,'survey_title':survey_title}
        global df
        df = df0.copy()
        # question_variables = []
        # df = df0.assign(Reason=df0['Reason'].str.split(',')).explode('Reason')
        # print(df['Reason'].value_counts())
        # for i in present_columns:
        #     df = df0.assign(i=df0[i].str.split(',')).explode(i)
        #     print(df[i].value_counts())
        return render(request,'SurveyResult/home.html',context)

    def post(self,request):
        variablename = request.POST.get('variablename')
        print(variablename)
        global df
        res = df.groupby(variablename).count().reset_index()
        res = res.iloc[:,:2]
        result = res.rename(columns={res.columns[1]:'Count'})
        present_columns = result.columns.to_list()
        json_records = result.reset_index().to_json(orient ='records')
        data = []
        data = json.loads(json_records)
        context = {'data': data,'present_columns':present_columns}
        return render(request,'SurveyResult/questionresult.html',context)
        
