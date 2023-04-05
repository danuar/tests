from db.Base import *


class ResultTest(BaseModel):
    __tablename__ = 'results_tests'
    user_id = Column(Uuid(), ForeignKey('users.id'))
    user = relationship('User', backref='results_tests')
    test_id = Column(Uuid(), ForeignKey('tests.id'))
    test = relationship('Test', backref='results_tests', lazy=False)
    note = Column(String(), nullable=True)
    completed_date = Column(DateTime(), nullable=False)
