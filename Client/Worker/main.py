from api import API
import argparse
from constants import API_DOMAIN
from llm_task import LLMTask
from utils import get_logger, timer
import time
from llm_models import LLMModelConfig

logger = get_logger("GPU-Worker")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--api_domain", type=str, required=False, default=API_DOMAIN)
    args = args.parse_args()

    api = API(domain=args.api_domain, token=args.token)
    available_models = api.get_available_models()
    logger.info(available_models)

    avail_model_objs = {
        model["model_name"]: LLMModelConfig(**model) for model in available_models
    }
    logger.info("Init process complete. Waiting for tasks...")

    while True:
        try:
            with timer(logger=logger, message="get_task"):
                task = api.get_task()
            if task is None:
                # No task available
                time.sleep(0.25)
                continue

            llm_task = LLMTask(**task)
            llm_model = avail_model_objs.get(llm_task.llm_model_name, None)
            if llm_model is None:
                logger.error(f"LLM Model {llm_task.llm_model_name} not exist")
                api.post_task_result(
                    task_id=llm_task.task_id,
                    result_status="failed",
                    description="LLM Model not exist",
                    completed_in_seconds=0,
                )
                continue

            if llm_model.llm is None:
                # we will hold the model in memory, this potentially can cause error
                llm_model.init_llm()
            logger.info(f"Running task {llm_task.task_id}")
            logger.info(f"LLM Model: {llm_task.llm_model_name}")
            logger.info(f"LLM Model Path: {llm_model.model_path()}")

            with timer(logger=logger, message="run_task"):
                start_time = time.time()
                try:
                    result = llm_task.run(llm_model)
                    result_status = "completed"
                except Exception as e:
                    logger.exception(e)
                    result = str(e)
                    result_status = "failed"
                end_time = time.time()
                logger.info(f"Task {llm_task.task_id} completed")
                try:
                    api.post_task_result(
                        task_id=llm_task.task_id,
                        result_status=result_status,
                        description=str(result) if result else "Error",
                        completed_in_seconds=end_time - start_time,
                        result=result,
                    )
                except Exception as e:
                    logger.exception(e)
        except Exception as e:
            logger.exception(e)
        time.sleep(0.25)
