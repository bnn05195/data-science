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

3-1 compare
FAF5와 소비자 물가지수와 합쳐서 파란색 막대기는 그 해의 모든 품목의 물동량을 합친 값, 주황색 막대기는 그 해의 소비자 물가지수(총 4분기)의 평균을 구한 값을 나타냈습니다.

3-2 each_item 
각 품목의 연도 간 물동량 차이를 꺾은선 그래프로 나타냈습니다. 

3-3 state_origin
주별 물동량(출발 기준)를 나타냈습니다.

3-4 state_origin
주별 물동량(도착 기준)를 나타냈습니다.

3-5 total
각 연도별로 물동량이 많은 품목 순으로 막대 그래프로 나타냈습니다.
