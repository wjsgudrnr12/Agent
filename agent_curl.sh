#!/bin/bash

# 첫 번째 API 요청: React에 대한 쿼리
curl -X POST "http://127.0.0.1:8000/ETRI/vectordb/customdb/query" -H "Content-Type: application/json; charset=utf-8" -d '{"query": "React가 뭐야?","top_k":1}'
echo -e "\n"  # 요청 간 구분을 위해 줄바꿈 추가

# 두 번째 API 요청: 논문 내용 조회
curl -X POST "http://127.0.0.1:8000/ETRI/vectordb/chromadb/query" -H "Content-Type: application/json; charset=utf-8" -d '{"query": "이 논문의 내용은 어떤 내용이야?", "top_k": 1}'
echo -e "\n"

# 세 번째 API 요청: 1980년대 혁신적인 기술 조회 (koalpaca)
curl -X POST "http://127.0.0.1:8000/ETRI/llm/koalpaca_12_8/query" -H "Content-Type: application/json" -d '{"query": "1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?"}'
echo -e "\n"

# 네 번째 API 요청: 1980년대 혁신적인 기술 조회 (agent)
curl -X POST "http://127.0.0.1:8000/agent/query" -H "Content-Type: application/json" -d '{"query": "1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?"}'
echo -e "\n"

# 스크립트가 모든 요청을 완료했음을 알림
echo "All requests have been sent."
