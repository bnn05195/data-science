### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   ex) $ py -m streamlit run 2023_total.py

   ```

3. 각 폴더 설명

   3-1 compare <br>
   FAF5와 소비자 물가지수와 합쳐서 파란색 막대기는 그 해의 모든 품목의 물동량을 합친 값, 주황색 막대기는 그 해의 소비자 물가지수(총 4분기)의 평균을 구한 값을 나타냈습니다.

   3-2 each_item <br>
   각 품목의 연도 간 물동량 차이를 꺾은선 그래프로 나타냈습니다. 

   3-3 state_origin <br>
   주별 물동량(출발 기준)의 품목 순위를 막대 그래프로 나타냈습니다.

   3-4 state_destination <br>
   주별 물동량(도착 기준)의 품목 순위를 막대 그래프로 나타냈습니다.

   3-5 total <br>
   각 연도별로 물동량이 많은 품목 순으로 막대 그래프로 나타냈습니다.

   3-6 Choropleth_Map <br>
   각 물품별로 수출/수입이 어느 주가 많고 적은지를 색상의 진하기로 나타냈습니다. (물동량 분포)

   3-7 od_map <br>
   "이 주가 어디로 많이 보내는가" (출발지 고정, 도착지별 집계) — 수출/생산 분석 <br>
   "이 주가 어디서 많이 받는가" (도착지 고정, 출발지별 집계) — 수입/소비 분석

   3-8 corridor_map <br>
   지도 위에 화물의 출발지와 도착지를 점(Node)으로 찍고, 그 사이를 선(Edge/Line)으로 연결하여 주요 물동량 거점 주(state)를 나타냈습니다.

   3-9 distance_histogram <br>
   X축을 '운송 거리(마일)', Y축을 '물동량(톤)'으로 설정하여, 어느 거리 구간에서 화물 운송이 가장 활발하게 일어나는지 나타냈습니다.