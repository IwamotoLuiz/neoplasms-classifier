#!/usr/bin/env bash
# Sobe a demonstração neste PC e mantém um endereço fixo (gist secreto) com o link atual.
# Uso: ./iniciar.sh   (Ctrl+C encerra)
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORTA="${PORTA:-8010}"
INTERVALO="${INTERVALO:-20}"   # segundos entre verificações
PASSO="${PASSO:-1}"            # segundos entre tentativas enquanto algo inicia
ESPERA="${ESPERA:-60}"         # limite, em segundos, para a API e para o túnel iniciarem
ESTADO_DIR="${ESTADO_DIR:-$HOME/.local/share/tcc-demo}"
CLOUDFLARED="${CLOUDFLARED:-$(command -v cloudflared || echo "$HOME/.local/bin/cloudflared")}"
PLANO_B="https://boisterous-moxie-6297bc.netlify.app/"
NOME="tcc-demo"
LOCAL="http://127.0.0.1:$PORTA"

TUNEL_PID=""
TUNEL_URL=""
INIBIDOR_PID=""
GIST_PENDENTE=1
INICIADO=""

avisar() { echo "[$(date +%H:%M:%S)] $*"; }
falhar() { echo "Erro: $*" >&2; exit 1; }
vivo() { [ -n "$1" ] && kill -0 "$1" 2>/dev/null; }

# Um túnel travado pode ignorar o pedido de encerrar
matar() {
  vivo "$1" || return 0
  kill "$1" 2>/dev/null
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    vivo "$1" || break
    sleep 0.2 9>&-
  done
  kill -9 "$1" 2>/dev/null
  wait "$1" 2>/dev/null
}

# O sleep fica em segundo plano para que os sinais sejam atendidos na hora
dormir() { sleep "$1" 9>&- & wait $!; }

api_ok() { curl -sf -m 10 "$LOCAL/ping" 2>/dev/null | grep -q pong; }
# DNS sobre HTTPS: o DNS local guarda por um tempo a resposta de que o endereço novo não existe
link_ok() { curl -sf -m 15 --doh-url https://1.1.1.1/dns-query "$1/ping" 2>/dev/null | grep -q pong; }
internet_ok() { curl -sf -m 10 https://www.cloudflare.com/cdn-cgi/trace >/dev/null 2>&1; }

esperar() {
  local limite=$(( SECONDS + ESPERA ))
  until "$@"; do
    [ "$SECONDS" -lt "$limite" ] || return 1
    dormir "$PASSO"
  done
}

subir_api() {
  docker rm -f "$NOME" >/dev/null 2>&1
  docker run -d --name "$NOME" -p "127.0.0.1:$PORTA:8000" \
    --read-only --tmpfs /tmp:size=256m --cap-drop ALL --security-opt no-new-privileges \
    --memory 2g --pids-limit 256 "$NOME" >/dev/null && esperar api_ok
}

reiniciar_api() {
  if docker restart -t 5 "$NOME" >/dev/null 2>&1 && esperar api_ok; then return 0; fi
  subir_api
}

# Abre um túnel e só responde com sucesso depois que o link público funciona
abrir_tunel() {
  local log limite
  log="$(mktemp "$ESTADO_DIR/tunel.XXXXXX")"
  "$CLOUDFLARED" tunnel --no-autoupdate --url "$LOCAL" >"$log" 2>&1 9>&- &
  NOVO_PID=$!
  NOVA_URL=""
  limite=$(( SECONDS + ESPERA ))
  while vivo "$NOVO_PID" && [ "$SECONDS" -lt "$limite" ]; do
    # api.trycloudflare.com também aparece no log, mas não é o link
    NOVA_URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$log" | grep -v '//api\.' | head -1)"
    [ -n "$NOVA_URL" ] && link_ok "$NOVA_URL" && { rm -f "$log"; return 0; }
    dormir "$PASSO"
  done
  tail -5 "$log"
  matar "$NOVO_PID"
  rm -f "$log"
  return 1
}

trocar_tunel() {
  local antigo="$TUNEL_PID"
  abrir_tunel || return 1
  TUNEL_PID="$NOVO_PID"
  TUNEL_URL="$NOVA_URL"
  GIST_PENDENTE=1
  avisar "Link atual: $TUNEL_URL"
  matar "$antigo"
}

texto_gist() {
  echo "# Demonstração do TCC"
  echo
  if [ -n "$1" ]; then
    echo "## [Abrir a aplicação]($1)"
    echo
    echo "$1"
    echo
    echo "Se o link não abrir, espere um minuto e recarregue esta página."
  else
    echo "A demonstração não está no ar."
  fi
  echo
  echo "Plano B: $PLANO_B (a primeira resposta pode levar cerca de 10 minutos)"
  echo
  echo "Atualizado em $(date '+%d/%m/%Y às %H:%M:%S')."
}

criar_gist() {
  local endereco
  endereco="$(gh gist create -d "Demonstração do TCC" "$1" 2>/dev/null | grep -oE 'https://gist\.github\.com/[^ ]+' | head -1)"
  [ -n "$endereco" ] || return 1
  echo "$endereco" > "$ESTADO_DIR/gist"
}

publicar() {
  local arquivo="$ESTADO_DIR/demonstracao-tcc.md" endereco="" resposta
  texto_gist "$1" > "$arquivo"
  [ -s "$ESTADO_DIR/gist" ] && endereco="$(cat "$ESTADO_DIR/gist")"
  if [ -z "$endereco" ]; then
    criar_gist "$arquivo" || return 1
    avisar "Endereço fixo: $(cat "$ESTADO_DIR/gist")"
    return 0
  fi
  resposta="$(gh api --method PATCH "/gists/${endereco##*/}" --silent \
    -F "files[demonstracao-tcc.md][content]=@$arquivo" 2>&1)" && return 0
  # Só recria se o gist foi apagado; em qualquer outra falha, tenta de novo depois
  case "$resposta" in *"HTTP 404"*) ;; *) return 1 ;; esac
  [ -n "$1" ] || return 1
  criar_gist "$arquivo" || return 1
  avisar "ATENÇÃO: o gist anterior não existe mais e o endereço fixo mudou: $(cat "$ESTADO_DIR/gist")"
}

