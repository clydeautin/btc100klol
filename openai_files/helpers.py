from .utils import PromptType

SYSTEM_MESSAGES = {
    PromptType.GET_HOLIDAYS: "You are an expert on international holidays, commemorations, and funny celebrations.",
}


def get_system_message(prompt_type: PromptType) -> str:
    return SYSTEM_MESSAGES.get(prompt_type, "")




PROMPTS = {
    PromptType.GENERATE_IMAGE_HAPPY: lambda holiday_list, price=None: (
        f"Here is a list of holidays: {holiday_list}\n"
        "Please create an image that combines all these events with the context of a happy crypto "
        "investor as the subject."
    ),
    PromptType.GENERATE_IMAGE_SAD: lambda holiday_list, price=100000: (
        f"Here is a list of holidays: {holiday_list}\n"
        "Please create an image that combines all these events with the context of a sad crypto "
        "investor as the subject, but make it a little bit funny."
        + (
            " Make the scene a freezing cold 'crypto winter' with snow, ice, and a shivering investor."
            if price < 75000
            else ""
        )
    ),
    PromptType.GET_HOLIDAYS: lambda date, price=None: (
        "List all international commemorations, including national holidays, observances, "
        f"awareness days, and unofficial and obscure celebrations recognized globally on {date}. "
        "Each item should be a plain-text description in the following format: "
        "'[Holiday Name] - [Brief Description]'. "
        "Do not include categories, preambles, or additional comments. "
        "Return only the list of holidays with descriptions in the specified format. "
        "Please omit holidays or words that may trigger OpenAIs safety system when "
        "generating images. Opt to use family friendly synonyms instead of omitting if possible."
    ),
}


def get_prompt(prompt_type: PromptType, param: str, price: float = 100000) -> str:
    return PROMPTS[prompt_type](param, price=price)
