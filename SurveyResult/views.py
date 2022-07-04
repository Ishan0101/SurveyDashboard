from asyncio.windows_events import NULL
from django.shortcuts import render
from django.views import View
import pandas as pd
import ssaw
from ssaw import InterviewsApi, QuestionnairesApi
from ssaw.models import Group, QuestionnaireDocument
from ssaw.utils import get_properties
import json
import numpy as np
import warnings

# Create your views here.

df = pd.DataFrame()
variablename=''
question_df = pd.DataFrame()

warnings.filterwarnings('ignore')

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
        json_records = df0.reset_index().to_json(orient ='records')
        data = []
        data = json.loads(json_records)
        global df
        df = df0.copy()
        present_columns = df0.columns.to_list()
        q_doc =  QuestionnairesApi(client).document(id = "c1a0eb87a5384aacba9b2c3fdf9ea19f",version = 2)
        Group.update_forward_refs()

        q = QuestionnaireDocument.parse_obj(q_doc)

        question_txt = pd.DataFrame(columns=['variable_name','question_text'])

        flat_list = get_properties(q)
        for i in present_columns:
            question_txt.loc[len(question_txt.index)] = [i,flat_list[i].question_text]

        global question_df
        question_df = question_txt.copy()

        df0 = df0.rename(columns=question_txt.set_index('variable_name')['question_text'])

        for q in ssaw.QuestionnairesApi(client).get_list(questionnaire_id='c1a0eb87a5384aacba9b2c3fdf9ea19f'):
            survey_title = q.title
        present_columns1 = df0.columns.to_list()
        column_list = zip(present_columns,present_columns1)
        context = {'data': data,'column_list':column_list,'survey_title':survey_title,'present_columns':present_columns,'present_columns1':present_columns1}
        return render(request,'SurveyResult/home.html',context)


    def post(self,request):
        variable = request.POST.get('variablename')
        global variablename
        variablename = variable
        #print(variablename)
        global df
        global question_df
        client = ssaw.Client('https://cssapp.dishhome.com.np', 'DH_Datateam', 'Balen12345*#')
        q_doc =  QuestionnairesApi(client).document(id = "c1a0eb87a5384aacba9b2c3fdf9ea19f",version = 2)
        Group.update_forward_refs()
        q = QuestionnaireDocument.parse_obj(q_doc)
        flat_list = get_properties(q)
        if flat_list[variablename].obj_type == 'MultyOptionsQuestion':
            choice_list = []
            for i in flat_list[variablename].answers:
                choice_list.append(i.answer_text)
            res = pd.DataFrame(columns=[variablename,'Count'])
            for i in choice_list:
                count = 0
                for j in df[variablename]:
                    if j is not None:
                        if j.find(i) !=-1:
                            count = count+1
                res.loc[len(res.index)] = [i,count]
            present_columns = res.columns.to_list()
            print(res)
            print(choice_list)
            json_records = res.reset_index().to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            result = res.rename(columns=question_df.set_index('variable_name')['question_text'])
            present_columns1 = result.columns.to_list()
            context = {'data': data,'present_columns':present_columns,'variablename':variablename,'present_columns1':present_columns1}
            return render(request,'SurveyResult/questionresult.html',context)
        else:
            res = df.groupby(variablename).count().reset_index()
            res = res.iloc[:,:2]
            result = res.rename(columns={res.columns[1]:'Count'})
            present_columns = result.columns.to_list()
            json_records = result.reset_index().to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            result = result.rename(columns=question_df.set_index('variable_name')['question_text'])
            present_columns1 = result.columns.to_list()
            context = {'data': data,'present_columns':present_columns,'variablename':variablename,'present_columns1':present_columns1}
            return render(request,'SurveyResult/questionresult.html',context)




class Response(View):
    def get(self,request):
        option_value = request.GET.get("name")
        global variablename
        global df
        global question_df
        client = ssaw.Client('https://cssapp.dishhome.com.np', 'DH_Datateam', 'Balen12345*#')
        q_doc =  QuestionnairesApi(client).document(id = "c1a0eb87a5384aacba9b2c3fdf9ea19f",version = 2)
        Group.update_forward_refs()
        q = QuestionnaireDocument.parse_obj(q_doc)
        flat_list = get_properties(q)
        if flat_list[variablename].obj_type == 'MultyOptionsQuestion':
            result = df.iloc[:0].copy()
            count =0
            for i in df[variablename]:
                if i is not None:
                    if option_value in i:
                        result.loc[len(result.index)]=df.iloc[count,:]
                count = count+1
            present_columns = result.columns.to_list()
            json_records = result.reset_index().to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            result = result.rename(columns=question_df.set_index('variable_name')['question_text'])
            present_columns1 = result.columns.to_list()
            context = {'data': data,'present_columns':present_columns,'option_value':option_value,'variablename':variablename,'present_columns1':present_columns1}
            return render(request,'SurveyResult/responselist.html',context)
        else:
            result = df[df[variablename]==option_value]
            present_columns = result.columns.to_list()
            json_records = result.reset_index().to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            result = result.rename(columns=question_df.set_index('variable_name')['question_text'])
            present_columns1 = result.columns.to_list()
            context = {'data': data,'present_columns':present_columns,'option_value':option_value,'variablename':variablename,'present_columns1':present_columns1}
            return render(request,'SurveyResult/responselist.html',context)
        

