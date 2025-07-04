from vlmeval.smp import *
from vlmeval.api.base import BaseAPI

headers = 'Content-Type: application/json'


class GeminiWrapper(BaseAPI):

    is_api: bool = True

    def __init__(self,
                 model: str = 'gemini-1.0-pro',
                 retry: int = 5,
                 wait: int = 5,
                 key: str = None,
                 verbose: bool = True,
                 temperature: float = 0.0,
                 system_prompt: str = None,
                 max_tokens: int = 2048,
                 proxy: str = None,
                 backend='genai',
                 project_id='vlmeval',
                 thinking_budget: int = None,  # range from 0 to 24576
                 # see https://ai.google.dev/gemini-api/docs/thinking
                 **kwargs):

        self.model = model
        self.fail_msg = 'Failed to obtain answer via API. '
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.thinking_budget = thinking_budget
        if key is None:
            key = os.environ.get('GOOGLE_API_KEY', None)
        # Try to load backend from environment variable
        be = os.environ.get('GOOGLE_API_BACKEND', None)
        if be is not None and be in ['genai', 'vertex']:
            backend = be

        assert backend in ['genai', 'vertex']
        if backend == 'genai':
            # We have not evaluated Gemini-1.5 w. GenAI backend
            assert key is not None  # Vertex does not require API Key
            try:
                from google import genai
            except ImportError as e:
                raise ImportError(
                    "Could not import 'google.genai'. Please install it with:\n"
                    "    pip install --upgrade google-genai"
                ) from e
            self.genai = genai
            self.client = genai.Client(api_key=key)

        self.backend = backend
        self.project_id = project_id
        self.api_key = key

        if proxy is not None:
            proxy_set(proxy)
        super().__init__(wait=wait, retry=retry, system_prompt=system_prompt, verbose=verbose, **kwargs)

    def build_msgs_genai(self, inputs):
        messages = [] if self.system_prompt is None else [self.system_prompt]
        for inp in inputs:
            if inp['type'] == 'text':
                messages.append(inp['value'])
            elif inp['type'] == 'image':
                messages.append(Image.open(inp['value']))
        return messages

    def build_msgs_vertex(self, inputs):
        from vertexai.generative_models import Part, Image
        messages = [] if self.system_prompt is None else [self.system_prompt]
        for inp in inputs:
            if inp['type'] == 'text':
                messages.append(inp['value'])
            elif inp['type'] == 'image':
                messages.append(Part.from_image(Image.load_from_file(inp['value'])))
        return messages

    def generate_inner(self, inputs, **kwargs) -> str:
        if self.backend == 'genai':
            from google.genai import types
            assert isinstance(inputs, list)
            model = self.model
            messages = self.build_msgs_genai(inputs)

            # Configure generation parameters
            config_args = {
                "temperature": self.temperature,
                "max_output_tokens": get_effective_max_tokens(self.max_tokens)
            }

            # If thinking_budget is specified, add thinking_config
            # By default, Gemini 2.5 Pro will automatically select
            # a thinking budget not exceeding 8192 if not specified.
            if self.thinking_budget is not None:
                config_args["thinking_config"] = types.ThinkingConfig(
                    thinking_budget=self.thinking_budget
                )
            config_args.update(kwargs)

            try:
                resp = self.client.models.generate_content(
                    model=model,
                    contents=messages,
                    config=types.GenerateContentConfig(**config_args)
                )
                answer = resp.text
                return 0, answer, 'Succeeded! '
            except Exception as err:
                if self.verbose:
                    self.logger.error(f'{type(err)}: {err}')
                    self.logger.error(f'The input messages are {inputs}.')

                return -1, '', ''
        elif self.backend == 'vertex':
            import vertexai
            from vertexai.generative_models import GenerativeModel
            vertexai.init(project=self.project_id, location='us-central1')
            model_name = 'gemini-1.0-pro-vision' if self.model == 'gemini-1.0-pro' else self.model
            model = GenerativeModel(model_name=model_name)
            messages = self.build_msgs_vertex(inputs)
            try:
                resp = model.generate_content(messages)
                answer = resp.text
                return 0, answer, 'Succeeded! '
            except Exception as err:
                if self.verbose:
                    self.logger.error(f'{type(err)}: {err}')
                    self.logger.error(f'The input messages are {inputs}.')

                return -1, '', ''


class Gemini(GeminiWrapper):

    def generate(self, message, dataset=None):
        return super(Gemini, self).generate(message)
