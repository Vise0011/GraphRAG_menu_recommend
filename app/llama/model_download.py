from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    local_dir="/root/16_team/app/llama/Llama-3.1-8B-Instruct",
    local_dir_use_symlinks=False
)
