import random
from locust import FastHttpUser, task, between

class User(FastHttpUser):
    wait_time = between(1,5)
    
    def get_random_token(self):
        return f"Token {random.choice(("3312e312db9a5b22fcb4a59d08be15751a60a7fb", "1df01115f48d450fcc867f8b6293303d2602cba9", "5d30233f092915b0c1397ca6e7778cf63dc99ef3"))}"
    
    @task
    def see_user_profile(self):
        token = self.get_random_token()
        self.client.get("/member/profile/p-1/", headers={"Authorization": token})
    
    @task
    def see_tasks(self):
        self.client.get("/member/tasks/", headers={"Authorization": "Token 313c4e6b87bdc960da84c9c7c3e5f0f2a8e54e39"})
