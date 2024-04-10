from api import API
import argparse
from constants import API_DOMAIN, NORMAL_MODELS
from ml_models import MLModelConfig
from llm_task import LLMTask
from llm_adaptor_worker import LLMAdaptor
from utils import get_logger, timer
import time
import uuid
from llm_models import LLMModelConfig

logger = get_logger("Ghat-Worker")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--api_domain", type=str, required=False, default=API_DOMAIN)
    args.add_argument("--task_type", type=str, required=False, default="gpu")
    args = args.parse_args()
    uuid = uuid.uuid4()
    logger.info(f"Chat Worker UUID: {uuid}")

    api = API(
        domain=args.api_domain,
        token=args.token,
        uuid=str(uuid),
        task_type=args.task_type,
    )
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

    while True:
        try:
            with timer(logger=logger, message="get_chat_task"):
                task = api.get_chat()
            if task is None:
                # get summary task
                with timer(logger=logger, message="get_summary_task"):
                    task = api.get_chat_summary()

                if task is None:
                    # No task available
                    time.sleep(0.25)
                    continue
            prompt = task.get("prompt", None)
            messages = task.get("messages", None)
            llm_model_name = task.get("llm_model_name", None)
            logger.info(f"Model Name: {llm_model_name}")
            llm_model = avail_model_objs.get(llm_model_name, None)
            if llm_model is None:
                logger.error(f"Model {llm_model_name} not found")
                continue
            if llm_model.llm is None:
                logger.error(f"Model {llm_model_name} not loaded")
                llm_model.init_llm()

            with timer(logger=logger, message="run_chat_task"):
                llm_adaptor = LLMAdaptor(llm_model)
                # if prompt is not None, then we are responding
                res = llm_adaptor.create_chat_completion(prompt=prompt, messages=messages)
                logger.info(res)
                if prompt is not None:
                    api.post_chat_summary(
                        chat_uuid=task["uuid"],
                        summary=res["choices"][0]["message"]["content"],
                    )
                if messages is not None:
                    api.post_chat(
                        chat_uuid=task["uuid"],
                        message=res["choices"][0]["message"]["content"],
                    )
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            time.sleep(0.25)
            continue
