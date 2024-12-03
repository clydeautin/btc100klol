from .utils import PromptType

SYSTEM_MESSAGES = {
    PromptType.GET_HOLIDAYS: "You are an expert on international holidays, commemorations, and funny celebrations.",
}


def get_system_message(prompt_type: PromptType) -> str:
    return SYSTEM_MESSAGES[prompt_type]


PROMPTS = {
    PromptType.GET_HOLIDAYS: lambda date: (
        f"List all international commemorations, including national holidays, observances, "
        f"awareness days, and unofficial and obscure celebrations recognized globally on {date}. "
        "Each item should be a plain-text description in the following format: "
        "'[Holiday Name] - [Brief Description]'. "
        "Do not include categories, preambles, or additional comments. "
        "Return only the list of holidays with descriptions in the specified format."
    ),
}


def get_prompt(prompt_type: PromptType, param: str) -> str:
    return PROMPTS[prompt_type](param)
