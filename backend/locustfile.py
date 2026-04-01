import random
from faker import Faker
from locust import FastHttpUser, task, between


class UserDRF(FastHttpUser):
    wait_time = between(1, 3)
    host="https://localhost"
    TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc1MDMwNjc4LCJpYXQiOjE3NzUwMDU0NzgsImp0aSI6IjA5YzQ5YWYzZmFlNzRlYmZiYjMxZjgzMDJjNjgzYThiIiwidXNlcl9pZCI6IjEwMzYxIiwicm9sZSI6Im9yZ2FuaXplciJ9.x4R_ZLsZelQR_d1wEAnmn3_SRzy75hxE6rfRdNCrxOM"
    
    @task
    def see_track_members_FrontEnd(self):
        self.client.get(f"/api/organizer/members/frontend/", headers={"Authorization": self.TOKEN})
    @task
    def see_track_members_CCNA(self):
        self.client.get(f"/api/organizer/members/CCNA/", headers={"Authorization": self.TOKEN})
    @task
    def see_track_members_Python(self):
        self.client.get(f"/api/organizer/members/Python/", headers={"Authorization": self.TOKEN})
    @task
    def see_track_members_C_Sharp(self):
        self.client.get(f"/api/organizer/members/C-Sharp/", headers={"Authorization": self.TOKEN})
    @task
    def see_track_members_Graphic(self):
        self.client.get(f"/api/organizer/members/Graphic%20Design/", headers={"Authorization": self.TOKEN})

    # @task
    # def do_register(self):
    #     faker = Faker()
    #     code = f"C{random.randint(1111111, 9999999)}"
    #     body = {
    #         "name": faker.user_name(),
    #         "email": faker.email(domain="gmail.com"),
    #         "collage_code": code,
    #         "phone_number": faker.phone_number(),
    #         "request_track_id": random.randint(12,16),
    #     }
    #     res = self.client.post(
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
