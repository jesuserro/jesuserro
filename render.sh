#!/usr/bin/env bash
set -euo pipefail

set -a
source <(sops --decrypt --input-type dotenv --output-type dotenv .env.enc)
set +a

envsubst < cv/Jesus_Erro_CV.template.yaml > cv/Jesus_Erro_CV.yaml
rendercv render cv/Jesus_Erro_CV.yaml
