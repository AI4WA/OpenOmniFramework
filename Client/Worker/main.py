from api import API
import argparse
from constants import API_DOMAIN, NORMAL_MODELS
from ml_models import MLModelConfig
from llm_task import LLMTask
from utils import get_logger, timer
import time
import uuid
from llm_models import LLMModelConfig
import json

logger = get_logger("GPU-Worker")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--api_domain", type=str, required=False, default=API_DOMAIN)
    args.add_argument("--task_type", type=str, required=False, default="gpu")
    args = args.parse_args()
    uuid = uuid.uuid4()
    logger.info(f"GPU Worker UUID: {uuid}")
    api = API(
        domain=args.api_domain,
        token=args.token,
        uuid=str(uuid),
        task_type=args.task_type,
    )
    api.register_or_update_worker()
    available_models = api.get_available_models()
    logger.info(available_models)

    avail_model_objs = {
        model["model_name"]: LLMModelConfig(**model) for model in available_models
    }
    avail_ml_model_objs = {
        ml_model_name: MLModelConfig(model_name=ml_model_name)
        for ml_model_name in NORMAL_MODELS
    }
    logger.info("Init process complete. Waiting for tasks...")

    counter = 0
    while True:
        counter += 1
        if counter % 50 == 0:
            logger.info(f"Still alive. Counter: {counter}")
            api.register_or_update_worker()
        try:
            with timer(logger=logger, message="get_task"):
                task = api.get_task()
            if task is None:
                # No task available
                time.sleep(0.25)
                continue

            # we want to control it also run a normal model task
            model_name = task["parameters"].get("model_name", None)
            logger.info(f"Model Name: {model_name}")
            if model_name in NORMAL_MODELS:
                logger.info(f"Running ML Model Task {model_name}")
                # get the ml model ready
                start_time = time.time()
                ml_task_id = task["id"]
                logger.info(f"Running ML Model Task {ml_task_id}")
                ml_model = avail_ml_model_objs.get(model_name, None)
                logger.debug(ml_model)
                ml_model.model_ready()
                ml_input = task["parameters"].get("prompt", "")
                logger.debug(ml_input)
                result = ml_model.run_model(ml_input)
                logger.debug(result)
                end_time = time.time()
                try:
                    api.post_task_result(
                        task_id=ml_task_id,
                        result_status="completed",
                        description=str(result) if str(result) else "Error",
                        completed_in_seconds=end_time - start_time,
                        result={"embedding": result},
                    )
                except Exception as e:
                    logger.exception(e)
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
                    # dump the json to string
                    result = json.dumps(result)
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
