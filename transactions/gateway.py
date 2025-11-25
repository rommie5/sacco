class PaymentGateway:
    def initiate_payment(self, amount, member):
        raise NotImplementedError

    def verify_payment(self, payload):
        raise NotImplementedError
