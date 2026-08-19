# Sonda di verifica — claude-opus-4-1 su Bedrock
Data: 2026-08-16T09:47:10   Account: <profilo-bedrock>   Regione: us-east-1

## Perche'
Il caso «disuso» del censimento (research/CENSIMENTO.md) citava Opus 4.1 con il suo
messaggio verbatim, ma nessun file sotto results/ conteneva una traccia della sonda:
l'affermazione viveva solo nel documento. Il censimento e' la parte del paper su cui
cade il peso probatorio, e una prova che non si puo' rieseguire non e' una prova.

## Comando
    aws bedrock-runtime converse --model-id us.anthropic.claude-opus-4-1-20250805-v1:0 \
        --messages [{"role":"user","content":[{"text":"hi"}]}] --inference-config {"maxTokens":1}

## Risposta, verbatim
    ResourceNotFoundException: Access denied. This Model is marked by provider as Legacy
    and you have not been actively using the model in the last 30 days. Please upgrade to
    an active model on Amazon Bedrock

## Nota sull'identificatore
Senza prefisso regionale (anthropic.claude-opus-4-1-...) la risposta e' diversa:
    ValidationException: Invocation of model ID ... with on-demand throughput isn't
    supported. Retry your request with the ID or ARN of an inference profile
Due messaggi diversi per lo stesso modello, a seconda di come lo si nomina: chi cerca il
modello con la forma sbagliata conclude che non esista, ed e' un settimo modo in cui un
endpoint fa sparire un modello da un campione — non per rifiuto, ma per identificatore.
