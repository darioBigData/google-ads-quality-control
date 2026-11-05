class AccountNotProcessableError(Exception):
    def __init__(self, customer_id: str, reason: str):
        self.customer_id = customer_id
        self.reason = reason
        super().__init__(f"{customer_id} | {reason}")
