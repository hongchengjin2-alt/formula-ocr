"""Formula OCR engine abstraction layer."""

from abc import ABC, abstractmethod
import os
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageFilter, ImageOps

from core.converter import normalize_latex
from core.paths import resource_path


DEFAULT_ENGINE = "unimernet"


class FormulaRecognizer(ABC):
    """Abstract base class for formula recognition engines."""

    @abstractmethod
    def recognize(self, image: Image.Image) -> str:
        """Recognize formula from image and return a LaTeX string."""
        ...

    @staticmethod
    def preprocess(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy."""
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        img = ImageOps.grayscale(image)

        width, height = img.size
        if height < 64:
            scale = 64 / height
            img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)

        img = img.filter(ImageFilter.SHARPEN)
        return ImageOps.expand(img, border=10, fill=255)


class Pix2TexRecognizer(FormulaRecognizer):
    """Formula recognizer using Pix2Tex (LaTeX-OCR)."""

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            from pix2tex.cli import LatexOCR

            self._model = LatexOCR()

    def recognize(self, image: Image.Image) -> str:
        self._load_model()
        processed = self.preprocess(image)
        latex = self._model(processed)
        return normalize_latex(latex)


class UniMERNetRecognizer(FormulaRecognizer):
    """Formula recognizer using UniMERNet when installed and configured.

    Expected files:
    - configs/demo.yaml from the UniMERNet project
    - the model checkpoint referenced by that config
    """

    def __init__(self, config_path: str | Path = resource_path("configs", "unimernet_tiny.yaml")):
        self._config_path = Path(config_path)
        self._model = None
        self._vis_processor = None

    def _load_model(self):
        if self._model is not None:
            return

        if not self._config_path.exists():
            raise RuntimeError(
                f"UniMERNet is selected, but {self._config_path} was not found. "
                "Install UniMERNet, download a checkpoint, and create the config file, "
                "or use the Pix2Tex engine."
            )

        try:
            from unimernet.common.config import Config
            from unimernet.common.registry import registry
            from unimernet.processors import load_processor
            from unimernet.tasks import setup_task
        except ImportError as exc:
            raise RuntimeError(
                "UniMERNet is selected, but the unimernet package is not installed. "
                "Install it following the UniMERNet project instructions, or use Pix2Tex."
            ) from exc

        cache_dir = Path(os.environ.get("TRANSFORMERS_CACHE", resource_path("models", ".hf_cache")))
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("TRANSFORMERS_CACHE", str(cache_dir.resolve()))
        os.environ.setdefault("HF_HOME", str(cache_dir.resolve()))

        args = SimpleNamespace(cfg_path=str(self._config_path), options=None)
        cfg = Config(args)
        task = setup_task(cfg)
        model = task.build_model(cfg)

        vis_processor_cfg = cfg.config.model.preprocess.vis_processor.eval
        self._vis_processor = load_processor(
            vis_processor_cfg.name,
            cfg=vis_processor_cfg,
        )

        device = getattr(model, "device", None)
        if device is None:
            import torch

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)

        model.eval()
        self._model = model

    def recognize(self, image: Image.Image) -> str:
        self._load_model()
        processed = self.preprocess(image).convert("RGB")
        tensor = self._vis_processor(processed).unsqueeze(0)

        device = getattr(self._model, "device", None)
        if device is not None:
            tensor = tensor.to(device)

        output = self._model.generate({"image": tensor})
        if isinstance(output, dict):
            output = output.get("pred_str", output.get("pred_tokens", ""))
        if isinstance(output, (list, tuple)):
            output = output[0]
        return normalize_latex(str(output))


def available_engines() -> list[str]:
    """Return supported recognizer engine names."""
    return ["unimernet", "pix2tex"]


def get_recognizer(engine: str = DEFAULT_ENGINE) -> FormulaRecognizer:
    """Factory function to get a recognizer instance."""
    engines = {
        "pix2tex": Pix2TexRecognizer,
        "unimernet": UniMERNetRecognizer,
    }
    if engine not in engines:
        raise ValueError(f"Unknown engine '{engine}'. Available: {list(engines)}")
    return engines[engine]()
