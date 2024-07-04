from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import CLUSTER_Q_ETE_CONVERSATION_NAME

logger = get_logger(__name__)


class AccuracyBenchmark:
    def __init__(self, benchmark_cluster: str = CLUSTER_Q_ETE_CONVERSATION_NAME):
        """
        Initialize the benchmark
        Args:
            benchmark_cluster (str): The benchmark cluster
        """
        # if it is a specific name, gather this metric, otherwise, report all existing cluster
        self.benchmark_cluster = benchmark_cluster

    def run(self):
        """
        Run the benchmark
        """
        logger.info(f"Running accuracy benchmark for cluster {self.benchmark_cluster}")
        # run the benchmark
        pass
