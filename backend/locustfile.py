# import random
# from faker import Faker
# from pprint import pprint
from locust import FastHttpUser, task, between


class MemberBoltUser(FastHttpUser):
    wait_time = between(2, 5)
    host="https://localhost/api"
    TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzc4OTc0NTgyLCJpYXQiOjE3Nzg5NDkzODIsImlzX3N0YWZmIjpmYWxzZSwiaXNfc3VwZXJ1c2VyIjpmYWxzZSwidXNlcm5hbWUiOiJOb29yIiwiZW1haWwiOiJub29yd25lNkBnbWFpbC5jb20iLCJyb2xlIjoibWVtYmVyIiwiY29kZSI6InAtMSIsInRva2VuX3R5cGUiOiJhY2Nlc3MiLCJqdGkiOiI5MTA4YjIxMC1iM2ZiLTQ3YTMtYmY3Ny02NmY1ZDhmNjBkOGMifQ.93um4f-dWcWA6OKqCttOvn5NVXuB6na29owzwMrMnE8"
    
    @task
    def see_tasks(self):
        self.client.get(f"/member/tasks/", headers={"Authorization": self.TOKEN})
    
    @task
    def see_my_profile(self):
        self.client.get(f"/member/profile/p-1/", headers={"Authorization": self.TOKEN})
    
    
# class OrgBoltUser(FastHttpUser):
#     wait_time = between(2, 5)
#     host="http://localhost:8000/api"
#     TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2ODg1NjY4LCJpYXQiOjE3NzY4NjA0NjgsImp0aSI6ImVmODI0Y2QyMDQxYjQ1MGM4NmQ2MTc2NTYwNWE2MGM2IiwidXNlcl9pZCI6IjEwIiwicm9sZSI6Im9yZ2FuaXplciJ9._4RFUn1PNoQFdV4TighWdOn5YxjcuOJxsMNjxXQHslA"
    
#     @task
#     def see_track_members_FrontEnd(self):
#         self.client.get(f"/organizer/members/Frontend/", headers={"Authorization": self.TOKEN})
    
#     @task
#     def see_track_members_CCNA(self):
#         self.client.get(f"/organizer/members/CCNA/", headers={"Authorization": self.TOKEN})
    
#     @task
#     def see_track_members_Python(self):
#         self.client.get(f"/organizer/members/Python/", headers={"Authorization": self.TOKEN})
    
#     @task
#     def see_track_members_C_Sharp(self):
#         self.client.get(f"/organizer/members/C-Sharp/", headers={"Authorization": self.TOKEN})
    
#     @task
#     def see_track_members_Graphic(self):
#         self.client.get(f"/organizer/members/Graphic%20Design/", headers={"Authorization": self.TOKEN})
    
    # @task
    # def do_register(self):
    #     faker = Faker()
    #     code = f"C{random.randint(1111111, 9999999)}"
    #     body = {
    #         "name": faker.user_name(),
    #         "email": faker.email(domain="gmail.com"),
    #         "collage_code": code,
    #         "phone_number": faker.phone_number(),
    #         "request_track_id": random.choice((1, 2, 7, 8 ,11)),
    #     }
    #     self.client.post(
    #         "/api/register/", json=body, headers={"Content-Type": "application/json"}
    #     )

# class Technical(FastHttpUser):
#     wait_time = between(1, 3)
#     host = "https://localhost/en"
    
#     @task
#     def see_home_page(self):
#         self.client.get(f"", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNTM3NTA5LCJpYXQiOjE3NzE1MTIzMDksImp0aSI6ImQ5NmVkY2E4MWM0YzRiYmU5MzlkZjFmNmFlM2I3ZWE1IiwidXNlcl9pZCI6IjMwMjYifQ.mJM9mrvN26weEPWfyuU2MizgbbyinlwdvXlvpzxIebE"})
    
#     @task
#     def see_home_role_page(self):
#         self.client.get(f"/technical/Python", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNTM3NTA5LCJpYXQiOjE3NzE1MTIzMDksImp0aSI6ImQ5NmVkY2E4MWM0YzRiYmU5MzlkZjFmNmFlM2I3ZWE1IiwidXNlcl9pZCI6IjMwMjYifQ.mJM9mrvN26weEPWfyuU2MizgbbyinlwdvXlvpzxIebE"})
    
#     @task
#     def see_tasks_page(self):
#         self.client.get(f"/technical/Python/tasks", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNTM3NTA5LCJpYXQiOjE3NzE1MTIzMDksImp0aSI6ImQ5NmVkY2E4MWM0YzRiYmU5MzlkZjFmNmFlM2I3ZWE1IiwidXNlcl9pZCI6IjMwMjYifQ.mJM9mrvN26weEPWfyuU2MizgbbyinlwdvXlvpzxIebE"})
    

# class Member(FastHttpUser):
#     wait_time = between(2, 5)
#     host = "https://localhost/en"
    
    
#     @task
#     def see_home_page(self):
#         self.client.get(f"/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNzEwNjg2LCJpYXQiOjE3NzE2ODU0ODYsImp0aSI6IjIxOTJiZmI5ODBhNTRiNjViZWRjYTFkNzk1NDIwNTQ4IiwidXNlcl9pZCI6IjEwMzUxIn0.Zb6GkCniTZEQBzegQsEtBDMhkOr9qcMpOl941pZdE_U"})
    
#     @task
#     def see_home_role_page(self):
#         self.client.get(f"/member/Python", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNzEwNjg2LCJpYXQiOjE3NzE2ODU0ODYsImp0aSI6IjIxOTJiZmI5ODBhNTRiNjViZWRjYTFkNzk1NDIwNTQ4IiwidXNlcl9pZCI6IjEwMzUxIn0.Zb6GkCniTZEQBzegQsEtBDMhkOr9qcMpOl941pZdE_U"})
    
#     @task
#     def see_my_profile_page(self):
#         self.client.get(f"/profile/p-746", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNzEwNjg2LCJpYXQiOjE3NzE2ODU0ODYsImp0aSI6IjIxOTJiZmI5ODBhNTRiNjViZWRjYTFkNzk1NDIwNTQ4IiwidXNlcl9pZCI6IjEwMzUxIn0.Zb6GkCniTZEQBzegQsEtBDMhkOr9qcMpOl941pZdE_U"})
    
#     @task
#     def see_tasks_page(self):
#         self.client.get(f"/member/Python/tasks", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNzEwNjg2LCJpYXQiOjE3NzE2ODU0ODYsImp0aSI6IjIxOTJiZmI5ODBhNTRiNjViZWRjYTFkNzk1NDIwNTQ4IiwidXNlcl9pZCI6IjEwMzUxIn0.Zb6GkCniTZEQBzegQsEtBDMhkOr9qcMpOl941pZdE_U"})
