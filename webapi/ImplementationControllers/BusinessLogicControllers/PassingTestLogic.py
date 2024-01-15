import uuid

from webapi.InterfacesControllers import ICachedService, IResultTestLogic
from webapi.InterfacesControllers.BusinessLogicControllers.IPassingTestLogic import IPassingTestLogic
from webapi.ViewModel import UserViewModel, AnswerViewModel, ResultTestViewModel, QuestionViewModel, \
    StatePassingTestViewModel, TestViewModel


class PassingTestLogic(IPassingTestLogic):

    async def start_passing_test(self, user: UserViewModel, test_id: uuid.UUID) -> StatePassingTestViewModel:
        state_passing: StatePassingTestViewModel = self._cache_service.TryGet(f"StatePassingTest.{user.id}")
        if (state_passing is not None and state_passing.completed is None or
                self._cache_service.result_last_operation is True):
            raise Exception("Уже начато прохождение теста")
        state = StatePassingTestViewModel(
            await self._logic.Create(ResultTestViewModel.Create(user, TestViewModel.GetFromId(test_id))))
        self._cache_service.Set(f"StatePassingTest.{user.id}", state)
        return state.GetViewModel()

    def get_current_question(self, user: UserViewModel) -> QuestionViewModel:
        return self._get_state_passing_test_from_user(user.id).current_question

    def add_answer_in_result(self, user: UserViewModel, answer: AnswerViewModel):
        return self._get_state_passing_test_from_user(user.id).add_answer(answer)

    async def complete_test(self, user: UserViewModel) -> ResultTestViewModel:
        result_test = self._get_state_passing_test_from_user(user.id).complete_test()
        await self._logic.CompleteTest(user, result_test)
        return result_test

    def _get_state_passing_test_from_user(self, user_id: uuid.UUID) -> StatePassingTestViewModel:
        state: StatePassingTestViewModel = self._cache_service.TryGet(f"StatePassingTest.{user_id}")
        if self._cache_service.result_last_operation is False:
            raise Exception("У данного пользователя нет активных тестов")
        return state
