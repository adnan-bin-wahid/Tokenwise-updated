# Third-Party Notices

TokenWise's own source is MIT licensed; see the root LICENSE. Bundled backend
source retains its upstream license at backend-bundle/swe-pruner/swe-pruner/LICENSE.

## SWE-Pruner and Model Assets

- Source: https://github.com/Ayanami1314/swe-pruner
- Model and model card: https://huggingface.co/ayanami-kitasan/code-pruner
- Model card license: MIT.
- Pinned revision: 863cee3198c715c9df1faa422a3490e0832bb734.
- Weight SHA-256: 373b77f5262c3298b803303d49ea38949d3e92f08dc3bbb90b03f490413adae9.

The extension bundles configuration/tokenizer files and the upstream model card,
not the 1.35 GB weight. Setup downloads that weight with the user's approval.
The model is derived from Qwen/Qwen3-Reranker-0.6B; its upstream information is
available at https://huggingface.co/Qwen/Qwen3-Reranker-0.6B.

## Runtime Dependencies

PyTorch, Transformers, FastAPI, Hugging Face Hub, NumPy, pandas, scikit-learn,
XGBoost, and other Python dependencies are installed from their package
distributions and retain their respective licenses. Their distribution license
files remain in the managed virtual environment. gpt-tokenizer is distributed
under MIT and its license remains in the extension's node_modules.

jsonc-parser 3.3.1, copyright Microsoft, is MIT licensed. TokenWise uses it to
preserve unrelated JSONC settings and comments during cleanup. Its upstream
license remains at node_modules/jsonc-parser/LICENSE.md in the extension.

## Research Material

The included papers are reference material subject to their authors' and
distributors' terms. They are not included in the end-user VSIX. TokenWise's
carbon artifacts are locally trained and SEAL-derived, not a claim of exact
reproduction or measurement of a user's cloud-model energy consumption.
