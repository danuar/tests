from classy_fastapi import post, get
from fastapi import Depends

from webapi.InterfacesControllers import IPassingTestLogic
from webapi.SchemasModel import AnswerForCurrentQuestionSchema
from webapi.ViewModel import AnswerViewModel, AnswerTestViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user, get_passing_test_logic


class PassingTestController(AbstractController):

    @post("/start_test")
    async def start_passing_test(self, test_id, user=Depends(get_user),
                                 logic=Depends(get_passing_test_logic)):
        return await logic.start_passing_test(user, test_id)

    @get("/current_question")
    def get_current_question(self, user=Depends(get_user),
                             logic=Depends(get_passing_test_logic)):
        return logic.get_current_question(user)

    @post("/answer")
    async def send_answer_for_current_question(self, answer: AnswerForCurrentQuestionSchema, user=Depends(get_user),
                                         logic=Depends(get_passing_test_logic), auto_complete: bool = True):
        answervm = (AnswerViewModel.CreateForPassintTest(answer.text_answer)
                    .AddAnswersTests([AnswerTestViewModel.FromId(i) for i in answer.answers]))
        await logic.add_answer_in_result(user, answervm, auto_complete)
        return "Ответ успешно добавлен"

    @post("/end_test")
    async def complete_test(self, user=Depends(get_user),
                            logic=Depends(get_passing_test_logic)):
        return await logic.complete_test(user)
