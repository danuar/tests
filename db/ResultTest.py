from db.Base import *


class ResultTest(BaseModel):
    __tablename__ = 'results_tests'
    user_id = Column(Integer(), ForeignKey('users.id'))
    user = relationship('User', backref='results_tests')
    test_id = Column(Integer(), ForeignKey('tests.id'))
    test = relationship('Test', backref='results_tests')
