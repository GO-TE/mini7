from django.shortcuts import render

import pandas as pd
import numpy as np
import os
import openai

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



# Create your views here.


embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# db 경로 변경 요망
database = Chroma(persist_directory="./database",
                    embedding_function = embeddings
)

def index(request):
    return render(request, 'vectordb/index.html')

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        file_path = fs.path(filename)
        
        try:
            df = pd.read_csv(file_path)
            if df.columns in 'Unnamed: 0':
                df.drop('Unnamed: 0', axis=1, inplace = True)

            if validDataFrame(df):
                meta = df['구분'].to_list()
                meta = [{'cateogory' : data} for data in  meta]
                data = df['QA'].to_list()
                doc = []
                
                for i in range(len(df)):
                    if validSimilarityScore(data[i]):
                        doc.append(Document(page_content=data[i], metadata=meta[i]))
                    continue
                database.add_documents(doc)

                return JsonResponse({'status': 'success', 'message': 'CSV 업로드 완료'})
            else:
                return JsonResponse({'status': 'error', 'message': 'CSV 양식이 올바르지 않습니다.'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '업로드 할 파일이 없거나 올바르지 않은 요청입니다.'})


def validSimilarityScore(data):
    score = database.similarity_search_with_score(data, k=1)
    if score[0][1] >= 0.7:
        return False
    return True

def validDataFrame(df):
    if len(df.columns) != 2:
        return False
    
    if df.columns[0] in ['QA', '구분'] and df.columns[1] in ['QA', '구분']:
        return True
    return False