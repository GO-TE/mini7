from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django import forms
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string


from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory , ChatMessageHistory 
from langchain.schema import Document

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import openai
from .serializers import ChatSerializer
from django.conf import settings

import pandas as pd
import json

def index(request):
    session_variable_name = 'chat_history'
    chat_history = request.session.get(session_variable_name, [])
    
    context = {
        'chat_history': chat_history
    }
    return render(request, 'selfchatgpt/index.html', context)
# http 연결 끊지만 않으면 세션에 저장되어 있는 대화 내용을 유지하고 보여줌


# Chroma 데이터베이스 초기화 - 사전에 database가 완성 되어 있다는 가정하에 진행 - aivleschool_qa.csv 내용이 저장된 상태임
embeddings = OpenAIEmbeddings(model = "text-embedding-ada-002")
database = Chroma(persist_directory = "./database2", embedding_function = embeddings)


def chat(request):
    #post로 받은 question (index.html에서 name속성이 question인 input태그의 value값)을 가져옴
    query = request.POST.get('question')

    #chatgpt API 및 lang chain을 사용을 위한 선언
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    k = 3
    retriever = database.as_retriever(search_kwargs={"k": k})
    qa = RetrievalQA.from_llm(llm=chat,  retriever=retriever,  return_source_documents=True)

    result = qa(query)

    # result.html에서 사용할 context
    context = {
        'question': query,
        'result': result["result"]
    }

    # 응답을 보여주기 위한 html 선택 (위에서 처리한 context를 함께 전달)
    return render(request, 'selfchatgpt/index.html', context) 



class ChatbotView(APIView):
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        session_variable_name = 'chat_history'
        chat_history = request.session.get(session_variable_name, []) # 이전 대화 내용이 저장된 세션 변수
        
        if serializer.is_valid():
            user_message = serializer.validated_data['message']
            chat = ChatOpenAI(model="gpt-3.5-turbo")
            
            k = 3
            retriever = database.as_retriever(search_kwargs={"k": k})
            
            memory = ConversationBufferMemory(memory_key=session_variable_name, input_key="question", output_key="answer",
                                  return_messages=True, initial_memory=chat_history)
            qa = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, memory=memory,
                                           return_source_documents=True,  output_key="answer")

            result = qa(user_message)
            
            # 이전 대화 기록에 현재 대화 추가
            chat_history.append((user_message, result['answer']))

            # 세션에 대화 내용 저장
            request.session[session_variable_name] = chat_history
            
            context = {
                'question': user_message,
                'result': result['answer'],
            }


            return Response({'response': context['result']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)