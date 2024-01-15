import uuid
from abc import ABCMeta, abstractmethod

from webapi.InterfacesControllers.StorageControllers import IResultTestRepository
from webapi.ViewModel import AnswerViewModel, UserViewModel, QuestionViewModel, ResultTestViewModel, \
    StatePassingTestViewModel


class IPassingTestLogic(metaclass=ABCMeta):

    @abstractmethod
    async def start_passing_test(self, user: UserViewModel, test_id: uuid.UUID) -> StatePassingTestViewModel:
        pass

    @abstractmethod
    def get_current_question(self, user: UserViewModel) -> QuestionViewModel:
        pass

    @abstractmethod
    def add_answer_in_result(self, user: UserViewModel, answer: AnswerViewModel):
        pass

    @abstractmethod
    async def complete_test(self, user: UserViewModel) -> ResultTestViewModel:
        pass

    def __init__(self, repository: IResultTestRepository):
        self._repository = repository
