import time
from backend.gateway.core.celery import celery
from celery import Task
# import logging
# from transformers import pipeline


class PredictTransformersPipelineTask(Task):
    """
    Abstraction of Celery's Task class to support loading transformers model.
    """

    task_name = ""
    model_name = ""
    abstract = True

    def __init__(self):
        super().__init__()
        self.pipeline = None

    def __call__(self, *args, **kwargs):
        """
        Load pipeline on first call (i.e. first task processed) Avoids the need to load pipeline on each task request.
        """
        pass
        # if not self.pipeline:
        #     logging.info("Loading pipeline...")
        #     self.pipeline = pipeline(self.task_name, model=self.model_name)
        #     logging.info("Pipeline loaded")
        # return self.run(*args, **kwargs)


@celery.task(
    ignore_result=False,
    bind=True,
    base=PredictTransformersPipelineTask,
    task_name="text-generation",
    model_name="gpt2",
    name="tasks.predict_transformers_pipeline",
)
def predict_transformers_pipeline(self, prompt: str):
    """
    Essentially the run method of PredictTask.
    """
    return "Not implemented"
    # result = self.pipeline(prompt)
    # return result


@celery.task(name="tasks.increment")
def increment(value: int) -> int:
    time.sleep(5)
    new_value = value + 1
    return new_value
