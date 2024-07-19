#!/bin/bash

echo "Querying for a Python calculator code..."
curl -X POST "http://127.0.0.1:8000/agent/functioncall/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "python으로 작성된 계산기 코드를 검색해줘"}'

echo "Querying about the first innovative technology seen in the 1980s..."
curl -X POST "http://127.0.0.1:8000/agent/functioncall/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?"}'

echo "Querying what is React..."
curl -X POST "http://127.0.0.1:8000/agent/functioncall/query" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"query": "React가 뭐야?","top_k":1}'

echo "Querying for writing a Python program..."
curl -X POST "http://127.0.0.1:8000/agent/query" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"query": "Write a python program that satisfies the description below."}'

# 스크립트가 모든 요청을 완료했음을 알림
echo "All requests have been sent."
