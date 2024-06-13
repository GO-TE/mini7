from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import forms
from django.urls import reverse
from django.utils import timezone


from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory , ChatMessageHistory 
from langchain.schema import Document

from datetime import datetime

from .models import History

import numpy as np
import pandas as pd
import pytz
import json
import os


# Chroma 데이터베이스 초기화 - 사전에 database가 완성 되어 있다는 가정하에 진행 - aivleschool_qa.csv 내용이 저장된 상태임
embeddings = OpenAIEmbeddings(model = "text-embedding-ada-002")
database = Chroma(persist_directory = "./database2", embedding_function = embeddings)

def index(request):
    return render(request, 'selfgpt/index.html')

def chat(request):
    
    # post로 받은 question (index.html에서 name속성이 question인 input태그의 value값)을 가져옴
    query = request.POST.get('question')
        
    # 현재 시간
    dt = datetime.now()
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')   
    
    #chatgpt API 및 lang chain을 사용을 위한 선언
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    k = 3
    retriever = database.as_retriever(search_kwargs={"k": k})
    qa = RetrievalQA.from_llm(llm=chat,  retriever=retriever,  return_source_documents=True)
    
    # 유사성 점수
    sim = []
    result_sim = database.similarity_search_with_score(query=query, k=k)
    for r in result_sim:
        sim.append(round(r[1], 5))
    
    # 답변
    result = qa(query)

    # result.html에서 사용할 context
    context = {
        'question': query,
        'result': result["result"]
    }
    
    # DB에 로그 저장
    history = History(datetime=dt, query=query, sim1=sim[0], sim2=sim[1], 
                      sim3=sim[2], answer=result['result'])
    history.save()
    
    # 응답을 보여주기 위한 html 선택 (위에서 처리한 context를 함께 전달)
    return render(request, 'selfgpt/result.html', context) 


def show_log(request):
    history = History.objects.all() 
    return render(request, 'selfgpt/log.html', {'history': history})


def search_log(request):
    sp = request.POST.get('spdate')
    ep = request.POST.get('epdate')
    sp = sp.replace('T', ' ')
    ep = ep.replace('T', ' ')
    sp += ':00'
    ep += ':00'
    sp = datetime.strptime(sp, '%Y-%m-%d %H:%M:%S')
    ep = datetime.strptime(ep, '%Y-%m-%d %H:%M:%S')
    
    history = History.objects.filter(datetime__range=(sp, ep))
    return render(request, 'selfgpt/log.html', {'history': history})


