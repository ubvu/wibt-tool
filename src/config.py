import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
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
    summary_dir: Path
    translation_dir: Path
    factuality_dir: Path
    default_context: str

    # Agent Model Settings
    summary: ModelSettings
    refinement: ModelSettings
    read_eval: ModelSettings
    draft: ModelSettings
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
    def from_env(cls) -> "AppConfig":
        """
        Factory method to create an AppConfig instance by reading 
        environment variables. This is the primary way to initialize the config.
        """

        def get_model_settings(prefix: str) -> ModelSettings:
            """Helper to fetch model name and temperature based on a prefix."""
            name = os.environ.get(f"DEFAULT_{prefix}_MODEL")
            # Default temperature to 0.0 if not provided
            temp_str = os.environ.get(f"DEFAULT_{prefix}_MODEL_TEMP", "0.0")
            
            if not name:
                raise ValueError(f"Missing environment variable: DEFAULT_{prefix}_MODEL")
                
            return ModelSettings(name=name, temperature=float(temp_str))

        load_dotenv() 
        # 1. Handle API Settings
        token = os.environ.get("OPEN_AI_TOKEN")
        url = os.environ.get("OPEN_AI_URL")
        if not token or not url:
            raise ValueError("OPEN_AI_TOKEN and OPEN_AI_URL must be set in environment.")

        # 2. Handle Prompt Path Settings
        # Default to a folder named 'prompts' in the current working directory
        base_path = Path(os.environ.get("PROMPT_ROOT_DIR", "prompts"))
        
        summary_dir = base_path / "summary"
        translation_dir = base_path / "translation"
        factuality_dir = base_path / "factuality_evaluation"

        default_context = os.environ.get("DEFAULT_CONTEXT")
        if not default_context:
            raise ValueError("DEFAULT_CONTEXT must be set in environment.")

        # 3. Handle Validator List Settings
        # Expecting comma-separated strings: "model1,model2" and "0,1"
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

        # 4. Assemble and return the full Config object
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
            draft=get_model_settings("DRAFT"),
            proofread=get_model_settings("PROOFREAD"),
            translation_direct=get_model_settings("DIRECT_TRANSLATION"),
            fact_extractor=get_model_settings("FACT_EXTRACTION"),
            fact_alignment=get_model_settings("ALIGNMENT"),
            advocate=get_model_settings("ADVOCATE"),
            skeptic=get_model_settings("SKEPTIC"),
            adjudicator=get_model_settings("ADJUDICATOR"),
            fact_validators=validators
        )

# Example usage (for testing purposes only):
if __name__ == "__main__":
    # This allows you to run `python appconfig.py` to verify your .env is working
    try:
        config = AppConfig.from_env()
        print("✅ Configuration loaded successfully!")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
