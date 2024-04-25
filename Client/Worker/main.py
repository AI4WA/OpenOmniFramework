import argparse
import json
import time
import uuid

from api import API
from constants import API_DOMAIN, NORMAL_MODELS
from llm_adaptor_worker import LLMAdaptor
from llm_models import LLMModelConfig
from llm_task import LLMTask
from ml_models import MLModelConfig
from utils import get_logger, timer

logger = get_logger("GPU-Worker")

AVAIL_MODEL_OBJS = {}

AVAIL_ML_MODEL_OBJS = {}


def work_manager(api: API):
    """
    Manage it to be, if there is a Chat to be handled, it will be handled first
    Otherwise, it will be handled as a normal task
    Args:
        api:

    Returns:
    """
    with timer(logger=logger, message="get_chat"):
        chat = api.get_chat()
        if chat:
            return chat, "chat"
    with timer(logger=logger, message="get_summary_task"):
        chat_summary = api.get_chat_summary()
        if chat_summary:
            return chat_summary, "chat"
    with timer(logger=logger, message="get_task"):
        task = api.get_task()
        return task, "task"


def handle_task(task: dict, api: API):
    # we want to control it also run a normal model task
    model_name = task["parameters"].get("model_name", None)
    logger.info(f"Model Name: {model_name}")
    """
    This is handling the normal ML model task like bert, etc
    """
    if model_name in NORMAL_MODELS:
        logger.info(f"Running ML Model Task {model_name}")
        # get the ml model ready
        start_time = time.time()
        ml_task_id = task["id"]
        logger.info(f"Running ML Model Task {ml_task_id}")
        ml_model = AVAIL_ML_MODEL_OBJS.get(model_name, None)
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
        except Exception as ml_err:
            logger.exception(ml_err)
        return

    """
    This is to handle llm task
    """
    llm_task = LLMTask(**task)
    llm_model = AVAIL_MODEL_OBJS.get(llm_task.llm_model_name, None)
    if llm_model is None:
        logger.error(f"LLM Model {llm_task.llm_model_name} not exist")
        api.post_task_result(
            task_id=llm_task.task_id,
            result_status="failed",
            description="LLM Model not exist",
            completed_in_seconds=0,
        )
        return

    # confirm model exists
    if llm_model.llm is None:
        # we will hold the model in memory, this potentially can cause error
        try:
            llm_model.init_llm()
        except Exception as llm_err:
            logger.exception(llm_err)
            # release all other llm models
            for avail_model_obj in AVAIL_MODEL_OBJS.values():
                if (avail_model_obj.llm is not None) and (
                    avail_model_obj.model_name != llm_model.model_name
                ):
                    del avail_model_obj.llm
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
        except Exception as llm_err:
            logger.exception(llm_err)
            result = str(llm_err)
            result_status = "failed"
        end_time = time.time()

        # post task result
        logger.info(f"Task {llm_task.task_id} completed")
        try:
            api.post_task_result(
                task_id=llm_task.task_id,
                result_status=result_status,
                description=str(result) if result else "Error",
                completed_in_seconds=end_time - start_time,
                result=result,
            )
        except Exception as report_llm_err:
            logger.exception(report_llm_err)


def handle_chat(task: dict, api: API):
    """
    Handle chat task
    Args:
        task:
        api:

    Returns:

    """
    prompt = task.get("prompt", None)
    messages = task.get("messages", None)
    llm_model_name = task.get("llm_model_name", None)
    logger.info(f"Model Name: {llm_model_name}")
    logger.info(f"Task UUID: {task['uuid']}")
    llm_model = AVAIL_MODEL_OBJS.get(llm_model_name, None)
    if llm_model is None:
        logger.error(f"Model {llm_model_name} not found")
        return
    if llm_model.llm is None:
        logger.error(f"Model {llm_model_name} not loaded")
        try:
            llm_model.init_llm()
        except Exception as llm_err:
            logger.exception(llm_err)
            # release all other llm models
            for avail_model_obj in AVAIL_MODEL_OBJS.values():
                if (avail_model_obj.llm is not None) and (
                    avail_model_obj.model_name != llm_model.model_name
                ):
                    del avail_model_obj.llm
            llm_model.init_llm()

    with timer(logger=logger, message="run_chat_task"):
        llm_adaptor = LLMAdaptor(llm_model)
        # if prompt is not None, then we are responding
        res = llm_adaptor.create_chat_completion(
            prompt=prompt, messages=messages, handle_chat=True
        )
        logger.info(res)
        if prompt is not None:
            api.post_chat_summary(
                chat_uuid=task["uuid"],
                summary=res,
            )
        if messages is not None:
            api.post_chat(
                chat_uuid=task["uuid"],
                message=res,
            )


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--api_domain", type=str, required=False, default=API_DOMAIN)
    args.add_argument("--task_type", type=str, required=False, default="gpu")
    args = args.parse_args()
    uuid = uuid.uuid4()
    logger.info(f"GPU Worker UUID: {uuid}")
    shared_api = API(
        domain=args.api_domain,
        token=args.token,
        uuid=str(uuid),
        task_type=args.task_type,
    )
    shared_api.register_or_update_worker()
    available_models = shared_api.get_available_models()
    logger.info(available_models)

    for model in available_models:
        AVAIL_MODEL_OBJS[model["model_name"]] = LLMModelConfig(**model)

    for ml_model_name in NORMAL_MODELS:
        AVAIL_ML_MODEL_OBJS[ml_model_name] = MLModelConfig(model_name=ml_model_name)

    logger.info("Init process complete. Waiting for tasks...")

    counter = 0
    while True:
        counter += 1
        if counter % 50 == 0:
            logger.info(f"Still alive. Counter: {counter}")
            shared_api.register_or_update_worker()
        try:
            with timer(logger=logger, message="get_task"):
                current_work, current_work_type = work_manager(shared_api)
            if current_work is None:
                # No task available
                time.sleep(0.25)
                continue
            if current_work_type == "chat":
                # handle chat task
                handle_chat(current_work, shared_api)
            if current_work_type == "task":
                # handle task
                handle_task(current_work, shared_api)

        except Exception as e:
            logger.exception(e)

        time.sleep(1.5)
