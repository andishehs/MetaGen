import json
import autogen
from autogen.agentchat.contrib.agent_builder import AgentBuilder


def run_orchestra_auto(name, message, llm_config, config_list, config_file_or_env, build_json_file):
    """Simulates running an orchestra using the provided JSON configuration file and autogen."""
    try:
        # Read the JSON configuration file
        with open(build_json_file, "r") as json_file:
            build_config = json.load(json_file)

        print(f"RunOrchestraAuto: Starting the orchestra '{name}'.")
        print(f"RunOrchestraAuto: Using configuration:")
        print(json.dumps(build_config, indent=2))

        def start_task(execution_task: str, agent_list: list, coding=True):
            group_chat = autogen.GroupChat(
                agents=agent_list,
                messages=[],
                max_round=12,
                allow_repeat_speaker=agent_list[:-1] if coding else agent_list,
            )
            manager = autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config={"config_list": config_list, **llm_config},
            )
            agent_list[0].initiate_chat(manager, message=execution_task)

        # Initialize AgentBuilder and load agents
        new_builder = AgentBuilder(config_file_or_env=config_file_or_env)
        agent_list, agent_configs = new_builder.load(build_json_file)

        # Example task execution
        start_task(
            #execution_task="Find a recent paper about LLaVA on arxiv and find its potential applications in computer vision.",
            execution_task=message,
            agent_list=agent_list,
        )

        # Clean up agents
        new_builder.clear_all_agents()
        print(f"RunOrchestraAuto: The orchestra '{name}' is now running successfully with autogen!")

        return True

    except FileNotFoundError:
        print(f"RunOrchestraAuto: Configuration file '{build_json_file}' not found.")
        return False
    except json.JSONDecodeError:
        print(f"RunOrchestraAuto: Configuration file '{build_json_file}' contains invalid JSON.")
        return False
    except Exception as e:
        print(f"RunOrchestraAuto: An unexpected error occurred: {e}")
        return False

