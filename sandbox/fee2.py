# examples

class FeePaidOff:
    def __init__(self, fee):
        self.fee = fee

class Payment:
    def __init__(self, amount, fee):
        self.amount = amount
        self.fee = fee

class Entity:
    def __init__(self):
        self._events = []

    def broadcast(self, event):
        self._events.append(event)

class PaymentMade:
    fee = Type(Fee)
    amount = Int

class Fee(Entity):
    def __init__(self, balance):
        self.balance = balance
        self._orig_balance = balance
        self._payments = []
        super().__init__()

    def record_payment(self, amount):
        if amount <= 0:
            raise Exception("")

        self.apply(PaymentMade(self, amount))

        if self.balance == 0:
            self.broadcast(FeePaidOff(self))

    @PaymentMade.handle
    def apply(self, event):
        payment = Payment(event.amount, event.fee)
        self._payments.append(payment)
        self.balance = self.calc_balance()

    def calc_balance(self):
        balance = self._orig_balance
        for payment in self._payments:
            balance -= payment.amount
        return balance

fee = Fee(100)
fee.record_payment(10)
fee.record_payment(10)
fee.record_payment(30)
fee.record_payment(50)
print(fee.balance)
