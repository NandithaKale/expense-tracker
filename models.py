from dataclasses import dataclass

@dataclass
class Family:
    id: int
    name: str
    invite_code: str

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "invite_code": self.invite_code,
        }

@dataclass
class User:
    id: int
    username: str
    display_name: str
    role: str
    family_id: int

    def to_dict(self):
        return {
            "id":           self.id,
            "username":     self.username,
            "display_name": self.display_name,
            "role":         self.role,
            "family_id":    self.family_id,
        }

@dataclass
class Expense:
    id: int
    user_id: int
    family_id: int
    name: str
    amount: float
    category: str
    expense_type: str
    tag: str
    date: str

    def to_dict(self):
        return {
            "id":           self.id,
            "user_id":      self.user_id,
            "family_id":    self.family_id,
            "name":         self.name,
            "amount":       self.amount,
            "category":     self.category,
            "expense_type": self.expense_type,
            "tag":          self.tag,
            "date":         self.date,
        }

@dataclass
class Income:
    id: int
    user_id: int
    family_id: int
    amount: float
    category: str
    note: str
    month: str

    def to_dict(self):
        return {
            "id":        self.id,
            "user_id":   self.user_id,
            "family_id": self.family_id,
            "amount":    self.amount,
            "category":  self.category,
            "note":      self.note,
            "month":     self.month,
        }