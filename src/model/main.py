import time
import schedule
from utils.config import get_configs
from blackboard.blackboard import Blackboard
from controller.controller import Controller
from utils.config import LOGGER
from src.model.knowledge_sources.read import CleanPhase2
from knowledge_sources.compute_phases import ComputePhases
from knowledge_sources.drop_invalid_cycles import DropInvalidCycles
from knowledge_sources.input_cycles import InputCycles
from knowledge_sources.interpret_day import InterpretDay
from knowledge_sources.output_kafka import OutputKafka
from knowledge_sources.export_sql import ExportSQL
from knowledge_sources.refresh_blackboard import RefreshBlackboard
from knowledge_sources.retrain_if_needed import RetrainIfNeeded
from knowledge_sources.train_if_needed import TrainIfNeeded
from knowledge_sources.look_for_existing_model import LookForExistingModel

def main():
    target_env = "prd" # (prd, qat, dev, local)

    # Initialize blackboard and controller
    blackboard = Blackboard()
    controller = Controller(blackboard)

    # Load configs
    blackboard.load_configurations(
        process = get_configs("config_p2_processing.yml", target_env),
        frame = get_configs("config_kafka_profile.yml", target_env)["frame"],
        sql = get_configs("config_kafka_profile.yml", target_env)["sql"],
        kafka = get_configs("config_kafka_profile.yml", target_env)["kafka"]
    )

    # Add knowledge sources
    blackboard.add_knowledge_source(LookForExistingModel(blackboard))
    blackboard.add_knowledge_source(InputCycles(blackboard))
    blackboard.add_knowledge_source(CleanPhase2(blackboard))
    blackboard.add_knowledge_source(TrainIfNeeded(blackboard))
    blackboard.add_knowledge_source(DropInvalidCycles(blackboard))
    blackboard.add_knowledge_source(ComputePhases(blackboard))
    blackboard.add_knowledge_source(InterpretDay(blackboard))
    blackboard.add_knowledge_source(RetrainIfNeeded(blackboard))
    blackboard.add_knowledge_source(OutputKafka(blackboard))
    blackboard.add_knowledge_source(ExportSQL(blackboard))
    blackboard.add_knowledge_source(RefreshBlackboard(blackboard))

    # Process once
    controller.run_knowledge_sources()

    # Schedule to do it each day
    result_time = blackboard.process_config["analysis_result"]
    LOGGER.info(f"Now processing analysis everyday at {result_time['hour']}:{result_time['minute']}")
    schedule.every().day.at(f"{result_time['hour']}:{result_time['minute']}").do(
        controller.run_knowledge_sources
    )

    while True:
        # Checks whether a scheduled task is pending to run or not
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()