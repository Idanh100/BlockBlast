import torch
import torch.nn as nn
import torch.nn.functional as F
from State2 import State
from Environment2 import Environment
from CONSTANTS import *

class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
       
        # Conv1: מזהה תבניות בסיסיות
        # pool: מקטין את המידע ומדגיש תכונות חשובות
        # Conv2: מזהה תבניות מורכבות יותר
        # fc layers: בסוף מקבל את ההחלטה
        # Q: מייצג את הערך של של המצב שיהיה אחרי ביצוע הפעולה, אם הקיו גבוה, הפעולה הייתה טובה, אם הוא נמוך, הפעולה הייתה פחות טובה


        # conv1: יוצר שכבת קונבולוציה ראשונה עם
        # 16 פילטרים
        # גודל ליבה 3
        # 1 padding
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)  # input: (1, 8, 8) -> output: (16, 8, 8)
      
        # pool יוצר לוח מוקטן 4 על 4 עם גודל ליבה 2 וצעד 2, מקטין את גודל הלוח
        self.pool = nn.MaxPool2d(2, 2)  # output: (16, 4, 4)
      
        # conv2: יוצר שכבת קונבולוציה שנייה עם
        # 32 פילטרים
        # גודל ליבה 3
        # 1 padding
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)  # output: (32, 4, 4)
    
        # fc1: יוצר שכבת fully connected
        # שמקבלת את הפיצ'רים מהשכבות הקודמות
        # ויוצרת 128 נוירונים
        self.fc1 = nn.Linear(32 * 2 * 2, 128)  # 128 -> 128
     
        # fc2: יוצר שכבת fully connected
        # שמקבלת את הפיצ'רים מהשכבה הקודמת
        # ומקטינה ל64 נוירונים
        self.fc2 = nn.Linear(128, 64)  # 128 -> 64
      
        # fc3: יוצר שכבת fully connected סופית
        # שמקבלת את הפיצ'רים מהשכבה הקודמת
        # ומפיקה ערך קיו יחיד עבור כל מצב
        self.fc3 = nn.Linear(64, 1)  # 64 -> 1 (Q-value output)


        self.env = Environment(State())  # יצירת סביבה עם מצב התחלתי
        self.Current_State = State()  # מצב נוכחי חדש
        self.State_Tensor = self.Current_State.TensorState(self.Current_State.Board)  # טנסור מצב מהלוח
        self.All_Moves = self.env.GetAllPossibleMoves(self.Current_State)  # כל המהלכים האפשריים
        self.All_After_States = self.env.AfterState(self.Current_State, self.All_Moves)  # כל המצבים לאחר כל המהלכים
        
        
    def forward(self, All_After_States):  # של כל מצב Qמעביר את המצבים דרך הרשת ומחזיר את ערך ה 

        # conv1: סורק את הלוח ומזהה תבניות בסיסיות
        # relu: מוחקת ערכים שליליים בשביל לעזור לרשת ללמוד בצורה טובה ויציבה יותר
        # pool: מקטין את המידע ומדגיש את התכונות החשובות
        All_After_States = self.pool(F.relu(self.conv1(All_After_States)))  # conv1 + relu + pool

        # conv2: מקבלת את התבניות מהשכבה הראשונה ומזהה תבניות מורכבות יותר
        # relu: שוב מוחקת ערכים שליליים בשביל לעזור לרשת ללמוד בצורה טובה ויציבה יותר
        # pool: שוב מקטין את המידע בשביל לפשט את הייצוג של הלוח
        All_After_States = self.pool(F.relu(self.conv2(All_After_States)))  # conv2 + relu + pool

        # הופך את כל המפות שנוצרו לווקטור אחד ארוך
        # Fully Connected בשביל שאפשר יהיה להעביר אותו לשכבות
        All_After_States = All_After_States.view(-1, 32 * 2 * 2)  # שיטוח לתכונה לווקטור

        # שכבת Fully Connected ראשונה שמתחילה לשלב בין כל התכונות שנמצאו
        # relu מוסיפה אי ליניאריות ומשפרת את יכולת הלמידה של הרשת.
        All_After_States = F.relu(self.fc1(All_After_States))  # fc1 + relu

        # שכבת Fully Connected נוספת שמעבדת עוד את המידע
        # ומאפשרת לרשת להבין טוב יותר עד כמה המצב טוב
        All_After_States = F.relu(self.fc2(All_After_States))  # fc2 + relu

        # שכבת היציאה של הרשת
        # מחזירה ערך קיו יחיד שמייצג כמה המצב שהתקבל אחרי המהלך נחשב טוב
        All_After_States = self.fc3(All_After_States)  # fc3 -> Q-value

        return All_After_States  # החזרת ערכי Q
    

    
    def loss(self, Q_values, rewards, Q_hat_values, dones, gamma=GAMMA):  # חישוב איבוד MSE
        # מחשב את ערכי היעד לפי נוסחת בלמן
        target_q_values = rewards + gamma * Q_hat_values * (1 - dones)  # מטרות על בסיס Bellman
        
        # מחשב את ההפרש בין ערכי הקיו שהמודל חזה לבין ערכי היעד
        mse_loss = F.mse_loss(Q_values, target_q_values)  # בין קיו ליעד MSE

        # מחזיר את ערך השגיאה בשביל שבעזרתו נעדכן את משקלי הרשת
        return mse_loss
    
    def loadModel (self, file):  # טעינת מודל שמור מקובץ
        self.model = torch.load(file)
    
    def save_param (self, path):  # שומר את משקלי המודל לקובץ
        self.DQN.save_params(path)