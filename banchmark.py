from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)
    
    def on_start(self):
        pass

    @task
    def parse(self):
        self.client.get("/parse?sentence=我想看电影")
        