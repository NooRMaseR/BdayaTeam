import random
from faker import Faker
from locust import FastHttpUser, task, between


class UserDRF(FastHttpUser):
    wait_time = between(2, 5)
    host="https://localhost"

    # def get_random_token(self):
    #     return f"Token {random.choice(("3312e312db9a5b22fcb4a59d08be15751a60a7fb", "1df01115f48d450fcc867f8b6293303d2602cba9", "5d30233f092915b0c1397ca6e7778cf63dc99ef3"))}"

    # @task
    # def see_user_profile(self):
    #     # token = self.get_random_token()
    #     self.client.get("/api/member/profile/p-1/", headers={"Authorization": "Token 1fff50986e94802e10e6045fc4bca350330362f3"})

    # @task
    # def see_tasks(self):
    #     self.client.get("/api/member/tasks/", headers={"Authorization": "Token 7052ccbd55a3b7fd2c6f2061c11466f8694eb411"})
    
    @task
    def see_track_members_FrontEnd(self):
        self.client.get(f"/api/organizer/members/frontend/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMTk5OTgyLCJpYXQiOjE3NzAxNzQ3ODIsImp0aSI6IjE4NmJjZTdhMmVhMDQ5Mzk4NzQ4OGY5MjQ2NjdlNGM5IiwidXNlcl9pZCI6IjEifQ.5SK13z4Wb9DQq6GLzxx4vJurkOW8bc1lk3Z3WtCY1ZA"})
    @task
    def see_track_members_CCNA(self):
        self.client.get(f"/api/organizer/members/CCNA/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMTk5OTgyLCJpYXQiOjE3NzAxNzQ3ODIsImp0aSI6IjE4NmJjZTdhMmVhMDQ5Mzk4NzQ4OGY5MjQ2NjdlNGM5IiwidXNlcl9pZCI6IjEifQ.5SK13z4Wb9DQq6GLzxx4vJurkOW8bc1lk3Z3WtCY1ZA"})
    @task
    def see_track_members_Python(self):
        self.client.get(f"/api/organizer/members/Python/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMTk5OTgyLCJpYXQiOjE3NzAxNzQ3ODIsImp0aSI6IjE4NmJjZTdhMmVhMDQ5Mzk4NzQ4OGY5MjQ2NjdlNGM5IiwidXNlcl9pZCI6IjEifQ.5SK13z4Wb9DQq6GLzxx4vJurkOW8bc1lk3Z3WtCY1ZA"})
    @task
    def see_track_members_C_Sharp(self):
        self.client.get(f"/api/organizer/members/C-Sharp/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMTk5OTgyLCJpYXQiOjE3NzAxNzQ3ODIsImp0aSI6IjE4NmJjZTdhMmVhMDQ5Mzk4NzQ4OGY5MjQ2NjdlNGM5IiwidXNlcl9pZCI6IjEifQ.5SK13z4Wb9DQq6GLzxx4vJurkOW8bc1lk3Z3WtCY1ZA"})
    @task
    def see_track_members_Graphic(self):
        self.client.get(f"/api/organizer/members/Graphic%20Design/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMTk5OTgyLCJpYXQiOjE3NzAxNzQ3ODIsImp0aSI6IjE4NmJjZTdhMmVhMDQ5Mzk4NzQ4OGY5MjQ2NjdlNGM5IiwidXNlcl9pZCI6IjEifQ.5SK13z4Wb9DQq6GLzxx4vJurkOW8bc1lk3Z3WtCY1ZA"})

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

