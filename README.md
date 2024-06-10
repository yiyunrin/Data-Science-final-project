# Data-Science-final-project
## 環境安裝
在Anaconda Prompt中，輸入以下指令來安裝環境和套件，env_name為自訂環境名稱
```cpp=
conda create --name {env_name} python=3.9
conda activate {env_name} 
pip install -r requirements.txt
```

## 執行程式碼
安裝完環境之後，即可輸入以下指令來執行程式碼
```cpp=
python search.py
```
開始執行後，即可在瀏覽器中打開 http://localhost:8000 來開啟介面

## 使用方法
1. 在下圖輸入框中輸入想要查詢的地點，並且按下搜尋按鈕
![show_engines_sidebar](./picture/search.png)

2. 勾選想要隨機選擇的餐廳，並按下隨機選擇的按鈕
![show_engines_sidebar](./picture/choose.png)

3. 最後就會在下方顯示隨機結果
![show_engines_sidebar](./picture/result.png)
