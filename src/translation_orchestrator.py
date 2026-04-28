class TranslationOrchestrator:
    def __init__(self, factory, config):
        self.factory = factory
        self.config = config

    def run(self, summary: str, translation_ctx: str) -> str:
        """
        Takes a summary and produces a polished translation.
        """
        print(f"Starting translation pipeline using context: '{translation_ctx}'")
        
        # 1. Initialize Agents
        draft_agent = self.factory.create_translation_draft_agent(translation_ctx)
        proof_agent = self.factory.create_translation_proofread_agent(translation_ctx)
        translation_direct_agent = self.factory.create_translation_direct_agent(translation_ctx)

        # 2. Drafting & Internal Refinement
        print("Step 1: Drafting and refining translation...")
        example_translation = translation_direct_agent.translate(summary)
        print("Example translation created...")
        draft, refined_draft = draft_agent.write_refined_draft(summary, example_translation)

        # 3. Proofreading
        print("Step 2: Proofreading translation...")
        translation = proof_agent.proofread_draft(summary, draft, refined_draft)

        return translation