atualizar_gist() {
  [ -n "$GIST_PENDENTE" ] || return 0
  if publicar "$TUNEL_URL"; then
    GIST_PENDENTE=""
    avisar "Gist atualizado."
  else
    avisar "Não consegui atualizar o gist. Tento de novo em ${INTERVALO}s."
  fi
}

encerrar() {
  trap '' INT TERM HUP
  matar "$TUNEL_PID"
  matar "${NOVO_PID:-}"
  matar "$INIBIDOR_PID"
  if [ -n "$INICIADO" ]; then
    docker rm -f "$NOME" >/dev/null 2>&1
    # Sem gist criado não há o que marcar como encerrado
    [ -s "$ESTADO_DIR/gist" ] && publicar "" >/dev/null 2>&1
    rm -f "$ESTADO_DIR"/tunel.*
    echo "Demonstração encerrada." 2>/dev/null
  fi
}

vigiar() {
  local falhas_api=0 falhas_link=0 sem_internet=""
  while :; do
    dormir "$INTERVALO"

    if ! api_ok; then
      falhas_api=$(( falhas_api + 1 ))
      if [ "$falhas_api" -ge 2 ]; then
        avisar "API sem resposta. Reiniciando o contêiner."
        reiniciar_api && avisar "API de volta."
        falhas_api=0
      fi
      continue   # com a API fora, o link também falha e não diz nada sobre o túnel
    fi
    falhas_api=0

    if vivo "$TUNEL_PID" && link_ok "$TUNEL_URL"; then
      falhas_link=0
      [ -n "$sem_internet" ] && avisar "Internet de volta."
      sem_internet=""
    elif ! internet_ok; then
      falhas_link=0
      [ -z "$sem_internet" ] && avisar "Sem internet. Mantendo o link atual."
      sem_internet=1
      continue
    else
      falhas_link=$(( falhas_link + 1 ))
      if ! vivo "$TUNEL_PID" || [ "$falhas_link" -ge 3 ]; then
        avisar "Link sem resposta. Abrindo outro túnel."
        trocar_tunel || avisar "O novo túnel não abriu. Mantendo o atual e tentando de novo."
        falhas_link=0
      fi
    fi

    atualizar_gist
  done
}

mkdir -p "$ESTADO_DIR" && chmod 700 "$ESTADO_DIR" || falhar "não consegui criar $ESTADO_DIR"
for comando in docker gh curl flock systemd-inhibit; do
  command -v "$comando" >/dev/null || falhar "$comando não encontrado"
done
[ -x "$CLOUDFLARED" ] || falhar "cloudflared não encontrado em $CLOUDFLARED"
exec 9>"$ESTADO_DIR/lock"
flock -n 9 || falhar "a demonstração já está rodando em outra janela"

trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
trap encerrar EXIT
INICIADO=1

systemd-inhibit --what=sleep:idle --who="Demonstração do TCC" --why="Apresentação em andamento" \
  sleep infinity >/dev/null 2>&1 9>&- &
INIBIDOR_PID=$!

avisar "Preparando a imagem (a primeira vez leva alguns minutos)."
if ! docker build -q -f "$RAIZ/demo/Dockerfile" -t "$NOME" "$RAIZ" >"$ESTADO_DIR/build.log" 2>&1; then
  docker image inspect "$NOME" >/dev/null 2>&1 || { tail -20 "$ESTADO_DIR/build.log"; falhar "a imagem não foi construída"; }
  avisar "A imagem não foi reconstruída. Usando a anterior."
fi

avisar "Iniciando a API."
subir_api || falhar "a API não respondeu em ${ESPERA}s"
avisar "Abrindo o túnel."
trocar_tunel || falhar "o túnel não abriu em ${ESPERA}s"
atualizar_gist

echo
[ -s "$ESTADO_DIR/gist" ] && echo "  Endereço fixo (Canva):  $(cat "$ESTADO_DIR/gist")"
echo "  Link atual:             $TUNEL_URL"
echo "  Neste PC:               $LOCAL"
echo
echo "  Deixe esta janela aberta. Ctrl+C encerra."
echo
vigiar
