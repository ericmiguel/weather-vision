"""PydanticAI agent construction and execution for image analysis."""

from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai import ImageUrl
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.models.openrouter import OpenRouterProvider

from wv.config import Settings
from wv.image import encode_image
from wv.schemas import Confidence
from wv.schemas import EventKind
from wv.schemas import ExtremeWeatherAnalysis
from wv.schemas import MapType
from wv.schemas import Severity

event_kind_values = " | ".join(item.value for item in EventKind)
severity_values = " | ".join(item.value for item in Severity)
confidence_values = " | ".join(item.value for item in Confidence)
map_type_values = " | ".join(item.value for item in MapType)

_SYSTEM_PROMPT = (
    "You are a senior meteorologist analyzing a weather-related image such as "
    "satellite imagery, radar, synoptic chart, or similar. "
    "Respond exclusively in English. "
    "Mandatory tasks:\n"
    f"1. Identify the map/image type in map_type ({map_type_values}).\n"
    "2. Indicate the geographic region covered in region_covered.\n"
    "3. List visible extreme weather events. For each event provide "
    f"kind ({event_kind_values}), severity ({severity_values}), region "
    "(affected region) and evidence (visual elements supporting the identification, "
    "e.g. 'band of cold cloud tops in IR channel', 'intense radar echo', etc.). "
    "If no extreme event is identifiable, return an empty list.\n"
    "4. Write an executive summary of 1-2 sentences.\n"
    f"5. Assign confidence ({confidence_values}) "
    f"according to image clarity/quality.\n"
    "6. List in caveats limitations of the visual analysis (e.g. 'grayscale image "
    "without RGB composition', 'no surface data', 'limited spatial resolution')."
)

_USER_PROMPT = (
    "Analyze the attached image and produce the JSON structure according to "
    "the schema. "
    "Do not invent data that is not visually observable; when in doubt, "
    "use confidence=low and record the uncertainty in caveats."
)


def _build_agent() -> Agent[None, ExtremeWeatherAnalysis]:
    """Build and return a PydanticAI Agent configured with OpenRouter.

    The agent is configured with the model defined in ``Settings.model_name``
    (via the MODEL_NAME environment variable) and the OpenRouter API key
    read from ``Settings.openrouter_api_key``.

    Returns
    -------
    Agent[None, ExtremeWeatherAnalysis]
        Agent ready to run ``run_sync`` with an image and return
        a validated ``ExtremeWeatherAnalysis`` instance.
    """
    settings = Settings()
    provider = OpenRouterProvider(api_key=settings.openrouter_api_key)
    model = OpenRouterModel(settings.model_name, provider=provider)
    return Agent(
        model,
        output_type=ExtremeWeatherAnalysis,
        system_prompt=_SYSTEM_PROMPT,
    )


def analyze_image(path: Path) -> ExtremeWeatherAnalysis:
    """Read an image from disk, encode it as a Data URI, and run weather analysis.

    Parameters
    ----------
    path : Path
        Filesystem path pointing to an image in ``.png``, ``.jpg`` or ``.jpeg`` format.

    Returns
    -------
    ExtremeWeatherAnalysis
        Validated Pydantic object containing the map type, covered
        region, list of identified extreme events, summary,
        confidence level, and analysis limitations.
    """
    data_uri = encode_image(path)
    agent = _build_agent()
    result = agent.run_sync([_USER_PROMPT, ImageUrl(url=data_uri)])
    return result.output
