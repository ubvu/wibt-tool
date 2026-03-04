from . import Agent
from models import Judgement
from utils import get_numbered_sentences



class AdjudicatorAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def judge(self, paper, summary, advocate_arguments, skeptic_arguments):
        self.clear_messages()
        
        split_paper = get_numbered_sentences(paper)
        numbered_paper = '\n'.join(split_paper)

        split_summary = get_numbered_sentences(summary)
        numbered_summary = '\n'.join(split_summary)
        number_of_summary_lines = len(split_summary)

        formatted_arguments = self._format_arguments(advocate_arguments, skeptic_arguments)

        judgements = self.send_messages_structured(
            [
                f"Paper:\n\n{numbered_paper}", 
                f"Summary:\n\n{numbered_summary}", 
                f"Arguments:\n\n{formatted_arguments}"
            ], Judgement, 
            number=number_of_summary_lines
        )

        return judgements

    def _format_arguments(self, advocate_arguments, skeptic_arguments):
        merged_lines = []

        for i in range(1, len(advocate_arguments) + 1):
            # faithful : bool
            # error_type : str
            # reference_sentences : List[int]
            # reason : str
            merged_lines.append(f"{i}:")            
            advocate_argument = advocate_arguments[str(i)]
            merged_lines.append("- Advocate:")
            merged_lines.append(f"-- Faithful: {advocate_argument['faithful']}")
            merged_lines.append(f"-- Error type: {advocate_argument['error_type']}")
            merged_lines.append(f"-- Reference sentences: {advocate_argument['reference_sentences']}")
            merged_lines.append(f"-- Reason: {advocate_argument['reason']}")

            skeptic_argument = skeptic_arguments[str(i)]
            merged_lines.append("- Skeptic:")
            merged_lines.append(f"-- Faithful: {skeptic_argument['faithful']}")
            merged_lines.append(f"-- Error type: {skeptic_argument['error_type']}")
            merged_lines.append(f"-- Reference sentences: {skeptic_argument['reference_sentences']}")
            merged_lines.append(f"-- Reason: {skeptic_argument['reason']}")

            merged_lines.append('\n')
        return '\n'.join(merged_lines)