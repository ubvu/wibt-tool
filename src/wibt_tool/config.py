import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv


@dataclass(frozen=True)
class ModelSettings:
    """
    Groups a model name with its temperature.
    Using frozen=True makes this object immutable.
    """
    name: str
    temperature: float


@dataclass(frozen=True)
class AppConfig:
    """
    The master configuration object for the application.
    Contains API credentials, prompt directory structures, and all agent settings.
    """
    # API Connection Settings
    api_token: str
    api_url: str

    # Prompt Directory Configuration
    prompt_root: Path
    summary_dir: str
    translation_dir: str
    factuality_dir: str
    default_context: str

    # Agent Model Settings
    summary: ModelSettings
    refinement: ModelSettings
    read_eval: ModelSettings
    pre_draft: ModelSettings
    draft: ModelSettings
    refine_draft: ModelSettings
    proofread: ModelSettings
    translation_direct: ModelSettings
    fact_extractor: ModelSettings
    fact_alignment: ModelSettings
    advocate: ModelSettings
    skeptic: ModelSettings
    adjudicator: ModelSettings
    
    # List of settings for multiple validators
    fact_validators: List[ModelSettings] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict) -> "AppConfig":
        """
        Creates an AppConfig instance from a dictionary.
        Useful for WASM/Notebook environments where environment variables are not available.
        """
        def get_model_settings(prefix: str) -> ModelSettings:
            name = config_dict.get(f"{prefix.upper()}_MODEL")
            if not name:
                raise ValueError(f"Missing configuration key: {prefix.upper()}_MODEL")
            temp = float(config_dict.get(f"{prefix.upper()}_MODEL_TEMP", 0.0))
            return ModelSettings(name=name, temperature=temp)

        # 1. API Settings
        token = config_dict.get("api_token")
        url = config_dict.get("api_url")
        if not token or not url:
            raise ValueError("api_token and api_url must be provided in config_dict")

        # 2. Prompt Path Settings
        prompt_root = config_dict.get("prompt_root", Path("prompts"))
        if isinstance(prompt_root, str):
            prompt_root = Path(prompt_root)
        
        summary_dir = config_dict.get("summary_dir", "summary")
        translation_dir = config_dict.get("translation_dir", "translation")
        factuality_dir = config_dict.get("factuality_dir", "factuality_evaluation")
        default_context = config_dict.get("default_context", "general")

        # 3. Validator List Settings
        validators = []
        val_models = config_dict.get("fact_validators_models", [])
        val_temps = config_dict.get("fact_validators_temps", [])
        if len(val_models) == len(val_temps):
            for m, t in zip(val_models, val_temps):
                validators.append(ModelSettings(name=m, temperature=float(t)))
        elif len(val_models) > 0:
            raise ValueError("Mismatch between number of validation models and temperatures.")

        # 4. Assemble
        return cls(
            api_token=token,
            api_url=url,
            prompt_root=prompt_root,
            summary_dir=summary_dir,
            translation_dir=translation_dir,
            factuality_dir=factuality_dir,
            default_context=default_context,
            summary=get_model_settings("SUMMARY"),
            refinement=get_model_settings("REFINEMENT"),
            read_eval=get_model_settings("READ_EVAL"),
            pre_draft=get_model_settings("PREDRAFT"),
            draft=get_model_settings("DRAFT"),
            refine_draft=get_model_settings("REFINE_DRAFT"),
            proofread=get_model_settings("PROOFREAD"),
            translation_direct=get_model_settings("DIRECT_TRANSLATION"),
            fact_extractor=get_model_settings("FACT_EXTRACTION"),
            fact_alignment=get_model_settings("ALIGNMENT"),
            advocate=get_model_settings("ADVOCATE"),
            skeptic=get_model_settings("SKEPTIC"),
            adjudicator=get_model_settings("ADJUDICATOR"),
            fact_validators=validators
        )

    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        Factory method to create an AppConfig instance by reading 
        environment variables. This is the primary way to initialize the config.
        """
        def get_model_settings(prefix: str) -> ModelSettings:
            name = os.environ.get(f"DEFAULT_{prefix}_MODEL")
            temp_str = os.environ.get(f"DEFAULT_{prefix}_MODEL_TEMP", "0.0")
            if not name:
                raise ValueError(f"Missing environment variable: DEFAULT_{prefix}_MODEL")
            return ModelSettings(name=name, temperature=float(temp_str))

        load_dotenv() 
        token = os.environ.get("OPEN_AI_TOKEN")
        url = os.environ.get("OPEN_AI_URL")
        if not token or not url:
            raise ValueError("OPEN_AI_TOKEN and OPEN_AI_URL must be set in environment.")

        base_path = Path(os.environ.get("PROMPT_ROOT_DIR", "prompts"))
        summary_dir = "summary"
        translation_dir = "translation"
        factuality_dir = "factuality_evaluation"
        default_context = os.environ.get("DEFAULT_CONTEXT")
        if not default_context:
            raise ValueError("DEFAULT_CONTEXT must be set in environment.")

        validators = []
        val_models_str = os.environ.get("DEFAULT_FACT_VALIDATION_MODEL", "")
        val_temps_str = os.environ.get("DEFAULT_FACT_VALIDATION_MODEL_TEMP", "")
        if val_models_str:
            model_names = val_models_str.split(",")
            temp_values = val_temps_str.split(",")
            if len(model_names) != len(temp_values):
                raise ValueError("Mismatch between number of validation models and temperatures.")
            for m, t in zip(model_names, temp_values):
                validators.append(ModelSettings(name=m.strip(), temperature=float(t.strip())))

        return cls(
            api_token=token,
            api_url=url,
            prompt_root=base_path,
            summary_dir=summary_dir,
            translation_dir=translation_dir,
            factuality_dir=factuality_dir,
            default_context=default_context,
            summary=get_model_settings("SUMMARY"),
            refinement=get_model_settings("REFINEMENT"),
            read_eval=get_model_settings("READ_EVAL"),
            pre_draft=get_model_settings("PREDRAFT"),
            draft=get_model_settings("DRAFT"),
            refine_draft=get_model_settings("REFINE_DRAFT"),
            proofread=get_model_settings("PROOFREAD"),
            translation_direct=get_model_settings("DIRECT_TRANSLATION"),
            fact_extractor=get_model_settings("FACT_EXTRACTION"),
            fact_alignment=get_model_settings("ALIGNMENT"),
            advocate=get_model_settings("ADVOCATE"),
            skeptic=get_model_settings("SKEPTIC"),
            adjudicator=get_model_settings("ADJUDICATOR"),
            fact_validators=validators
        )
