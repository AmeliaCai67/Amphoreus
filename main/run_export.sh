#!/bin/bash
# 切换到脚本所在目录（main目录）
cd "$(dirname "$0")"

# 激活conda环境
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate Amphoreus

# 运行Python脚本 - 添加 -u 参数禁用输出缓冲
python -u data_export.py "$@"
